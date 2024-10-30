# app/routes/main_routes.py

from flask import Blueprint, Blueprint, request, jsonify, render_template,current_app

from app.services.meeting_extractor import MeetingLinkExtractor
from app.services.cr_links_extractor import CRZipLinkExtractor 
from app.services.download import ZipFileDownloader
import os
import json
from datetime import datetime
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

process_bp = Blueprint('process_bp', __name__)

@process_bp.route("/")
def index():
            # Load existing links and get the total count and last updated date
    extractor = MeetingLinkExtractor()
    extractor.load_existing_links()  # Load existing links to get count and last update
    total_links = len(extractor.existing_links)
    last_updated = max(
        [f for f in os.listdir('data/extracted_links') if f.endswith('.txt')],
        key=lambda f: os.path.getmtime(os.path.join('data/extracted_links', f)),
        default="No files found"
    )
    return render_template('index.html', total_links=total_links, last_updated=last_updated)


@process_bp.route('/extract_links', methods=['POST'])
def extract_links():
    extractor = MeetingLinkExtractor()  # Instantiate without arguments
    new_links_count, date_str = extractor.run()

    # Return a JSON response with the number of new links extracted
    return jsonify({
        'new_links_count': new_links_count,
        'date_str': date_str
    })

@process_bp.route('/extract_cr_links', methods=['POST'])
def extract_cr_links():
    try:
        # Instantiate the CRLinkExtractor (or a function that processes CR links)
        cr_extractor = CRZipLinkExtractor()
        cr_links_extracted, meeting_links_removed = cr_extractor.run()

        # Return a JSON response with extracted CR links count and removed meeting links count
        return jsonify({
            'cr_links_extracted': cr_links_extracted,
            'meeting_links_removed': meeting_links_removed
        })

    except Exception as e:
        current_app.logger.error(f"Error in CR link extraction: {str(e)}")
        return jsonify({"error": "An error occurred during CR link extraction."}), 500

@process_bp.route('/download', methods=['POST'])
def download():
    try:
        # Load the latest document links from the extracted_links folder
        latest_url = get_latest_document_link()
        print("hello")
        if not latest_url:
            return jsonify({"error": "No document links found."}), 400
        
         # Here, implement your download logic
        downloader = ZipFileDownloader(latest_url)  # Instantiate your downloader
        
        # Check if there are downloadable links
        downloadable_links = downloader.get_downloadable_links()  # Assuming this method checks for downloadable links
        if not downloadable_links:
            return jsonify({"error": "No downloadable ZIP links found for the latest document."}), 404
        
        # Start downloading the files (you can implement this as you see fit)
        downloader.download(downloadable_links)

        return jsonify({"message": f"Download started for {len(downloadable_links)} ZIP files from {latest_url}."}), 200

    except Exception as e:
        current_app.logger.error(f"Error in download process: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500
def get_latest_document_link():
    """Get the latest document link from the document_links files."""
    directory = os.path.join('data', 'extracted_links')
    # Ensure the directory exists
    if not os.path.exists(directory):
        return None

    # Find the most recently modified document_links file
    files = sorted(
        (f for f in os.listdir(directory) if f.endswith('.txt')),
        key=lambda x: os.path.getmtime(os.path.join(directory, x)),
        reverse=True
    )
    
    if not files:
        return None
    
    # Read the most recent file and return the first URL found
    latest_file_path = os.path.join(directory, files[0])
    with open(latest_file_path, 'r') as file:
        # Assuming each line in the file contains a URL
        urls = file.readlines()
        if urls:
            return urls[0].strip()  # Return the first URL

    return None