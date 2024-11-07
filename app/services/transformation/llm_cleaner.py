
import json
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.services.transformation.cleaner_cr_prompt import clean_cr_prompt_text



def clean_cr_json_llm(json_data):
    # Load JSON data from file
 
    
    # Convert JSON data to a pretty-printed string
    text = json.dumps(json_data, indent=2)
    
    # Configure model and prompt
    api_key = "OLjgi0vnIGbJVhSxRDukfAlTs6gX1Hzq"
    model = ChatMistralAI(model="mistral-large-latest", temperature=0, api_key=api_key)
    parser = StrOutputParser()
    
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", clean_cr_prompt_text),
            ("human", "{text}"),
        ]
    )
    
    # Build and execute the chain
    chain = prompt_template | model | parser
    result = chain.invoke({"text": text})

    return result 