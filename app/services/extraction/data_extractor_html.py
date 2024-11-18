import os
import pypandoc
from bs4 import BeautifulSoup
from pathlib import Path
from app.services.extraction.llm_extractor import extract_section_data


def extract_sections_llm(filename):
    """
    Convert a DOCX file to cleaned HTML, extracting <h> elements and the first 30 words from <p> elements.
    
    Args:
        filename (str): The name of the DOCX file to convert.
    
    Returns:
        tuple: A tuple containing the cleaned HTML content and the extracted sections data.
    """
    # Check if the file exists
    file_path = Path(filename)
    print(file_path)
    
      # Check if the file exists
    if not file_path.exists():
        print(f"File {filename} does not exist.")
        return None, None
    print(f"File path: {file_path}")
    print(f"File exists: {file_path.exists()}")
    print(f"File is file: {file_path.is_file()}")

    # Convert the DOCX file to HTML and get the output as a string
    try:
        html_content = pypandoc.convert_file(str(file_path), 'html')
        print(f"HTML content length: {len(html_content)}")
    except Exception as e:
        print(f"Error converting DOCX to HTML: {e}")
    return None
    
    print(str(html_content))
    # Use BeautifulSoup to parse and clean the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Create a new BeautifulSoup object to hold only <h> and filtered <p> elements
    clean_soup = BeautifulSoup("", 'html.parser')

    # Find and append <h> elements to the new soup object
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        clean_soup.append(element)

    # Find and append <p> elements that are NOT inside <table> elements
    for p in soup.find_all('p'):
        # Check if the <p> tag has an ancestor <table>
        if not p.find_parent('table'):
            # Get the text of the <p> element and split it into words
            words = p.get_text().split()
            # Limit to the first 30 words
            limited_text = ' '.join(words[:20])
            # Create a new <p> element with the limited text
            new_p = soup.new_tag('p')
            new_p.string = limited_text
            # Append the new <p> element to clean_soup
            clean_soup.append(new_p)
    
    filename_header = clean_soup.new_tag('h2')
    filename_header.string = f"Extracted from: {os.path.basename(filename)}"
    clean_soup.insert(0, filename_header)  # Insert the header at the beginning
    cleaned_html_content = str(clean_soup)

    sections_data = extract_section_data(cleaned_html_content)

    
    return  sections_data
