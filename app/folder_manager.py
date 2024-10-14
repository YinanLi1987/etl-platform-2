import os
from pathlib import Path

def create_folder(folder_path):
    """Create a folder if it doesn't exist."""
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def create_required_folders(base_path):
    """Create necessary folders for the application."""
    folders = [ 'temp','preprocessed','extracted01','extracted02']
    for folder in folders:
        create_folder(base_path / folder)

def delete_folder(folder_path):
    """Delete a folder and all its contents."""
    folder = Path(folder_path)
    if folder.exists() and folder.is_dir():
        for item in folder.iterdir():
            if item.is_dir():
                delete_folder(item)  # Recursive call for subdirectories
            else:
                item.unlink()  # Delete the file
        folder.rmdir()  # Remove the empty directory