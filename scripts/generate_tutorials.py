import os
import json
from datetime import datetime
from pathlib import Path

class TutorialGenerator:
    def __init__(self):
        self.tutorials_dir = Path("docs/tutorials")
        self.templates_dir = Path("docs/templates")
        self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.tutorials_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def generate_tutorial_script(self, title, description, steps, duration_minutes=5):
        """Generate a tutorial script with timestamps."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{title.lower().replace(' ', '_')}.md"
        
        content = f"""# {title}

## Overview
{description}

## Video Details
- Duration: {duration_minutes} minutes
- Level: Beginner/Intermediate
- Last Updated: {datetime.now().strftime("%Y-%m-%d")}

## Timestamps
"""
        
        # Calculate timestamps based on duration and number of steps
        total_seconds = duration_minutes * 60
        step_duration = total_seconds / len(steps)
        
        for i, step in enumerate(steps, 1):
            timestamp_seconds = int(i * step_duration)
            minutes = timestamp_seconds // 60
            seconds = timestamp_seconds % 60
            content += f"\n{minutes:02d}:{seconds:02d} - {step['title']}\n"
            content += f"{step['description']}\n"
            
            if 'code' in step:
                content += f"\n```python\n{step['code']}\n```\n"
            
            if 'notes' in step:
                content += f"\n> Note: {step['notes']}\n"

        # Add resources section
        content += """
## Resources
- [Documentation](docs/user_guide.md)
- [API Reference](docs/api_docs.md)
- [Troubleshooting Guide](docs/troubleshooting_guide.md)

## Next Steps
1. Practice the demonstrated features
2. Explore related documentation
3. Join our community forum for questions
"""

        # Save the tutorial script
        with open(self.tutorials_dir / filename, 'w') as f:
            f.write(content)
        
        return filename

    def generate_tutorial_metadata(self, tutorial_data):
        """Generate metadata for tutorial tracking."""
        metadata = {
            "title": tutorial_data["title"],
            "description": tutorial_data["description"],
            "duration": tutorial_data["duration_minutes"],
            "level": tutorial_data.get("level", "Beginner"),
            "tags": tutorial_data.get("tags", []),
            "prerequisites": tutorial_data.get("prerequisites", []),
            "last_updated": datetime.now().isoformat(),
            "file": tutorial_data["filename"]
        }
        
        # Update metadata file
        metadata_file = self.tutorials_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                existing_metadata = json.load(f)
        else:
            existing_metadata = []
        
        existing_metadata.append(metadata)
        
        with open(metadata_file, 'w') as f:
            json.dump(existing_metadata, f, indent=2)

def main():
    # Example tutorial data
    getting_started_tutorial = {
        "title": "Getting Started with HR Analytics",
        "description": "Learn how to set up and start using the HR Analytics platform.",
        "duration_minutes": 10,
        "level": "Beginner",
        "tags": ["setup", "basics", "configuration"],
        "prerequisites": ["Python 3.8+", "Basic Python knowledge"],
        "steps": [
            {
                "title": "Installation",
                "description": "Install the HR Analytics platform and its dependencies.",
                "code": "pip install hr-analytics",
                "notes": "Make sure you have Python 3.8 or higher installed."
            },
            {
                "title": "Initial Configuration",
                "description": "Set up your initial configuration and preferences.",
                "code": "python -m hr_analytics configure",
                "notes": "You can modify these settings later."
            },
            {
                "title": "Starting the Application",
                "description": "Launch the application and verify the setup.",
                "code": "python -m hr_analytics start",
                "notes": "Check the system tray for the application icon."
            }
        ]
    }

    # Generate tutorial
    generator = TutorialGenerator()
    filename = generator.generate_tutorial_script(
        title=getting_started_tutorial["title"],
        description=getting_started_tutorial["description"],
        steps=getting_started_tutorial["steps"],
        duration_minutes=getting_started_tutorial["duration_minutes"]
    )
    
    # Add filename to tutorial data and generate metadata
    getting_started_tutorial["filename"] = filename
    generator.generate_tutorial_metadata(getting_started_tutorial)

if __name__ == "__main__":
    main() 