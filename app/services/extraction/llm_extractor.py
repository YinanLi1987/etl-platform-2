
from typing import List, Optional
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.extraction.schema import Sections



# Define a custom prompt to provide instructions and any additional context.
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)
# Function to extract metadata
def extract_section_and_meeting_documentNum_data(text: str) -> Optional[Sections]:
    
    api_key = "OLjgi0vnIGbJVhSxRDukfAlTs6gX1Hzq"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. Extract only sections with a 'section number' "
                "and a 'section title'. The 'section number' must start with a numeric character, "
                "such as 1, 2, 3, etc. If a 'section number' is missing or does not start with a "
                "numeric character, exclude that item from the extraction. "
                "Return each valid section as an object in the 'sections' list, with 'section_number' "
                "and 'section_title' fields.",
            ),
            ("human", "{text}"),
        ]
    )

    llm = ChatMistralAI(model="mistral-large-latest", temperature=0, api_key=api_key)

    runnable = prompt | llm.with_structured_output(schema=Sections)
    result = runnable.invoke({"text": text})
     # Return as a list if multiple sections, or wrap in a list if a single response
    return result 