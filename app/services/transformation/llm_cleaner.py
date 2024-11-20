
import json
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import concurrent.futures
from app.services.transformation.cleaner_cr_prompt import clean_cr_prompt_text



def clean_cr_json_llm(json_data, timeout=120):
    # Load JSON data from file
 
    
    # Convert JSON data to a pretty-printed string
    text = json.dumps(json_data, indent=2)
    
    # Configure model and prompt
    api_key = os.getenv('MISTRALAI_API_KEY')
    model = ChatMistralAI(model="mistral-large-latest", temperature=0, api_key=api_key, timeout=120)
    parser = StrOutputParser()
    
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", clean_cr_prompt_text),
            ("human", "{text}"),
        ]
    )
    
    # Build and execute the chain
    chain = prompt_template | model | parser
    # Invoke the chain with a timeout
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(chain.invoke, {"text": text})
            result = future.result(timeout=timeout)
            return result
    except concurrent.futures.TimeoutError:
        print("Timeout occurred while invoking the model")
        return None
    except Exception as e:
        print(f"Error during model invocation: {e}")
        return None