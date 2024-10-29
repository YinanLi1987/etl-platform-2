# app/routes/main_routes.py

from flask import Blueprint, Blueprint, request, jsonify, render_template,current_app
from app.services.process_pip import process_documents
from app.services.load_extract_save import load_extract_save_data
from app.services.changement_image import detect_and_crop_regions_from_pdf
from app.services.meeting_extractor import MeetingLinkExtractor
import os
import json
from datetime import datetime
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
BASE_URLS = os.getenv('BASE_URLS').split(',')
DOCUMENT_LINK_BASE = os.getenv('DOCUMENT_LINK_BASE')


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

@process_bp.route('/download', methods=['POST'])
def handle_process():
    """Handle the file download request."""
    temp_folder = current_app.config['TEMP_FOLDER']
    preprocessed_folder=current_app.config['PREPROCESSED_FOLDER']
    extracted01_folder=current_app.config['EXTRACTED01_FOLDER']
    extracted02_folder=current_app.config['EXTRACTED02_FOLDER']

    try:
        #Step 1: Validate the URL
        url = request.form.get('url')
        if not url:
            raise ValueError("URL is missing or invalid.")
        #Step 2:Process the documents (download + conversion)
        result = process_documents(url, temp_folder, preprocessed_folder)
        # Step 3: Load, extract data and save data to json
        for pdf_file in os.listdir(preprocessed_folder):
            if pdf_file.endswith(".pdf"):  # Only process PDF files
               pdf_path = os.path.join(preprocessed_folder, pdf_file)
    
               # Save the extracted data as JSON file
               json_filename = f"{os.path.splitext(pdf_file)[0]}_extracted.json"
               json_path = os.path.join(extracted01_folder, json_filename)
               
               # Call the function to load, extract, and save data  
               load_extract_save_data(pdf_path, json_path)
               # Step 4: Retrieve the document_number from the JSON file
               with open(json_path, 'r') as json_file:
                    json_data = json.load(json_file)
                    document_number = json_data.get("document_number", "Unknown")
               # Crop image
               detect_and_crop_regions_from_pdf(pdf_path, extracted02_folder,document_number,json_path)
               # Save the extracted data including URLs to the JSON file
               
               print(f"Finished detect_and_crop_regions_from_pdf for {pdf_file}")
              
    
        return jsonify({
            "detected_message": f"{result['number_of_links_found']} documents detected.",  
            "download_message": f"{result['total_files_downloaded']} documents downloaded.",   
            "conversion_message": f"{result['total_files_converted']} documents converted to PDF.",       
        }), 200
    
    except ValueError as ve:
            return jsonify({"error": str(ve)}), 400  # Handle invalid URL case with 400 Bad Request
    except Exception as e:
            return jsonify({"error": str(e)}), 500  # Handle general errors with 500 Internal Server Error
