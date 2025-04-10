#!/usr/bin/env python3
r"""
Scheduled Webcam Recording Script with Menu, Status, Stop/Resume,
Resolution Check, and Recording Warning

This script performs the following tasks:
  • Automatically records from the webcam every 15 minutes (each session lasting 60 seconds by default).
  • Provides an interactive text-based menu to:
      1. Trigger an immediate manual recording.
      2. View the log file.
      3. Show the current status.
      4. Toggle automatic scheduled recordings (i.e. stop or resume them).
      5. Exit the program.
      
All recordings and the log file are saved in:
    C:\Users\USER\Documents\Recordings

When the camera is recording, a warning window appears alerting you that recording is in progress.

Requirements:
    - Python 3.x
    - OpenCV (pip install opencv-python)
    - schedule (pip install schedule)
    - licensing_module (local)

Usage:
    Run this script (via a batch file or directly from a terminal).
    The background scheduler will record every 15 minutes if automatic recordings are enabled.

Note:
    Make sure you have proper consent for video recording and comply with privacy regulations.
"""

import cv2
import time
import threading
import schedule
import logging
import os
from licensing_module import LicenseManager

# Initialize license manager
license_manager = LicenseManager()
if not license_manager.is_licensed():
    print("License validation failed. Please check your license key.")
    exit(1)

# ------------------------------------------------------------------------------
# Configuration: Set the folder where recordings and logs are stored.
# ------------------------------------------------------------------------------
SAVE_DIR = r"C:\Users\USER\Documents\Recordings"  # Directory for saved files.
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Define the log file path.
LOG_FILE = os.path.join(SAVE_DIR, "recording_log.log")

# ------------------------------------------------------------------------------
# Logging Configuration: Log messages to console and file.
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# ------------------------------------------------------------------------------
# Global Variables for Status Management
# ------------------------------------------------------------------------------
# Count the number of recordings (both scheduled and manual).
record_count = 0
# Flag to determine whether automatic scheduling is active.
automatic_enabled = True

# ------------------------------------------------------------------------------
# Visual Warning: Display a warning window during recording.
# ------------------------------------------------------------------------------
def recording_warning_window(stop_event):
    """
    Displays a small window that warns the user that the camera is recording.
    The window remains open until the provided stop_event is set.
    
    Parameters:
        stop_event (threading.Event): An event that, when set, will close the window.
    """
    try:
        import tkinter as tk
    except ImportError:
        logging.error("tkinter is not available. Please install or enable tkinter to see the recording warning.")
        return

    root = tk.Tk()
    root.title("Recording In Progress")
    # Position the window at the top right (adjust geometry as needed)
    root.geometry("300x100+1000+50")
    root.attributes("-topmost", True)

    label = tk.Label(root, text="Camera is recording", fg="red", font=("Arial", 16))
    label.pack(expand=True, fill="both")

    def check_stop():
        if stop_event.is_set():
            root.destroy()
        else:
            root.after(100, check_stop)
    check_stop()
    root.mainloop()

# ------------------------------------------------------------------------------
# Functions for Recording and Logging
# ------------------------------------------------------------------------------

def record_video_for_duration(filename, record_duration=60):
    """
    Records video from the default webcam for the specified duration and saves it.
    While the recording is in progress, a warning window is displayed.
    
    Parameters:
        filename (str): Full path for the output video file.
        record_duration (int): Recording duration in seconds (default is 60).
    """
    global record_count
    cap = cv2.VideoCapture(0)  # Open the default webcam.
    if not cap.isOpened():
        logging.error("Unable to access the webcam.")
        return

    # Optionally, set the desired resolution:
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Create a VideoWriter object.
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0.0:
        fps = 20.0  # Fallback value if fps is not available.
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (frame_width, frame_height)
    out = cv2.VideoWriter(filename, fourcc, fps, frame_size)

    # Create an event and start the warning window thread.
    stop_event = threading.Event()
    warning_thread = threading.Thread(target=recording_warning_window, args=(stop_event,), daemon=True)
    warning_thread.start()

    start_time = time.time()
    logging.info(f"Recording started; saving to {filename}")

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to capture a frame from the webcam.")
            break

        out.write(frame)

        # End the recording after the specified duration.
        if (time.time() - start_time) > record_duration:
            logging.info("Record duration reached.")
            break

        time.sleep(0.01)  # Small delay to reduce CPU load

    cap.release()
    out.release()
    logging.info(f"Recording saved to {filename}")

    # Log the recorded file's duration.
    duration = inspect_video_duration(filename)
    logging.info(f"Recorded video duration: {duration:.2f} seconds.")
    
    # Log the resolution of the recording.
    check_recording_resolution(filename)
    
    record_count += 1

    # Signal the warning window thread to close its window.
    stop_event.set()
    warning_thread.join()  # Wait for the warning window to close.

