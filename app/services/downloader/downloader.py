import os
import requests
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from flask import current_app

# Load environment variables
load_dotenv()


class CRZipDownloader:
    def __init__(self):
        self.cr_links_folder = 'data/cr_links'
        self.download_folder = 'data/downloads'
        
        os.makedirs(self.download_folder, exist_ok=True)
        self.max_retries = 3
        self.retry_delay = 10  # seconds



    def get_latest_cr_links_file(self):
        """Get the latest CR links .txt file."""
        files = [f for f in os.listdir(self.cr_links_folder) if f.endswith('.txt')]
        if not files:
            return None
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.cr_links_folder, f)))
        return os.path.join(self.cr_links_folder, latest_file)

    def download_file(self, meeting_id, url):
        """Download a single file with retry logic and a custom filename."""
        # Extract the original filename from the URL
        original_filename = url.split('/')[-1]
        filename = os.path.join(self.download_folder, f"{meeting_id}_{original_filename}")
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(filename, 'wb') as file:
                    file.write(response.content)
                return filename, True
            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Download attempt {attempt+1} for {url} failed: {str(e)}")
                sleep(self.retry_delay)
        return filename, False

    def download_all_files(self):
        """Download all files from the latest CR links file."""
        cr_links_file = self.get_latest_cr_links_file()
        if not cr_links_file:
            raise FileNotFoundError("No CR links file found in the data/cr_links directory.")

        successful_downloads = 0
        failed_downloads = []

        with open(cr_links_file, 'r') as file:
            # Split each line into meeting ID and URL
            for line in file:
                line = line.strip()
                if line:
                    meeting_id, url = line.split(':', 1)  # Split on the first colon
                    meeting_id = meeting_id.strip()  # Clean the meeting ID
                    url = url.strip()  # Clean the URL

                    # Download the file using the meeting ID and the URL
                    filename, success = self.download_file(meeting_id, url)
                    if success:
                        successful_downloads += 1
                    else:
                        failed_downloads.append(filename)

        return successful_downloads, failed_downloads