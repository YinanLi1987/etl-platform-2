import os
import json
from app.services.transformation.llm_cleaner import clean_cr_json_llm  # Ensure this function is correctly imported

def clean_json_cr(input_folder, output_folder):
  
    print(input_folder)
    # Iterate through each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Open and read the JSON file
            with open(input_path, 'r') as f:
                try:
                    original_data = json.load(f)
                    #print(original_data)
             
                except json.JSONDecodeError as e:
                    print(f"Error reading {filename}: {e}")
                    continue

            # Use the cleaning function to process the data
            result = clean_cr_json_llm(original_data)
            result_lines = result.splitlines()
            result_lines = result_lines[1:-1]  # Remove the first and last line
    
            # Join the lines back together
            cleaned_result = "\n".join(result_lines)
       

            # Save cleaned data to the output folder
            with open(output_path, 'w') as f:
                f.write(cleaned_result) 

            print(f"Processed and saved cleaned JSON to {output_path}")