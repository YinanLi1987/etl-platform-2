import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkExtractor:
    """Extracts .zip and .xlsx links from meeting pages with error control."""

    def __init__(self):
        # Initialize URLs and paths from environment variables
        self.wg_base_urls = os.getenv('WG_BASE_URLS', '').split(',')
        self.tsg_base_urls = os.getenv('TSG_BASE_URLS', '').split(',')
        self.document_link_base = os.getenv('DOCUMENT_LINK_BASE')
        self.excel_link_base = os.getenv('MEETING_EXCEL_LINK_BASE')

        # Define the required output directories
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dirs = {
            "wg_meeting_ids": Path("data/download_links/wg_meeting_ids"),
            "tsg_meeting_ids": Path("data/download_links/tsg_meeting_ids"),
            "wg_tdoc_links": Path("data/download_links/wg_tdoc_links"),
            "tsg_tdoc_links": Path("data/download_links/tsg_tdoc_links"),
            "wg_excel_links": Path("data/download_links/wg_excel_links"),
            "tsg_excel_links": Path("data/download_links/tsg_excel_links")
        }

        # Create directories if they don't exist
        for path in self.output_dirs.values():
            path.mkdir(parents=True, exist_ok=True)

    def get_meeting_ids(self, urls):
        """Fetches meeting IDs from the given base URLs."""
        meeting_ids = []
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    match = re.search(r'meetingId=(\d+)', link['href'])
                    if match:
                        meeting_ids.append(match.group(1))
            except requests.RequestException as e:
                logger.error(f"Error fetching meeting IDs from {url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error while parsing meeting IDs from {url}: {e}")
        return meeting_ids

    def extract_links(self, meeting_id, link_base, file_type):
        """Extracts specific file type links for a given meeting ID."""
        file_links = []
        try:
            doc_url = link_base + meeting_id
            response = requests.get(doc_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if link['href'].endswith(file_type):
                    file_links.append(f"{meeting_id}: {link['href']}")
        except requests.RequestException as e:
            logger.error(f"Error fetching {file_type} links for meeting ID {meeting_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while extracting {file_type} links for meeting ID {meeting_id}: {e}")
        return file_links

    def save_links_to_file(self, links, output_path):
        """Saves links to a specified text file."""
        try:
            with open(output_path, 'w') as f:
                for link in links:
                    f.write(link + "\n")
        except IOError as e:
            logger.error(f"Error saving links to {output_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while writing to file {output_path}: {e}")

    def run(self):
        """Main method to extract and save links, with error control."""
        try:
            # Extract all WG and TSG meeting IDs
            wg_meeting_ids = self.get_meeting_ids(self.wg_base_urls)
            tsg_meeting_ids = self.get_meeting_ids(self.tsg_base_urls)

            # Save WG and TSG meeting IDs to their respective folders
            self.save_links_to_file(wg_meeting_ids, self.output_dirs["wg_meeting_ids"] / "wg_meeting_ids.txt")
            self.save_links_to_file(tsg_meeting_ids, self.output_dirs["tsg_meeting_ids"] / "tsg_meeting_ids.txt")

            # Collect WG .zip links and save to file
            wg_zip_links = []
            for meeting_id in wg_meeting_ids:
                wg_zip_links.extend(self.extract_links(meeting_id, self.document_link_base, ".zip"))
            self.save_links_to_file(wg_zip_links, self.output_dirs["wg_tdoc_links"] / "wg_tdoc_links.txt")

            # Collect TSG .zip links and save to file
            tsg_zip_links = []
            for meeting_id in tsg_meeting_ids:
                tsg_zip_links.extend(self.extract_links(meeting_id, self.document_link_base, ".zip"))
            self.save_links_to_file(tsg_zip_links, self.output_dirs["tsg_tdoc_links"] / "tsg_tdoc_links.txt")

            # Collect WG .xlsx links and save to file
            wg_excel_links = []
            for meeting_id in wg_meeting_ids:
                wg_excel_links.extend(self.extract_links(meeting_id, self.excel_link_base, ".xlsx"))
            self.save_links_to_file(wg_excel_links, self.output_dirs["wg_excel_links"] / "wg_excel_links.txt")

            # Collect TSG .xlsx links and save to file
            tsg_excel_links = []
            for meeting_id in tsg_meeting_ids:
                tsg_excel_links.extend(self.extract_links(meeting_id, self.excel_link_base, ".xlsx"))
            self.save_links_to_file(tsg_excel_links, self.output_dirs["tsg_excel_links"] / "tsg_excel_links.txt")

            # Return number of each type of link
            return {
                "wg_zip_count": len(wg_zip_links),
                "tsg_zip_count": len(tsg_zip_links),
                "wg_excel_count": len(wg_excel_links),
                "tsg_excel_count": len(tsg_excel_links),
                "date_str": datetime.now().strftime("%Y%m%d_%H%M%S")
            }

        except Exception as e:
            logger.error(f"Unexpected error during link extraction: {e}")
            return {
                "wg_zip_count": 0,
                "tsg_zip_count": 0,
                "wg_excel_count": 0,
                "tsg_excel_count": 0,
                "date_str": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
