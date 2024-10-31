# services/meeting_extractor.py

from bs4 import BeautifulSoup
import requests
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_URLS = os.getenv('BASE_URLS').split(',')
DOCUMENT_LINK_BASE = os.getenv('DOCUMENT_LINK_BASE')
WG_MEETING_EXCEL_LINK_BASE=os.getenv('WG_MEETING_EXCEL_LINK_BASE')
#print(WG_MEETING_EXCEL_LINK_BASE)

class MeetingLinkExtractor:
    def __init__(self):
        self.existing_links = set()  # To keep track of existing links
        self.load_existing_links()    # Load existing links at initialization

    def load_existing_links(self):
        """Load existing links from the most recent file."""
        try:
            # Find the most recently modified .txt file in the 'data/extracted_links' directory
            directory = os.path.join('data', 'meeting_links')
            if not os.path.exists(directory):
                os.makedirs(directory)
            # Load the last updated file (by date)
            
             # Find all .txt files in the directory
            files = [f for f in os.listdir(directory) if f.endswith('.txt')]
            if not files:
                print("No existing link files found.")
                return  # Exit if no files found
            # Load links from each file
            for file in files:
                with open(os.path.join(directory, file), 'r') as f:
                    self.existing_links.update(f.read().splitlines())
            print(f"Loaded {len(self.existing_links)} existing links")
            

        except Exception as e:
            print(f"Error loading existing links: {e}")

    def download_html(self, url):
        """Download HTML content from a URL."""
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def extract_meeting_ids(self, html_content):
        """Extract meeting IDs from the page based on 'MtgId=' pattern."""
        soup = BeautifulSoup(html_content, 'html.parser')
        meeting_ids = []
        wg_meeting_excel_links = []
        
        # Find links with 'MtgId=' in the URL
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if 'MtgId=' in href:
                # Extract the meeting ID from the href
                match = re.search(r'MtgId=(\d+)', href)
                if match:
                    meeting_id = match.group(1)
                    link = f"{DOCUMENT_LINK_BASE}{meeting_id}"
                    wg_meeting_excel_link = f"{WG_MEETING_EXCEL_LINK_BASE}{meeting_id}"
                    #print(wg_meeting_excel_link)
                    wg_meeting_excel_links.append(wg_meeting_excel_link)
                    
                    if link not in self.existing_links:
                        meeting_ids.append(link)
        #print(wg_meeting_excel_links)
                        
        return meeting_ids, wg_meeting_excel_links

    def run(self):
        self.load_existing_links()  # Load existing links at the start
        all_new_links = []  # To store newly extracted links
        all_excel_links = []  # To store all Excel links


        for url in BASE_URLS:
            # Step 1: Download page for each base URL
            #print(f"Processing {url}...")
            main_page_html = self.download_html(url)
            
            # Step 2: Extract meeting IDs
            new_links,excel_links = self.extract_meeting_ids(main_page_html)
            all_new_links.extend(new_links)
            all_excel_links.extend(excel_links)
            
        # Save newly extracted links with date in the filename
        if all_new_links:
            date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            output_dir = os.path.join('data', 'meeting_links')
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
            output_file = os.path.join(output_dir, f'meeting_links_{date_str}.txt')
            with open(output_file, 'w') as file:
                for link in all_new_links:
                    file.write(f"{link}\n")
            print(f"Saved {len(all_new_links)} new links to {output_file}")
            return len(all_new_links), date_str  # Return the count and date
        else:
            print("No new links found.")
        # Save all Excel links with date in the filename
        if all_excel_links:
            date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            output_dir = os.path.join('data', 'wg_excel_links')
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
            excel_output_file = os.path.join(output_dir, f'wg_meeting_excel_links_{date_str}.txt')
            with open(excel_output_file, 'w') as file:
                for excel_link in all_excel_links:
                    file.write(f"{excel_link}\n")
            print(f"Saved {len(all_excel_links)} Excel links to {excel_output_file}")

        # Return counts for both types of links
        return len(all_new_links), len(all_excel_links)

