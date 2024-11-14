import os
import requests
from datetime import datetime
from config import load_headers

headers = load_headers()

class LinkDownloader:
    def __init__(self):
        # Define folder paths
        self.input_folders = {
            "tsg_excel_links": "data/download_links/tsg_excel_links",
            "wg_excel_links": "data/download_links/wg_excel_links",
            "wg_tdoc_links": "data/download_links/wg_tdoc_links"
        }
        self.output_folders = {
            "tsg_excel_links": "data/download_files/tsg_excel",
            "wg_excel_links": "data/download_files/wg_excel",
            "wg_tdoc_links": "data/download_files/wg_tdoc"
        }
        # Ensure output folders exist
        for path in self.output_folders.values():
            os.makedirs(path, exist_ok=True)

    def get_latest_file(self, folder_path):
        """Find the latest .txt file in the specified folder."""
        try:
            txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
            if not txt_files:
                print(f"No .txt files found in {folder_path}")
                return None
            latest_file = max(
                txt_files, 
                key=lambda f: os.path.getmtime(os.path.join(folder_path, f))
            )
            return os.path.join(folder_path, latest_file)
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error accessing folder {folder_path}: {e}")
            return None

    def parse_links(self, file_path, is_tdoc=False):
        """Parse the links and meeting IDs from a given .txt file."""
        links = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        if is_tdoc:
                            # For wg_tdoc_links: Format is "meeting_id: url"
                            meeting_id, url = line.split(": ", 1)
                        else:
                            # For excel links: Format contains meetingId in the URL
                            url = line
                            meeting_id = url.split("meetingId=")[-1]
                        links.append((meeting_id, url))
                    except ValueError:
                        print(f"Skipping line with invalid format in {file_path}: {line}")
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error reading file {file_path}: {e}")
        return links

    def download_file(self, url, output_path):
        """Download a file from a URL using headers and save it to the output path."""
        try:
            print(f"Attempting to download: {url}")
            response = requests.get(url,headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            with open(output_path, 'wb') as file:
                
                    file.write(response.content)
            print(f"Downloaded: {output_path}")
            return True
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
            return False
        except (OSError, IOError) as e:
            print(f"Error saving file {output_path}: {e}")
            return False
    def run(self):
        download_counts = {
            'tsg_excel_links': 0,
            'wg_excel_links': 0,
            'wg_tdoc_links': 0,
            'failed_files': []
        }
        """Main method to find, parse, and download links from the latest files."""
        for key, folder_path in self.input_folders.items():
            latest_file = self.get_latest_file(folder_path)
            if not latest_file:
                print(f"Skipping folder due to missing or inaccessible file: {folder_path}")
                continue

            print(f"Processing file: {latest_file}")
            is_tdoc = (key == "wg_tdoc_links")
            links = self.parse_links(latest_file, is_tdoc=is_tdoc)

            if not links:
                print(f"No valid links found in file {latest_file}")
                continue

            for meeting_id, url in links:
                # Construct the filename as meetingid.xlsx
                filename = f"{meeting_id}.xlsx"
                output_path = os.path.join(self.output_folders[key], filename)
                
                # Attempt to download the file and track success or failure
                if self.download_file(url, output_path):
                    download_counts[key] += 1  # Increment count for successful download
                else:
                    download_counts['failed_files'].append(url)  # Add to failed list

        return download_counts
