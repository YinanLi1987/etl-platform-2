#This file will contain the reusable download logic like URL validation, downloading the file, and saving the file.
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import zipfile




def validate_url(url):
    """Check if the URL is valid and starts with 'http' or 'https'."""
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Invalid URL provided")
    return url

def download_html(url):
    """Download the HTML content from the provided URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)  # Include the headers in the request
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error while downloading HTML: {str(e)}")

def extract_zip_links(html_content):
    """Extract .zip links that include '=R4-' from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', href=True):
        if '=R4-' in a_tag['href']:
            full_url = urljoin('https://portal.3gpp.org', a_tag['href'])  # Adjust base URL if necessary
            links.append(full_url)
    return links

def download_zip_file(url):
    """Download a .zip file from the provided URL and return its content."""
    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error while downloading ZIP file: {str(e)}")

def find_actual_zip_url(intermediate_html):
    """Extract the actual .zip URL from the intermediate HTML page."""
    match = re.search(r"window\.location\.href='([^']*)'", intermediate_html)
    if match:
        return match.group(1)
    else:
        raise Exception("Failed to extract actual .zip URL")

def save_file(content, filename):
    """Save the downloaded file content to the local file system."""
    with open(filename, 'wb') as f:
        f.write(content)
    return filename

def unzip_file(zip_file_path,temp_folder):
    """Unzip the downloaded .zip file."""
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_folder)

def download_documents(url,temp_folder):
    """Main function to orchestrate the download process and count downloaded files."""
    total_files = 0  # Initialize total files counter
    try:
        # Step 1: Download the HTML page
        html_content = download_html(url)
        # Step 2: Extract .zip links that include '=R4-'
        zip_links = extract_zip_links(html_content)
        number_of_links = len(zip_links)
       
       
        # Step 3: Download .zip files
        for link in zip_links:
            try:
                print(f"Processing {link}")
                intermediate_html = download_html(link)  # Download intermediate HTML page
                actual_zip_url = find_actual_zip_url(intermediate_html)  # Extract the actual .zip URL

                print(f"Downloading from {actual_zip_url}")
                zip_content = download_zip_file(actual_zip_url)  # Download the actual .zip file

                # Step 4: Save the .zip file
                print(f"Saving to {temp_folder}")
                filename = os.path.join(temp_folder, os.path.basename(actual_zip_url))
                save_file(zip_content, filename)

                # Step 5: Unzip the downloaded .zip file
                print(f"Unzipping...")
                unzip_file(filename,temp_folder)

                # Optionally, delete the zip file after unzipping
                print(f"Removing the original zip file...")
                os.remove(filename)

                # Increment the downloaded count
                total_files += 1 

                
                print(f"{total_files} files downloaded and unzipped.")

            except Exception as e:
                print(f"An error occurred while processing the link {link}: {str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred during the download process: {str(e)}")
    return total_files, number_of_links