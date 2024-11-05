
import zipfile
from pathlib import Path
import re


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
                # Extract the numeric prefix from the zip file name
                match = re.match(r"(\d+)_", zip_file.name)
                if match:
                    prefix = match.group(1)


                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        for file_info in zip_ref.infolist():
                            # Prepend the prefix to the original filename
                            extracted_filename = f"{prefix}_{file_info.filename}"
                            # Define the full path for the extracted file
                            extracted_filepath = self.unzip_folder / extracted_filename
                            
                            # Write the file with the new name
                            with extracted_filepath.open("wb") as extracted_file:
                                extracted_file.write(zip_ref.read(file_info.filename))
                            
                        print(f"Unzipped: {zip_file.name} with files renamed to include prefix '{prefix}'")
                else:
                    print(f"Skipped: {zip_file.name} (No valid prefix found)")




                    #zip_ref.extractall(self.unzip_folder)
                print(f"Unzipped: {zip_file.name}")
            except zipfile.BadZipFile:
                print(f"Failed to unzip: {zip_file.name} (Bad zip file)")
            except Exception as e:
                print(f"An error occurred while unzipping {zip_file.name}: {e}")
   