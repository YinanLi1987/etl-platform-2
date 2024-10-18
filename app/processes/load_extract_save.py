import json
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from app.processes.extract_llm import extract_metadata
from app.processes.schemas import ChangeRequestTdoc


def load_pdf(file_path):
    """
    Load a multi-page PDF file and return a Document object.
    """
    loader = PyPDFLoader(file_path=file_path)
    docs = loader.load()  # Load all pages as Document objects
    return [doc.page_content for doc in docs]  # Return the list of page contents
def chunk_pages(pages: list[str], chunk_size: int = 3) -> list[str]:
    """Chunk the list of pages into groups of specified size."""
    chunks = []
    for i in range(0, len(pages), chunk_size):
        # Combine a chunk of pages into a single string
        chunk = "\n".join(pages[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

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
    # Step 2: Chunk the PDF content
    print("Chunking PDF content...")
    chunks = chunk_pages(pdf_content, chunk_size=3)
    # Step 3: Extract metadata from each chunk
    # Load API key once (outside the loop)
  
    combined_extracted_data = ChangeRequestTdoc()  # Create an empty ChangeRequestTdoc instance
    for chunk in chunks:
        print("Extracting metadata from PDF content chunk...")
        extracted_data = extract_metadata(chunk)  # This returns structured data
        if extracted_data:
            combined_extracted_data = combined_extracted_data.copy(update=extracted_data)
    # Step 4: Save the extracted data to a JSON file
    print(f"Saving extracted data to: {output_json_path}")
    save_extracted_data(combined_extracted_data.dict(), output_json_path)
    print("Extract metadata completed successfully!")