import os
import subprocess
import json
import re
import pdfplumber

from app.services.extraction.data import extracted_data, pdf_patterns
from app.services.extraction.data_extractor_html import extract_sections_llm

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
    # Loop through patterns and assign matches to `data`
    for field, pattern in pdf_patterns.items():
        match = re.search(pattern, text)
        if match:
            if field == "proposed_change_affects":
                options_line = match.group(1).strip()
                options = options_line.split()
                checked_options = []
                for i in range(len(options)):
                    if 'X' in options[i]:
                        if i > 0:
                            checked_options.append(options[i - 1]) 
                data[field] = checked_options 
            else:
                if field == "dates":
                    data[field] = match.group(2).strip()  
                else:
                    data[field] = match.group(1).strip() 

    return data


def process_file_and_update_json(input_file, converted_folder, json_folder):
    """
    Convert a DOC/DOCX file to PDF, extract data from the PDF, and save as JSON.
    """
    # Ensure output folders exist
    os.makedirs(converted_folder, exist_ok=True)
    os.makedirs(json_folder, exist_ok=True)

    # Convert DOCX file to PDF
    pdf_path = convert_to_pdf_with_unoconv(input_file, converted_folder)
    if pdf_path is None:
        return  # Exit if conversion failed

    # Extract text from the converted PDF
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Extract data from text
    data = extract_data_from_pdf(text)

    # Save extracted data to JSON
    json_filename = os.path.splitext(os.path.basename(input_file))[0] + ".json"
    json_path = os.path.join(json_folder, json_filename)
    with open(json_path, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Processed {input_file} and saved to {json_filename}")
    # Update JSON with sections data extracted from the DOCX file
    update_json_with_sections(json_path, input_file)



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

    # Save the updated JSON data back to the file
    with open(json_filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Updated {json_filename} with sections data.")