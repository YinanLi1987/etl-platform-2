# app/routes/main_routes.py

from flask import Blueprint, Blueprint, request, jsonify, render_template,current_app

from app.services.meeting_extractor import MeetingLinkExtractor
from app.services.cr_links_extractor import CRZipLinkExtractor 
from app.services.downloader import CRZipDownloader
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
        [f for f in os.listdir('data/meeting_links') if f.endswith('.txt')],
        key=lambda f: os.path.getmtime(os.path.join('data/meeting_links', f)),
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

@process_bp.route('/download_all_files', methods=['POST'])
def download_all_files():
    downloader = CRZipDownloader()
    try:
        successful_downloads, failed_downloads = downloader.download_all_files()
        return jsonify({
            'success_count': successful_downloads,
            'failed_files': failed_downloads,
            'failed_count': len(failed_downloads)
        })
    except Exception as e:
        current_app.logger.error(f"Error in download process: {str(e)}")
        return jsonify({"error": "An error occurred during the download process."}), 500