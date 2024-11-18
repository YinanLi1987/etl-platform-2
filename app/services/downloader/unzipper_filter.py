import zipfile
from pathlib import Path
import re
import shutil
from docx import Document
from dir_manage import (WG_TDOC_FOLDER,UNZIP_FILES_FOLDER)

class FileUnzipperFilter:
    def __init__(self):
        self.download_folder = Path(WG_TDOC_FOLDER)
        self.unzip_folder= Path(UNZIP_FILES_FOLDER)
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
                
                print(f"Unzipped: {zip_file.name}")
                
            except zipfile.BadZipFile:
                print(f"Failed to unzip: {zip_file.name} (Bad zip file)")
            except Exception as e:
                print(f"An error occurred while unzipping {zip_file.name}: {e}")

        # Call cleanup methods after unzipping
        self.cleanup_download_folder()
        self.cleanup_unzip_folder()
    
    def cleanup_download_folder(self):
        """Deletes all .zip files from the download folder."""
        for zip_file in self.download_folder.glob("*.zip"):
            try:
                zip_file.unlink()
                print(f"Deleted original zip file: {zip_file.name}")
            except Exception as e:
                print(f"Failed to delete zip file {zip_file.name}: {e}")

    def cleanup_unzip_folder(self):
        """Removes non-.docx files from the unzip folder, and moves .zip files back to the download folder."""
        for file in self.unzip_folder.iterdir():
            if file.is_file():
                if file.suffix == ".docx":
                    # Check if the .docx file meets the criteria
                    if not self.check_docx_content(file):
                        # If the criteria is not met, delete the file
                        try:
                            file.unlink()
                            print(f"Deleted .docx file without 'CHANGE REQUEST' in the first table: {file.name}")
                        except Exception as e:
                            print(f"Failed to delete file {file.name}: {e}")
                    else:
                        print(f"Kept .docx file with 'CHANGE REQUEST' in the first table: {file.name}")
                elif file.suffix == ".zip":
                    # Move .zip files back to the download folder
                    destination = self.download_folder / file.name
                    try:
                        shutil.move(str(file), str(destination))
                        print(f"Moved zip file back to download folder: {file.name}")
                    except Exception as e:
                        print(f"Failed to move file {file.name}: {e}")
                else:
                    # Delete all other files
                    try:
                        file.unlink()
                        print(f"Deleted non-docx file: {file.name}")
                    except Exception as e:
                        print(f"Failed to delete file {file.name}: {e}")

    def check_docx_content(self, docx_file):
        """
        Checks the content of the first table in a .docx file.
        If the first table does not contain 'CHANGE REQUEST' in the first 5 lines, returns False.
        """
        try:
            document = Document(docx_file)
            tables = document.tables
            if tables:
                # Access the first table
                first_table = tables[0]
                # Read the first 5 rows of the table
                for i, row in enumerate(first_table.rows[:5]):
                    for cell in row.cells:
                        if "CHANGE REQUEST" in cell.text:
                            return True  # Found 'CHANGE REQUEST' in the first table
            # If no 'CHANGE REQUEST' was found in the first 5 rows
            return False
        except Exception as e:
            print(f"Failed to read {docx_file.name}: {e}")
            return False
