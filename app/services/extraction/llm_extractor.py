
from typing import List, Optional
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.extraction.schema import Sections




# Define a custom prompt to provide instructions and any additional context.
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)
# Function to extract metadata
def extract_section_data(text: str) -> Optional[Sections]:
    
    api_key = "OLjgi0vnIGbJVhSxRDukfAlTs6gX1Hzq"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "You are an expert extraction algorithm. Your task is to extract specific information from text based on predefined requirements:"

                "1. \"Meeting Name\": Extract the meeting name, which always begins with \"3GPP\" and may include a workgroup or TSG abbreviation."

                "2. \"Document Number\": Extract a single document number containing a hyphen (\"-\")."

                "3. \"Sections\": Extract sections based only on items that include:"

                    "   - \"Section Number\": Starts with a numeric character (e.g., \"1\", \"2\", \"3\", etc.). Exclude any sections where the number does not start with a numeric character or is missing."

                    "   - \"Section Title\": Present for each valid section."

                "Return each valid section as an object within the 'sections' list, where each object includes fields:"

                    "- 'section_number' (optional): The section's number, if available."

                    "- 'section_title' (optional): The section's title."

                "Additionally, return:"

                    "- 'meeting': The extracted meeting name."

                    "- 'document_number': The extracted document number."

            ),
            ("human", "{text}"),
        ]
    )

    llm = ChatMistralAI(model="mistral-large-latest", temperature=0, api_key=api_key)

    runnable = prompt | llm.with_structured_output(schema=Sections)
   
    result = runnable.invoke({"text": text})
    # Return as a list if multiple sections, or wrap in a list if a single response
    return result 