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

# Set up logging
logging.basicConfig(
    filename="installer_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class HRAnalyticsInstaller:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("HR Analytics Platform Installer")
            self.root.geometry("500x300")  # Smaller window size
            self.setup_ui()
            logging.info("Installer UI initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing installer: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error_and_exit(f"Failed to initialize installer: {str(e)}")
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Welcome message with simpler text
        ttk.Label(main_frame, 
                 text="HR Analytics Setup\n\nThis will install the basic activity tracking tool.",
                 font=("Helvetica", 12),
                 justify=tk.CENTER).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Installation path with browse button
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        ttk.Label(path_frame, text="Install to:").pack(side=tk.LEFT)
        self.install_path = tk.StringVar(value=str(Path.home() / "HR Analytics"))
        ttk.Entry(path_frame, textvariable=self.install_path, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_path).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Big install button
        self.install_button = ttk.Button(
            main_frame, 
            text="INSTALL", 
            command=self.install,
            style="Big.TButton"
        )
        self.install_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Configure styles
        style = ttk.Style()
        style.configure("Big.TButton", font=('Helvetica', 12, 'bold'), padding=10)
        
    def install(self):
        try:
            self.install_button.state(['disabled'])
            self.progress['value'] = 0
            logging.info("Starting installation process")
            
            # Create installation directory
            install_dir = Path(self.install_path.get())
            install_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created installation directory: {install_dir}")
            
            # Install core dependencies
            self.progress['value'] = 20
            self.install_dependencies()
            
            # Copy application files
            self.progress['value'] = 40
            self.copy_application_files(install_dir)
            
            # Configure features
            self.progress['value'] = 60
            self.configure_features(install_dir)
            
            # Attempt to create desktop shortcut
            self.progress['value'] = 80
            shortcut_created = self.create_shortcut(install_dir)
            
            self.progress['value'] = 100
            if shortcut_created:
                logging.info("Installation completed successfully with shortcut")
                messagebox.showinfo("Success", "Installation completed successfully!\nA desktop shortcut was created.")
            else:
                logging.info("Installation completed successfully (no shortcut)")
                messagebox.showinfo("Success", 
                    "Installation completed successfully!\n\n"
                    "Note: Could not create desktop shortcut.\n"
                    "You can run the program from:\n"
                    f"{install_dir / 'activity_tracker.py'}")
            self.root.quit()
            
        except Exception as e:
            logging.error(f"Installation failed: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("Error", f"Installation failed: {str(e)}\n\nPlease check the installer_log.txt file for details.")
            self.install_button.state(['!disabled'])
    
    def browse_path(self):
        """Let user browse for installation directory"""
        from tkinter import filedialog
        path = filedialog.askdirectory(
            title="Select Installation Folder",
            initialdir=str(Path.home())
        )
        if path:
            self.install_path.set(path)

    def install_dependencies(self):
        try:
            logging.info("Installing core dependencies")
            # Install only core requirements
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-core.txt"], check=True)
            logging.info("Core dependencies installed successfully")
        except Exception as e:
            logging.error(f"Failed to install dependencies: {str(e)}")
            raise
    
    def copy_application_files(self, install_dir):
        try:
            logging.info(f"Copying application files to {install_dir}")
            # Copy core application files
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
                    logging.info(f"Copied {file} to {install_dir}")
                else:
                    logging.warning(f"File not found: {file}")
            
            logging.info("Application files copied successfully")
        except Exception as e:
            logging.error(f"Failed to copy application files: {str(e)}")
            raise
    
    def configure_features(self, install_dir):
        try:
            logging.info("Configuring basic features")
            # Default configuration with only core features
            config = {
                "core_features": True,
                "webcam_features": False, 
                "analytics_features": False
            }
            
            # Save configuration
            config_path = install_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            
            logging.info(f"Basic configuration saved to {config_path}")
        except Exception as e:
            logging.error(f"Failed to configure features: {str(e)}")
            raise
    
    def create_shortcut(self, install_dir):
        try:
            logging.info("Attempting to create desktop shortcut")
            # Create desktop shortcut
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "HR Analytics.lnk"
            
            try:
                # Create Windows shortcut if winshell available
                import winshell
                from win32com.client import Dispatch
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = str(install_dir / "activity_tracker.py")
                shortcut.WorkingDirectory = str(install_dir)
                shortcut.save()
                
                logging.info(f"Desktop shortcut created at {shortcut_path}")
                return True
            except ImportError:
                logging.warning("Skipping shortcut creation - winshell not installed")
                return False
            except Exception as e:
                logging.warning(f"Couldn't create shortcut: {str(e)}")
                return False
        except Exception as e:
            logging.warning(f"Shortcut creation failed: {str(e)}")
            return False
    
    def show_error_and_exit(self, error_message):
        """Show error message and keep window open until user clicks OK"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Error", error_message)
        root.destroy()
        sys.exit(1)
    
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            logging.error(traceback.format_exc())
            self.show_error_and_exit(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        # Add a try-except block around the entire program
        installer = HRAnalyticsInstaller()
        installer.run()
    except Exception as e:
        # Log the error and show a message box
        logging.error(f"Unhandled exception: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Create a simple error window that won't close immediately
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Critical Error", 
                            f"An unexpected error occurred: {str(e)}\n\n"
                            "Please check the installer_log.txt file for details.\n\n"
                            "Click OK to exit.")
        root.destroy() 