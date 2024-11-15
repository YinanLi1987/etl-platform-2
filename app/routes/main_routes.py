# app/routes/main_routes.py

from flask import Blueprint, Blueprint, request, jsonify, render_template,current_app

from app.services.downloader.link_extractor import LinkExtractor
from app.services.downloader.link_downloader import LinkDownloader
from app.services.downloader.unzipper import FileUnzipperFilter
from app.services.extraction.data_extractor_pdf import process_file_and_update_json
from app.services.transformation.transformer import clean_json_cr
from app.services.validation.json_validater import validate_json

import os
import json
import shutil
from datetime import datetime
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

process_bp = Blueprint('process_bp', __name__)

@process_bp.route("/")
def index():

    last_updated = max(
        [f for f in os.listdir('data/download_links/tsg_excel_links') if f.endswith('.txt')],
        key=lambda f: os.path.getmtime(os.path.join('data/download_links/tsg_excel_links', f)),
        default="No files found"
    )
    return render_template('index.html',  last_updated=last_updated)


@process_bp.route('/extract_links', methods=['POST'])
def extract_links():
    extractor = LinkExtractor()
    link_counts = extractor.run()
    # Return JSON with the number of each type of link extracted and the date
    return jsonify({
        'wg_zip_count': link_counts['wg_zip_count'],
        'tsg_zip_count': link_counts['tsg_zip_count'],
        'wg_excel_count': link_counts['wg_excel_count'],
        'tsg_excel_count': link_counts['tsg_excel_count'],
        'date_str': link_counts['date_str']
    })

@process_bp.route('/download_all_files', methods=['POST'])
def download_all_files():
    downloader = LinkDownloader()
    try:
        # Download all files and get the result with counts of each category
        download_counts = downloader.run()
        
        # Return counts for each category
        return jsonify({
            'tsg_excel_count': download_counts['tsg_excel_links'],
            'wg_excel_count': download_counts['wg_excel_links'],
            'wg_tdoc_count': download_counts['wg_tdoc_links'],
            'failed_count': len(download_counts.get('failed_files', []))
        })
        
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({"error": "An error occurred during the download process."}), 500

    
@process_bp.route('/unzip_files', methods=['POST'])
def unzip_files():
    try:
        # Specify your download and temp folder paths
        download_folder = "data/download_files/wg_tdoc"  # Adjust this to your actual path
        temp_folder = "data/download_files/temp"  # Adjust this to your actual path
        unzipper = FileUnzipperFilter(download_folder, temp_folder)
        
        # Call the unzip method and get the count
        unzipper.unzip_files()
        
        #
        return jsonify({'unzipped completed.'})
    except Exception as e:
        current_app.logger.error(f"Error during unzipping: {str(e)}")
        return jsonify({"error": "An error occurred during the unzipping process."}), 500





@process_bp.route('/convert_file', methods=['POST'])
def convert_file():
    #input_file = "data/temp/unzip/C1-245945_was_C1-245892_was_C1-245482_PROSE_Ph3_UpdPolProv.docx"  # Change this to the appropriate path if necessary
    input_folder = "data/download_files/wg_tdoc"  # Folder containing the DOCX files
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
    

@process_bp.route('/validate_cleaned_data', methods=['POST'])
def validate_cleaned_data():
    input_folder = "data/clean_cr_json/"
    invalid_folder = "data/invalid_cleaned_json/"
    os.makedirs(invalid_folder, exist_ok=True)

   
# Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):  # Only process JSON files
            file_path = os.path.join(input_folder, filename)

            # Read the JSON file
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {filename}")
                    continue  # Skip the file if it's not a valid JSON

            # Validate the JSON file
            valid, error_msg = validate_json(data)
            if not valid:
                # If validation fails, move the file to the invalid folder
                invalid_file_path = os.path.join(invalid_folder, filename)
                shutil.move(file_path, invalid_file_path)
                print(f"Moved invalid file: {filename} to invalid folder. Reason: {error_msg}")
            else:
                print(f"Validated successfully: {filename}")

    return "Validation complete"