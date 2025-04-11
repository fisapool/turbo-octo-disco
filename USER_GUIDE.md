# Webcam Activity Tracker - User Guide

## What is this application?

The Webcam Activity Tracker is a tool that helps monitor your posture and activity using your computer's webcam. It's designed to help you maintain good posture while working at your computer.

## How does it work?

1. **Live Preview**: The application shows you a live preview of what your webcam is capturing, so you can see exactly what's being recorded.

2. **Posture Analysis**: It analyzes your posture using advanced computer vision technology to detect if you're maintaining good posture.

3. **Data Collection**: The application takes occasional snapshots and short video clips to track your posture over time.

4. **Local Storage**: All data is stored locally on your computer in the `webcam_data` folder. Nothing is sent over the internet.

## How to use the application

### Simple Test (Recommended for first-time users)

1. Run the simple test script:
   ```
   python simple_webcam_test.py
   ```

2. You should see a window showing your webcam feed.

3. The application will take a test snapshot after 3 seconds.

4. Press 'q' to quit the application.

### Full Activity Tracker

Once you're comfortable with the simple test, you can try the full activity tracker:

1. Run the full activity tracker:
   ```
   python test_webcam.py
   ```

2. Read the instructions on the screen and press Enter to start.

3. You should see a window showing your webcam feed with posture analysis.

4. Press 'q' to quit the application.

## Privacy and Security

- **All data is stored locally**: The application saves data only on your computer.
- **No internet connection required**: The application works completely offline.
- **You control when to stop**: You can stop the application at any time by pressing 'q' or Ctrl+C.
- **No data sharing**: The application does not send any data over the internet.

## Troubleshooting

If you encounter issues:

1. **Camera not showing**: Make sure your webcam is properly connected and has the necessary permissions in Windows.

2. **Application is slow**: The application uses advanced computer vision technology which can be resource-intensive. Try closing other applications to improve performance.

3. **Camera light is on but no image**: This usually means the camera is working but there might be a permission issue. Check your Windows camera permissions.

4. **Beeping sound**: This might be due to high CPU usage. The application has been optimized to reduce this, but you can try closing other applications.

## Data Storage

All data is stored in the `webcam_data` folder:

- **Snapshots**: JPG files showing still images
- **Recordings**: AVI files showing short video clips
- **Data files**: JSON files containing posture analysis data

You can delete these files at any time if you want to remove the stored data.

## Need Help?

If you have any questions or concerns, please contact the developer or refer to the project documentation. 