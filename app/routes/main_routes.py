# app/routes/main_routes.py

from flask import Blueprint, Blueprint, request, jsonify, render_template,current_app
from app.processes.process_pip import process_documents
from app.processes.load_extract_save import load_extract_save_data
from app.processes.changement_image import detect_and_crop_regions_from_pdf
import os


process_bp = Blueprint('process_bp', __name__)

@process_bp.route("/")
def index():
        """Serve the main download page."""
        return render_template('index.html')
    

@process_bp.route('/process', methods=['POST'])
def handle_process():
    """Handle the file download request."""
    temp_folder = current_app.config['TEMP_FOLDER']
    preprocessed_folder=current_app.config['PREPROCESSED_FOLDER']
    extracted01_folder=current_app.config['EXTRACTED01_FOLDER']
    extracted02_folder=current_app.config['EXTRACTED02_FOLDER']

    try:
        #Step 1: Validate the URL
        url = request.form.get('url')
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
               # Crop image
               detect_and_crop_regions_from_pdf(pdf_path, extracted02_folder)
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
