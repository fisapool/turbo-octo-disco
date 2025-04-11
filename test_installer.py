import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import traceback
import logging

# Set up logging
logging.basicConfig(
    filename="test_installer_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class InstallerTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HR Analytics Installer Tester")
        self.root.geometry("600x500")
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        ttk.Label(main_frame, text="HR Analytics Installer Tester", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=20)
        
        # Test buttons
        ttk.Button(main_frame, text="Test Python Environment", command=self.test_python).grid(row=1, column=0, pady=10, sticky=tk.W)
        ttk.Button(main_frame, text="Test Required Packages", command=self.test_packages).grid(row=2, column=0, pady=10, sticky=tk.W)
        ttk.Button(main_frame, text="Test File Access", command=self.test_files).grid(row=3, column=0, pady=10, sticky=tk.W)
        ttk.Button(main_frame, text="Test GUI Components", command=self.test_gui).grid(row=4, column=0, pady=10, sticky=tk.W)
        ttk.Button(main_frame, text="Run Full Test", command=self.run_full_test).grid(row=5, column=0, pady=10, sticky=tk.W)
        
        # Results area
        ttk.Label(main_frame, text="Test Results:", font=("Helvetica", 12, "bold")).grid(row=6, column=0, sticky=tk.W, pady=10)
        
        self.results_text = tk.Text(main_frame, height=10, width=60)
        self.results_text.grid(row=7, column=0, pady=10)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.root.quit).grid(row=8, column=0, pady=20)
        
    def log_result(self, test_name, success, message):
        result = f"{test_name}: {'SUCCESS' if success else 'FAILED'} - {message}\n"
        self.results_text.insert(tk.END, result)
        if success:
            logging.info(result)
        else:
            logging.error(result)
    
    def test_python(self):
        try:
            version = sys.version
            self.log_result("Python Environment", True, f"Python version: {version}")
        except Exception as e:
            self.log_result("Python Environment", False, f"Error: {str(e)}")
    
    def test_packages(self):
        try:
            required_packages = [
                "tkinter", "subprocess", "shutil", "pathlib", "json", 
                "traceback", "logging", "winshell", "win32com.client"
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                self.log_result("Required Packages", False, f"Missing packages: {', '.join(missing_packages)}")
            else:
                self.log_result("Required Packages", True, "All required packages are installed")
        except Exception as e:
            self.log_result("Required Packages", False, f"Error: {str(e)}")
    
    def test_files(self):
        try:
            required_files = [
                "installer.py", "activity_tracker.py", "dashboard.py", 
                "analytics_engine.py", "data_collection.py", "config.json"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if missing_files:
                self.log_result("File Access", False, f"Missing files: {', '.join(missing_files)}")
            else:
                self.log_result("File Access", True, "All required files are accessible")
        except Exception as e:
            self.log_result("File Access", False, f"Error: {str(e)}")
    
    def test_gui(self):
        try:
            # Test if we can create a simple window
            test_window = tk.Toplevel(self.root)
            test_window.title("Test Window")
            test_window.geometry("300x200")
            
            ttk.Label(test_window, text="If you can see this window, GUI is working!").pack(pady=20)
            ttk.Button(test_window, text="Close", command=test_window.destroy).pack()
            
            self.log_result("GUI Components", True, "GUI components are working")
        except Exception as e:
            self.log_result("GUI Components", False, f"Error: {str(e)}")
    
    def run_full_test(self):
        self.results_text.delete(1.0, tk.END)
        self.test_python()
        self.test_packages()
        self.test_files()
        self.test_gui()
        
        # Check if all tests passed
        results = self.results_text.get(1.0, tk.END)
        if "FAILED" not in results:
            messagebox.showinfo("Test Results", "All tests passed! The installer should work correctly.")
        else:
            messagebox.showwarning("Test Results", "Some tests failed. Please check the results for details.")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        tester = InstallerTester()
        tester.run()
    except Exception as e:
        logging.error(f"Unhandled exception: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Create a simple error window that won't close immediately
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Critical Error", 
                            f"An unexpected error occurred: {str(e)}\n\n"
                            "Please check the test_installer_log.txt file for details.\n\n"
                            "Click OK to exit.")
        root.destroy() 