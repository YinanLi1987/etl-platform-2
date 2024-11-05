import os
import pypandoc
from bs4 import BeautifulSoup
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
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return None, None

    # Convert the DOCX file to HTML and get the output as a string
    html_content = pypandoc.convert_file(filename, 'html')
    
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
     # Create a header with the filename
    filename_header = clean_soup.new_tag('h2')
    filename_header.string = f"Extracted from: {os.path.basename(filename)}"
    clean_soup.insert(0, filename_header)  # Insert the header at the beginning

    # Get the cleaned HTML content as text
    cleaned_html_content = str(clean_soup)
    # print(cleaned_html_content)
    # Extract section titles and numbers from the cleaned HTML using the LLM
    sections_data = extract_section_data(cleaned_html_content)
    # Print extracted sections
    #print(f"Extracted sections for {filename}:")
    #if sections_data and sections_data.sections:
    #    for section in sections_data.sections:
    #        print(f" - Section Number: {section.section_number}, Section Title: {section.section_title}")
    #else:
    #    print(f"No sections found in {filename}.")
    #print("Conversion complete.")
    #print(sections_data)
    
    return  sections_data
