import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from dotenv import load_dotenv
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZipFileDownloader:
    def __init__(self, url, download_folder="data/downloads", max_retries=3, timeout=10):
        self.url = self.validate_url(url)
        self.download_folder = download_folder
        self.zip_links = []
        self.max_retries = max_retries
        self.timeout = timeout

        # Load allowed prefixes, base URL, and User-Agent from environment variables
        self.allowed_prefixes = os.getenv('ALLOWED_PREFIXES').split(',')
        self.base_url = os.getenv('BASE_URL')
        self.user_agent = os.getenv('USER_AGENT')  # New User-Agent variable

        # Create the download directory if it doesn't exist
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)



    def validate_url(self,url):
        """Check if the URL is valid and starts with 'http' or 'https'."""
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            logger.error("Invalid URL provided: %s", url)
            raise ValueError("Invalid URL provided")
        return url

    def download_html(self):
        """Download the HTML content from the provided URL."""
        try:
            headers = {
                'User-Agent': self.user_agent  # Use User-Agent from the .env file
            }
            response = requests.get(self.url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
           logger.error("Error while downloading HTML: %s", str(e))
           raise 

    def extract_zip_links(self,html_content):
        """Extract .zip links that include '=R4-' from the HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_links = set()  # Use a set to avoid duplicates
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.endswith('.zip') and any(prefix in href for prefix in self.allowed_prefixes):
                full_url = urljoin(self.base_url, href)
                self.zip_links.append(full_url)
    # Update self.zip_links with new unique links
        self.zip_links.extend(extracted_links - set(self.zip_links))

    # Log the number of links extracted
        logger.info("Extracted %d unique .zip links.", len(extracted_links))

    def download_file(self, url):
        """Download a file from the given URL with retries."""
        for attempt in range(self.max_retries):
            try:
                local_filename = os.path.join(self.download_folder, os.path.basename(urlparse(url).path))
                logger.info("Downloading %s to %s", url, local_filename)

                with requests.get(url, stream=True, timeout=self.timeout) as response:
                    response.raise_for_status()
                    with open(local_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                logger.info("Downloaded %s", local_filename)
                return local_filename

            except requests.exceptions.RequestException as e:
                logger.warning("Error downloading %s (attempt %d/%d): %s", url, attempt + 1, self.max_retries, str(e))
                time.sleep(2)  # Delay before retrying

        logger.error("Failed to download %s after %d attempts", url, self.max_retries)
        return None

    def run(self):
        """Main execution method to perform the download process."""
        start_time = datetime.now()

        try:
            html_content = self.download_html()
            self.extract_zip_links(html_content)

            downloaded_files = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(self.download_file, zip_link): zip_link for zip_link in self.zip_links}

                for future in as_completed(futures):
                    zip_link = futures[future]
                    try:
                        downloaded_file = future.result()
                        if downloaded_file:
                            downloaded_files.append(downloaded_file)
                    except Exception as e:
                        logger.error("Error occurred for %s: %s", zip_link, str(e))

            end_time = datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()

            return {
                'downloaded_files': downloaded_files,
                'total_links': len(self.zip_links),
                'elapsed_time': elapsed_time
            }

        except Exception as e:
            logger.error("An error occurred in the run process: %s", str(e))
            return {
                'downloaded_files': [],
                'total_links': len(self.zip_links),
                'elapsed_time': None
            }