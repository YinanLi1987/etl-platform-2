import json
from langchain_community.document_loaders import PyPDFLoader
from app.processes.extract_llm import extract_metadata

def load_pdf(file_path):
    """
    Load a multi-page PDF file and return a Document object.
    """
    loader = PyPDFLoader(file_path=file_path)
    docs = loader.load()  # Load all pages as Document objects
    # Combine the page contents into a single string
    full_content = "\n".join(doc.page_content for doc in docs)
    print(full_content)
    return full_content  # Return the list of Document objects (or you can modify to return as needed)

def save_extracted_data(data, json_file_path):
    """
    Save the extracted data to a JSON file.
    """
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def load_extract_save_data(input_pdf_path,output_json_path):
    # Step 1: Load PDF content
    print(f"Loading PDF content from: {input_pdf_path}")
    pdf_content = load_pdf(input_pdf_path)
    # Step 2: Extract metadata from the content using LLM
    print("Extracting metadata from PDF content...")
    extracted_data = extract_metadata(pdf_content)  # This returns structured data
       # Step 3: Save the extracted data to a JSON file
    print(f"Saving extracted data to: {output_json_path}")
    save_extracted_data(extracted_data, output_json_path)
    print("Extract metadata completed successfully!")