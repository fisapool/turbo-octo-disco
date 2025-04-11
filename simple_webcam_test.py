import cv2
import time
import os

def main():
    print("=" * 50)
    print("SIMPLE WEBCAM TEST")
    print("=" * 50)
    print("\nThis is a simple test to verify your webcam is working.")
    print("You should see a live preview of your webcam feed.")
    print("\nPress 'q' to quit the application.")
    
    # Create output directory if it doesn't exist
    os.makedirs('webcam_data', exist_ok=True)
    
    # Try to open the webcam
    print("\nTrying to open webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam. Please check your camera connection and permissions.")
        return
    
    # Set lower resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Create a window for the preview
    cv2.namedWindow("Webcam Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Webcam Test", 640, 480)
    
    print("\nWebcam is now active!")
    print("You should see a live preview window.")
    
    # Take a snapshot after 3 seconds
    snapshot_taken = False
    
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Add text to the frame
            cv2.putText(frame, "Simple Webcam Test", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Take a snapshot after 3 seconds
            if not snapshot_taken and time.time() > 3:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = os.path.join('webcam_data', f"test_snapshot_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                print(f"\nSnapshot saved: {filename}")
                snapshot_taken = True
            
            # Display the frame
            cv2.imshow("Webcam Test", frame)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Release the camera and close windows
        cap.release()
        cv2.destroyAllWindows()
        
        print("\nTest completed. Thank you for using the Simple Webcam Test!")
        if snapshot_taken:
            print("A test snapshot has been saved in the 'webcam_data' folder.")

if __name__ == "__main__":
    main() 