def inspect_video_duration(filename):
    """
    Computes the duration of the given video file.
    
    Parameters:
        filename (str): Path to the video file.
    
    Returns:
        float: Duration of the video (in seconds).
    """
    cap = cv2.VideoCapture(filename)
    if not cap.isOpened():
        logging.error(f"Cannot open video file: {filename}")
        return 0.0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps if fps else 0.0
    cap.release()
    return duration

def check_recording_resolution(filename):
    """
    Checks and logs the resolution of the given video file.
    
    Parameters:
        filename (str): The full path to the video file.
    
    Returns:
        tuple: (width, height) in pixels, or (None, None) if the file cannot be opened.
    """
    cap = cv2.VideoCapture(filename)
    if not cap.isOpened():
        logging.error(f"Cannot open file: {filename} to check resolution.")
        return None, None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    logging.info(f"Video resolution for '{filename}': {width} x {height} pixels")
    return width, height

def scheduled_recording_job():
    """
    Generates a unique filename and performs a scheduled recording.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"recording_{timestamp}.avi")
    record_duration = 60  # seconds
    logging.info(f"Scheduled recording job triggered at {timestamp}")
    record_video_for_duration(filename, record_duration)

def run_scheduler():
    """
    Continuously checks and runs scheduled jobs.
    """
    while True:
        schedule.run_pending()
        time.sleep(1)

# ------------------------------------------------------------------------------
# Interactive Menu Functions (including Status and Toggle Stop/Resume)
# ------------------------------------------------------------------------------

def show_status():
    """
    Displays the current status, including:
      - Whether automatic (scheduled) recordings are enabled.
      - The next scheduled job time (if any).
      - The total number of recordings performed.
    """
    status = "Active" if automatic_enabled else "Stopped"
    next_job = schedule.next_run() if automatic_enabled else "Not scheduled"
    print("\n--- CURRENT STATUS ---")
    print(f"Automatic Recordings: {status}")
    print(f"Next Scheduled Job: {next_job}")
    print(f"Total Recordings Completed: {record_count}")
    print("----------------------\n")
    input("Press Enter to return to menu...")

def toggle_automatic_recordings():
    """
    Toggles the state of automatic recordings.
    When disabled, clears all scheduled jobs.
    When re-enabled, schedules the job every 15 minutes.
    """
    global automatic_enabled
    if automatic_enabled:
        schedule.clear()
        automatic_enabled = False
        logging.info("Automatic scheduled recordings have been STOPPED.")
        print("\nAutomatic scheduled recordings have been STOPPED.\n")
    else:
        schedule.every(15).minutes.do(scheduled_recording_job)
        automatic_enabled = True
        logging.info("Automatic scheduled recordings have been RESUMED.")
        print("\nAutomatic scheduled recordings have been RESUMED.\n")
    input("Press Enter to return to menu...")

def manual_recording():
    """
    Allows an immediate manual recording.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"manual_recording_{timestamp}.avi")
    duration_input = input("Enter recording duration in seconds (default is 60): ").strip()
    try:
        record_duration = int(duration_input) if duration_input else 60
    except ValueError:
        print("Invalid input; defaulting to 60 seconds.")
        record_duration = 60
    record_video_for_duration(filename, record_duration)

def view_log():
    """
    Displays the last 15 lines of the log file.
    """
    if not os.path.exists(LOG_FILE):
        print("Log file does not exist yet.")
        input("Press Enter to return to menu...")
        return
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    print("\n--- Log File (Last 15 Lines) ---")
    for line in lines[-15:]:
        print(line.rstrip())
    print("--- End of Log ---")
    input("Press Enter to return to menu...")

def main_menu():
    """
    Displays the interactive menu and processes user commands.
    Menu options:
      1. Manual Recording
      2. View Log File
      3. Show Status
      4. Toggle Automatic Recordings (Stop/Resume)
      5. Exit Program
    """
    while True:
        print("\n=== Scheduled Recording Menu ===")
        print("1. Trigger an immediate manual recording")
        print("2. View log file")
        print("3. Show status")
        print("4. Toggle automatic scheduled recordings (Stop/Resume)")
        print("5. Exit program")
        choice = input("Enter your choice [1-5]: ").strip()
        if choice == "1":
            manual_recording()
        elif choice == "2":
            view_log()
        elif choice == "3":
            show_status()
        elif choice == "4":
            toggle_automatic_recordings()
        elif choice == "5":
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

# ------------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Initially schedule the automatic recording if enabled.
    if automatic_enabled:
        schedule.every(15).minutes.do(scheduled_recording_job)

    # Start the scheduler thread (runs in the background).
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logging.info("Scheduler is running. A recording job will execute every 15 minutes (if enabled).")

    # Launch the interactive menu.
    main_menu()
    logging.info("Program terminated by user.")