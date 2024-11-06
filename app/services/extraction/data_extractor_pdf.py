import os
import subprocess
import json
import re
import pdfplumber
from app.services.extraction.data import extracted_data, pdf_patterns
from app.services.extraction.data_extractor_html import extract_sections_llm
from app.services.extraction.data_extractor_image import detect_and_crop_regions_from_pdf



def convert_to_pdf_with_unoconv(input_file, converted_folder):
    """
    Use unoconv (LibreOffice) to convert a DOC/DOCX file to PDF with tracked changes.
    """

    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_pdf_path = os.path.join(converted_folder, f"{name}.pdf")
    try:
        subprocess.run(['unoconv', '-f', 'pdf', '-o', output_pdf_path, input_file], check=True)
        print(f"Converted {input_file} to {output_pdf_path}")
        return output_pdf_path  # Return the path of the converted PDF
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        return None


def extract_data_from_pdf(text):
    data = extracted_data.copy()
    #print("Extracted Text from PDF:", text)
    # Loop through patterns and assign matches to `data`
    for field, pattern in pdf_patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        #print(f"Checking field '{field}' with pattern '{pattern}'...")  # Log the field and pattern
        if match:
            #print(f"Match found for field '{field}': {match.groups()}")  # Log the match
            if field == "proposed_change_affects":
                options_line = match.group(1).strip()
                #print(options_line)
                options = ["UICC apps", "ME", "Radio Access Network", "Core Network"]
                #options = options_line.split()
                checked_options = []
                for option in options:
                # Create a regex pattern to match each option with an optional trailing "X"
                    pattern = rf"{option}\s*X?"
                    found = re.search(pattern, options_line)
                
                # If 'X' is found right after the option, add it to checked_options
                    if found and found.group(0).endswith("X"):
                        checked_options.append(option)
                data[field] = checked_options 
            else:
                if field == "dates":
                    data[field] = match.group(2).strip()  
                else:
                    data[field] = match.group(1).strip() 
        #else:
            # Log if the pattern was not found
            #print(f"No match for field '{field}' using pattern '{pattern}'.")

    # Log the data extracted
    #print("Extracted Data:", data)

    return data


def process_file_and_update_json(input_file, converted_folder, json_folder):
    """
    Convert a DOC/DOCX file to PDF, extract data from the PDF, and save as JSON.
    """
    try:
        # Ensure output folders exist
        os.makedirs(converted_folder, exist_ok=True)
        os.makedirs(json_folder, exist_ok=True)
    except Exception as e:
        print(f"Error creating directories: {e}")
        return
    document_number = os.path.splitext(os.path.basename(input_file))[0] 
    #print(document_number)
    # Extract meeting_id from filename (numeric prefix before "_")
    match = re.match(r"(\d+)_", os.path.basename(input_file))
    meeting_id = match.group(1) if match else "unknown"
    #print(meeting_id)
 
    # Convert DOCX file to PDF
    pdf_path = convert_to_pdf_with_unoconv(input_file, converted_folder)
    if pdf_path is None:
        print("PDF conversion failed.")
        return  # Exit if conversion failed

    # Extract text from the converted PDF
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Extract data from text
    data = extract_data_from_pdf(text)
    # Add the meeting_id to the extracted data
    data["meeting_id"] = meeting_id

    # Save extracted data to JSON
    json_filename = f"{document_number}.json" 
    json_path = os.path.join(json_folder, json_filename)
    with open(json_path, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Processed {input_file} and saved to {json_filename}")
    # Update JSON with sections data extracted from the DOCX file
    update_json_with_sections(json_path, input_file)
     # Detect colored regions, crop, and save URLs to JSON
    output_dir = os.path.join(converted_folder, "cropped_images")
    #document_number = data.get("document_number", "unknown_document")
    #detect_and_crop_regions_from_pdf(pdf_path, output_dir, document_number, json_path)



def update_json_with_sections(json_filename, docx_filename):
    """
    Update a JSON file with sections data extracted from a DOCX file.

    Args:
        json_filename (str): The name of the JSON file to update.
        docx_filename (str): The name of the DOCX file to convert and extract data from.
    """
    # Convert the DOCX file to cleaned HTML and extract sections data
    sections_data = extract_sections_llm(docx_filename)
    #print(f"Type of sections_data: {type(sections_data)}") 

    if sections_data is None:
        print("No sections data extracted.")
        return
       # Transform Section objects into a list of dictionaries for JSON serialization
    sections_list = sections_data.sections
    sections_as_dicts = [
        {"section_number": section.section_number, "section_title": section.section_title}
        for section in sections_list
    ]
    # Check if the JSON file exists
    if os.path.exists(json_filename):
        # Load existing JSON data
        with open(json_filename, 'r') as json_file:
            json_data = json.load(json_file)
    else:
        json_data = {}

    # Update the JSON data with the extracted sections
    json_data['sections'] = sections_as_dicts
    json_data['meeting'] = sections_data.meeting  # Add meeting field
    json_data['document_number'] = sections_data.document_number  # Add document number field

    # Save the updated JSON data back to the file
    with open(json_filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Updated {json_filename} with sections data.")