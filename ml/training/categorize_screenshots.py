import os
import shutil
from pathlib import Path

# Source and destination paths
src_dir = 'ActiveWindowScreenshots'
train_dir = 'data/train'
val_dir = 'data/validation'

# Create category folders if they don't exist
for category in ['code', 'document', 'web']:
    os.makedirs(f'{train_dir}/{category}', exist_ok=True)
    os.makedirs(f'{val_dir}/{category}', exist_ok=True)

def categorize_and_copy(filename):
    """Categorize screenshot and copy to appropriate folder"""
    lower_name = filename.lower()
    
    # Determine category
    if 'python' in lower_name or 'cmd' in lower_name or 'code' in lower_name:
        category = 'code'
    elif 'edge' in lower_name or 'copilot' in lower_name or 'chrome' in lower_name:
        category = 'web'
    else:
        category = 'document'  # Default for file explorer, notepad etc.
    
    # Split into train/validation (80/20)
    dest_dir = train_dir if hash(filename) % 10 < 8 else val_dir
    shutil.copy2(f'{src_dir}/{filename}', f'{dest_dir}/{category}/{filename}')

# Process all screenshots
for filename in os.listdir(src_dir):
    if filename.endswith('.png'):
        categorize_and_copy(filename)

print(f"Copied screenshots to {train_dir} and {val_dir}")
