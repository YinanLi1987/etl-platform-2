import os
import re
import requests
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from flask import current_app

# Load environment variables
load_dotenv()


class ExcelDownloader:
    def __init__(self):
        self.wg_links_folder = 'data/meeting_links'
        self.download_folder = 'data/downloads/meetings_excel'
        self.user_agent = os.getenv('USER_AGENT')  # Load USER_AGENT from .env

        # Use the loaded User-Agent in headers
        self.headers = {
            'User-Agent': self.user_agent
        }

        
        os.makedirs(self.download_folder, exist_ok=True)
        self.max_retries = 3
        self.retry_delay = 10  # seconds



    def get_latest_wg_meeting_links_file(self):
        """Get the latest CR links .txt file."""
        files = [f for f in os.listdir(self.wg_links_folder) if f.endswith('.txt')]
        if not files:
            return None
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.wg_links_folder, f)))
        return os.path.join(self.wg_links_folder, latest_file)

    def download_file(self, url):
        """Download a single file with retry logic."""
        # Extract the meetingId from the URL
        match = re.search(r'meetingId=(\d+)', url)
        if match:
            meeting_id = match.group(1)
            filename = os.path.join(self.download_folder, f"{meeting_id}.xlsx")
        else:
            # Default to the last part of the URL if meetingId is not found
            filename = os.path.join(self.download_folder, url.split('/')[-1])
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers,timeout=10)
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
        wg_excel_links_file = self.get_latest_wg_meeting_links_file()
       

        if not wg_excel_links_file:
            raise FileNotFoundError("No wg excel file found in the data/meeting_links directory.")
        successful_downloads = 0
        failed_downloads = []

        with open(wg_excel_links_file, 'r') as file:
            urls = [line.strip() for line in file.readlines() if line.strip()]

        for url in urls:
            filename, success = self.download_file(url)
            if success:
                successful_downloads += 1
            else:
                failed_downloads.append(filename)

        return successful_downloads, failed_downloads


 

       