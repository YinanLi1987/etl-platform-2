from flask import current_app
from app.processes.download import download_documents
from app.processes.docx_to_pdf import convert_file_service


def process_documents(url, temp_folder, preprocessed_folder):
    """
    This function handles the full process:
    1. Download documents from the provided URL.
    2. Unzip and save the documents.
    3. Convert DOC/DOCX files to PDF.
    """
    # Step 1: Download the documents
    total_files, number_of_links = download_documents(url, temp_folder)
    # Step 2: Convert DOC/DOCX files to PDF
    converted_count = convert_file_service(temp_folder, preprocessed_folder)
    

    return {
        'total_files_downloaded': total_files,
        'number_of_links_found': number_of_links,
        'total_files_converted': converted_count,
       
    }