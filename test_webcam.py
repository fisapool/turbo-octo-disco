import cv2
import time
import os
from webcam_integration import WebcamIntegration

def main():
    print("=" * 50)
    print("WEBCAM ACTIVITY TRACKER - USER GUIDE")
    print("=" * 50)
    print("\nThis application helps track your posture and activity using your webcam.")
    print("It will show you a live preview of what it's capturing.")
    print("\nWhat this app does:")
    print("1. Shows a live preview of your webcam feed")
    print("2. Takes occasional snapshots (saved in 'webcam_data' folder)")
    print("3. Records short video clips (saved in 'webcam_data' folder)")
    print("4. Analyzes your posture (data saved in JSON files)")
    print("\nYour privacy is important:")
    print("- All data is stored locally on your computer")
    print("- No data is sent over the internet")
    print("- You can stop the application at any time by pressing 'q' or Ctrl+C")
    print("\nPress Enter to start, or Ctrl+C to exit...")
    input()
    
    print("\nStarting webcam test...")
    try:
        # Create output directory if it doesn't exist
        os.makedirs('webcam_data', exist_ok=True)
        
        # Initialize webcam integration
        integration = WebcamIntegration()
        
        # Start the integration
        print("Starting webcam integration...")
        integration.start()
        
        # Create a window for the preview
        cv2.namedWindow("Webcam Preview", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Webcam Preview", 640, 480)
        
        print("\nWebcam is now active!")
        print("You should see a live preview window.")
        print("Press 'q' to quit the application.")
        
        # Keep running until user presses 'q'
        while True:
            # Get the latest frame from the integration
            with integration.frame_lock:
                if integration.frame_buffer is not None:
                    frame = integration.frame_buffer.copy()
                    
                    # Add text to the frame
                    cv2.putText(frame, "Webcam Activity Tracker", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Show the frame
                    cv2.imshow("Webcam Preview", frame)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # Small delay to prevent high CPU usage
            time.sleep(0.03)
            
    except KeyboardInterrupt:
        print("\nStopping webcam integration...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Stop the integration
        if 'integration' in locals():
            integration.stop()
        
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        
        print("\nTest completed. Thank you for using the Webcam Activity Tracker!")
        print("Your data has been saved in the 'webcam_data' folder.")

if __name__ == "__main__":
    main() 