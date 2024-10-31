
import zipfile
from pathlib import Path


class FileUnzipper:
    def __init__(self, download_folder, temp_folder):
        self.download_folder = Path(download_folder)
        self.temp_folder = Path(temp_folder)
        
        # Define specific folders for unzipped files, HTML, and PDF files
        self.unzip_folder = self.temp_folder / 'unzip'
       

        # Create necessary folders if they do not exist
        self.unzip_folder.mkdir(parents=True, exist_ok=True)

    
    def unzip_files(self):
        """Unzips all .zip files in the download folder and extracts them to the unzip folder."""
        for zip_file in self.download_folder.glob("*.zip"):
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(self.unzip_folder)
                print(f"Unzipped: {zip_file.name}")
            except zipfile.BadZipFile:
                print(f"Failed to unzip: {zip_file.name} (Bad zip file)")
            except Exception as e:
                print(f"An error occurred while unzipping {zip_file.name}: {e}")
   