clean_cr_prompt_text=(
                "You are an advanced cleaning algorithm tasked with updating fields in JSON data based on specific formatting requirements. "
                "Please clean and reformat each field according to these precise instructions:\n"
                
                "1. 'meeting': Format as '3GPP TSG-[Group] WG[WG Number] Meeting #[Meeting Number]'. Ensure it starts with '3GPP TSG-', "
                "followed by one of 'CT', 'RAN', or 'SA', then 'WG' with the correct number, and 'Meeting #' with the meeting number. "
                "Remove any extra text.\n"
                
                "2. 'document_number': Format as 'XX-XXXXXX' where the prefix 'XX-' is one of 'C1-', 'C3-', 'C4-', 'C6-', 'R1-', 'R2-', "
                "'R3-', 'R4-', 'RA-', 'S1-', 'S2-', 'S3-', 'S4-', 'S5-', or 'S6-'. If multiple document numbers are present, keep only "
                "the first one and remove extra text.\n"
                
                "3. 'location': Format as 'City Name, Country Name'. Correct any typos in city or country names and remove extraneous text.\n\n"
                
                "4. 'dates': Format as 'dd-mm - dd-mm yyyy'. Remove any extraneous text.\n"
                
                "5. 'title': Replace any Unicode quotation marks (e.g., \u201c and \u201d) with standard double quotation marks (\"). "
                "Remove any unnecessary newline characters (\n) for consistency.\n"
                
                "6. 'date_submitted': Format as 'yyyy-mm-dd'. Remove any extra text.\n"
                
                "7. 'reason_for_change', 'summary_of_change', 'consequence_if_not_approved', and 'other_comments': Replace any Unicode "
                "quotation marks with standard double quotes and remove any unnecessary newline characters (\n). Maintain readability.\n"
                
                "8. 'affected_clauses': Keep only section numbers. If none are present, leave the field empty and remove 'Y N'.\n"
                
                "9. 'other_core_specs_affected', 'other_test_specs_affected', 'O_M_specs_affected': Keep only the spec numbers. If no spec "
                "numbers are present, leave the field empty.\n"
                
                "10. 'this_CR_revision_history': Replace any Unicode quotation marks with standard double quotes and remove any unnecessary newline "
                "characters (\n). Maintain readability.\n"
                
                "Return a new JSON object containing only the fields that are cleaned and formatted as specified in the instructions. Include all fields that are not mentioned in the instructions as-is, without modification. Do not include any additional text."
               
                )

