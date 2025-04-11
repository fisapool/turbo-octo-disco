import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import shutil
from pathlib import Path
import json
import traceback
import logging
import argparse

# Set up logging with more detailed information
logging.basicConfig(
    filename="installer_debug.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

def show_error_window(title, message):
    """Show an error message in a window that won't close immediately"""
    root = tk.Tk()
    root.title(title)
    root.geometry("600x400")
    
    frame = ttk.Frame(root, padding="20")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Error message
    ttk.Label(frame, text=message, wraplength=500).grid(row=0, column=0, pady=20)
    
    # Show the last few lines of the log file
    if os.path.exists("installer_debug.log"):
        with open("installer_debug.log", "r") as f:
            log_contents = f.readlines()[-10:]  # Last 10 lines
        log_text = tk.Text(frame, height=10, width=70)
        log_text.grid(row=1, column=0, pady=10)
        log_text.insert(tk.END, "Recent log entries:\n\n" + "".join(log_contents))
        log_text.config(state='disabled')
    
    # Close button
    ttk.Button(frame, text="Close", command=root.destroy).grid(row=2, column=0, pady=20)
    
    root.mainloop()

class HRAnalyticsInstaller:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        logging.info("Starting installer in %s mode", "debug" if debug_mode else "normal")
        
        try:
            self.root = tk.Tk()
            self.root.title("HR Analytics Platform Installer")
            self.root.geometry("600x400")
            self.setup_ui()
            logging.info("Installer UI initialized successfully")
        except Exception as e:
            logging.error("Failed to initialize installer: %s", str(e))
            logging.error("Traceback: %s", traceback.format_exc())
            show_error_window("Initialization Error", 
                            f"Failed to initialize installer:\n\n{str(e)}\n\n"
                            "Please check installer_debug.log for details.")
            sys.exit(1)
    
    def setup_ui(self):
        try:
            # Create main frame
            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Welcome message
            ttk.Label(main_frame, text="Welcome to HR Analytics Platform", 
                     font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=20)
            
            # Installation path
            ttk.Label(main_frame, text="Installation Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.install_path = tk.StringVar(value=str(Path.home() / "HR Analytics"))
            ttk.Entry(main_frame, textvariable=self.install_path, width=50).grid(row=1, column=1, sticky=tk.W, pady=5)
            
            # Features selection
            ttk.Label(main_frame, text="Features to Install:", 
                     font=("Helvetica", 12, "bold")).grid(row=2, column=0, sticky=tk.W, pady=10)
            
            self.core_features = tk.BooleanVar(value=True)
            ttk.Checkbutton(main_frame, text="Core Activity Tracking", 
                          variable=self.core_features).grid(row=3, column=0, sticky=tk.W)
            
            self.webcam_features = tk.BooleanVar(value=False)
            ttk.Checkbutton(main_frame, text="Webcam Posture Analysis (Optional)", 
                          variable=self.webcam_features).grid(row=4, column=0, sticky=tk.W)
            
            self.analytics_features = tk.BooleanVar(value=False)
            ttk.Checkbutton(main_frame, text="Advanced Analytics (Optional)", 
                          variable=self.analytics_features).grid(row=5, column=0, sticky=tk.W)
            
            # Progress bar
            self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
            self.progress.grid(row=6, column=0, columnspan=2, pady=20)
            
            # Status label
            self.status_var = tk.StringVar(value="Ready to install")
            ttk.Label(main_frame, textvariable=self.status_var).grid(row=7, column=0, columnspan=2)
            
            # Install button
            self.install_button = ttk.Button(main_frame, text="Install", command=self.install)
            self.install_button.grid(row=8, column=0, columnspan=2, pady=10)
            
            logging.info("UI setup completed successfully")
        except Exception as e:
            logging.error("Failed to setup UI: %s", str(e))
            logging.error("Traceback: %s", traceback.format_exc())
            raise
    
    def update_status(self, message):
        """Update the status message and log it"""
        logging.info(message)
        self.status_var.set(message)
        self.root.update()
    
    def install(self):
        try:
            self.install_button.state(['disabled'])
            self.progress['value'] = 0
            
            # Create installation directory
            install_dir = Path(self.install_path.get())
            self.update_status(f"Creating installation directory: {install_dir}")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Install core dependencies
            self.progress['value'] = 20
            self.update_status("Installing dependencies...")
            self.install_dependencies()
            
            # Copy application files
            self.progress['value'] = 40
            self.update_status("Copying application files...")
            self.copy_application_files(install_dir)
            
            # Configure features
            self.progress['value'] = 60
            self.update_status("Configuring features...")
            self.configure_features(install_dir)
            
            # Create desktop shortcut
            self.progress['value'] = 80
            self.update_status("Creating desktop shortcut...")
            self.create_shortcut(install_dir)
            
            self.progress['value'] = 100
            self.update_status("Installation completed successfully!")
            messagebox.showinfo("Success", "Installation completed successfully!")
            self.root.quit()
            
        except Exception as e:
            logging.error("Installation failed: %s", str(e))
            logging.error("Traceback: %s", traceback.format_exc())
            show_error_window("Installation Error", 
                            f"Installation failed:\n\n{str(e)}\n\n"
                            "Please check installer_debug.log for details.")
            self.install_button.state(['!disabled'])
    
    def install_dependencies(self):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True, text=True)
            logging.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logging.error("Failed to install dependencies: %s", e.output)
            raise Exception(f"Failed to install dependencies: {e.output}")
        except Exception as e:
            logging.error("Error installing dependencies: %s", str(e))
            raise
    
    def copy_application_files(self, install_dir):
        try:
            files_to_copy = [
                "activity_tracker.py",
                "dashboard.py",
                "analytics_engine.py",
                "data_collection.py",
                "config.json"
            ]
            
            for file in files_to_copy:
                if os.path.exists(file):
                    shutil.copy2(file, install_dir)
                    logging.info("Copied %s to %s", file, install_dir)
                else:
                    logging.warning("File not found: %s", file)
                    if self.debug_mode:
                        show_error_window("Missing File", 
                                        f"Warning: Could not find file: {file}\n"
                                        "The installation will continue, but some features may not work.")
        except Exception as e:
            logging.error("Failed to copy files: %s", str(e))
            raise
    
    def configure_features(self, install_dir):
        try:
            config = {
                "core_features": self.core_features.get(),
                "webcam_features": self.webcam_features.get(),
                "analytics_features": self.analytics_features.get(),
                "debug_mode": self.debug_mode
            }
            
            config_path = install_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            
            logging.info("Configuration saved to %s", config_path)
        except Exception as e:
            logging.error("Failed to save configuration: %s", str(e))
            raise
    
    def create_shortcut(self, install_dir):
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "HR Analytics.lnk"
            
            import winshell
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(install_dir / "activity_tracker.py")
            shortcut.WorkingDirectory = str(install_dir)
            shortcut.save()
            
            logging.info("Desktop shortcut created at %s", shortcut_path)
        except ImportError as e:
            logging.error("Failed to import shortcut creation modules: %s", str(e))
            if self.debug_mode:
                show_error_window("Shortcut Creation Error", 
                                "Could not create desktop shortcut due to missing modules.\n"
                                "The application is installed but you'll need to create a shortcut manually.")
        except Exception as e:
            logging.error("Failed to create shortcut: %s", str(e))
            raise
    
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error("Error in main loop: %s", str(e))
            logging.error("Traceback: %s", traceback.format_exc())
            show_error_window("Runtime Error", 
                            f"An error occurred while running the installer:\n\n{str(e)}\n\n"
                            "Please check installer_debug.log for details.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HR Analytics Platform Installer')
    parser.add_argument('--debug', action='store_true', help='Run installer in debug mode')
    args = parser.parse_args()
    
    try:
        installer = HRAnalyticsInstaller(debug_mode=args.debug)
        installer.run()
    except Exception as e:
        logging.error("Unhandled exception: %s", str(e))
        logging.error("Traceback: %s", traceback.format_exc())
        show_error_window("Critical Error", 
                        f"An unexpected error occurred:\n\n{str(e)}\n\n"
                        "Please check installer_debug.log for details.") 