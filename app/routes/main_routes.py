# app/routes/main_routes.py

from flask import Blueprint, Blueprint, request, jsonify, render_template,current_app

from app.services.downloader.meeting_extractor import MeetingLinkExtractor
from app.services.downloader.cr_links_extractor import CRZipLinkExtractor 
from app.services.downloader.downloader import CRZipDownloader
from app.services.downloader.meeting_excel_downloader import ExcelDownloader 
from app.services.extraction.unzipper import FileUnzipper
from app.services.extraction.data_extractor_pdf import process_file_and_update_json
from app.services.transformation.transformer import clean_json_cr

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
    
@process_bp.route('/unzip_files', methods=['POST'])
def unzip_files():
    try:
        # Specify your download and temp folder paths
        download_folder = "data/downloads"  # Adjust this to your actual path
        temp_folder = "data/temp"  # Adjust this to your actual path
        unzipper = FileUnzipper(download_folder, temp_folder)
        
        # Call the unzip method and get the count
        unzipper.unzip_files()
        
        # Count the number of unzipped files
        unzipped_files_count = len(list(unzipper.unzip_folder.glob("*")))  # Count files in the unzip folder
        
        return jsonify({'unzipped_files_count': unzipped_files_count})
    except Exception as e:
        current_app.logger.error(f"Error during unzipping: {str(e)}")
        return jsonify({"error": "An error occurred during the unzipping process."}), 500



@process_bp.route('/download_meeting_excel', methods=['POST'])
def download_meeting_excel():
    downloader = ExcelDownloader()
    try:
        successful_downloads, failed_downloads = downloader.download_all_files()
        return jsonify({
            'success_count': successful_downloads,
            'failed_files': failed_downloads,
            'failed_count': len(failed_downloads)
        })
    except Exception as e:
        current_app.logger.error(f"Error in meeting Excel download process: {str(e)}")
        return jsonify({"error": "An error occurred during the meeting Excel download process."}), 500



@process_bp.route('/convert_file', methods=['POST'])
def convert_file():
    #input_file = "data/temp/unzip/C1-245945_was_C1-245892_was_C1-245482_PROSE_Ph3_UpdPolProv.docx"  # Change this to the appropriate path if necessary
    input_folder = "data/temp/unzip/"  # Folder containing the DOCX files
    converted_folder = "data/temp/converted_pdf"  # Folder to save converted PDFs
    json_folder = "data/extracted_data/"  # Folder to save extracted JSON data

    try:
        # Ensure output folders exist
        os.makedirs(converted_folder, exist_ok=True)
        os.makedirs(json_folder, exist_ok=True)

        # List all files in the input folder
        for filename in os.listdir(input_folder):
            # Process only .docx files
            if filename.endswith('.docx'):
                input_file = os.path.join(input_folder, filename)
                current_app.logger.info(f"Processing file: {input_file}")
                
                # Call the function to process each file
                process_file_and_update_json(input_file, converted_folder, json_folder)

        return jsonify({"message": "File conversion and data extraction completed successfully."})
    
    except Exception as e:
        current_app.logger.error(f"Error during file conversion: {str(e)}")
        return jsonify({"error": "An error occurred during file conversion."}), 500
    
@process_bp.route('/clean_data', methods=['POST'])
def clean_data():
            # Define the path to the JSON file that needs cleaning
    input_folder="data/extracted_data/"
    output_folder="data/clean_cr_json/"
    try:

   
        # Ensure output folders exist
        os.makedirs(output_folder, exist_ok=True)

        # Call the update function to clean the JSON file
        clean_json_cr(input_folder,output_folder)

        return jsonify({"message": "Data cleaning process completed successfully."})
    
    except Exception as e:
        current_app.logger.error(f"Error during data cleaning: {str(e)}")
        return jsonify({"error": "An error occurred during the data cleaning process."}), 500