import os
import subprocess

def convert_file_service(downloads_folder, converted_folder):
    """
    Convert all DOC/DOCX files in the downloads folder to PDF
    while preserving tracked changes using unoconv.
    Returns the total count of successfully converted files.
    """
    converted_count = 0  # Initialize the count of successfully converted files

    # Loop through all files in the downloads folder
    for file_name in os.listdir(downloads_folder):
        if file_name.endswith(('.doc', '.docx')):  # Check for DOC or DOCX files
            full_file_path = os.path.join(downloads_folder, file_name)
            if convert_to_pdf_with_unoconv(full_file_path, converted_folder):
                converted_count += 1  # Increment count if conversion is successful
                print(f"{converted_count} files processed.")
    return converted_count  # Return the total count of converted files


def convert_to_pdf_with_unoconv(input_file, converted_folder):
    """
    Use unoconv (LibreOffice) to convert a DOC/DOCX file to PDF with tracked changes.
    """
    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_pdf_path = os.path.join(converted_folder, f"{name}.pdf")
    try:
        subprocess.run(['unoconv', '-f', 'pdf', '-o', output_pdf_path, input_file], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        return False