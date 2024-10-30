import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from datetime import datetime
from flask import current_app
# Load environment variables
load_dotenv()

class CRZipLinkExtractor:
    def __init__(self):
        self.allowed_prefixes = os.getenv('ALLOWED_PREFIXES').split(',')
        self.base_url = os.getenv('BASE_URL')
        self.meeting_links_folder = 'data/meeting_links'
        self.cr_links_folder = 'data/cr_links'
        self.user_agent = os.getenv('USER_AGENT')  # Load USER_AGENT from .env

        # Use the loaded User-Agent in headers
        self.headers = {
            'User-Agent': self.user_agent
        }

        # Ensure CR links folder exists
        os.makedirs(self.cr_links_folder, exist_ok=True)

    
    def get_latest_meeting_file(self):
        """Find the most recently modified meeting links file in the specified folder."""
        files = [f for f in os.listdir(self.meeting_links_folder) if f.endswith('.txt')]
        if not files:
            return None
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.meeting_links_folder, f)))
        return os.path.join(self.meeting_links_folder, latest_file)
    
    def extract_cr_links(self, meeting_link):
        """Extract .zip links with allowed prefixes from a meeting link's page."""
        try:
            response = requests.get(meeting_link, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                current_app.logger.error(f"Error in CR link extraction: Access denied (403) for URL: {meeting_link}")
                return []  # Return an empty list to continue with other links
            else:
                current_app.logger.error(f"Error in CR link extraction: {str(e)}")
                return []
        soup = BeautifulSoup(response.text, 'html.parser')
        cr_links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.endswith('.zip') and any(prefix in href for prefix in self.allowed_prefixes):
                full_url = urljoin(self.base_url, href)
                cr_links.append(full_url)

        return cr_links
    
    
    
    
    
    def run(self):
        """Run the CR link extraction process from the latest meeting link file."""
        # Get the latest meeting links file
        latest_meeting_file = self.get_latest_meeting_file()
        if not latest_meeting_file:
            raise FileNotFoundError("No meeting links file found in the data/meeting_links directory.")

        cr_links_extracted = 0
        meeting_links_removed = 0
        valid_meeting_links = []
         # Timesstamped output file for all CR links
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.cr_links_folder, f"cr_links_{timestamp}.txt")

        with open(latest_meeting_file, 'r') as file:
            meeting_links = file.readlines()

                # Extract CR links from each meeting link
        with open(output_file, 'w') as cr_file:
            for meeting_link in meeting_links:
                cr_links = self.extract_cr_links(meeting_link.strip())
                if cr_links:
                    cr_links_extracted += len(cr_links)
                    valid_meeting_links.append(meeting_link)
                    cr_file.write('\n'.join(cr_links) + '\n')
                else:
                    meeting_links_removed += 1

        # Update the meeting links file to only include links with CR links
        with open(latest_meeting_file, 'w') as file:
            file.writelines(valid_meeting_links)

        return cr_links_extracted, meeting_links_removed