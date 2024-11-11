import re
from datetime import datetime
from app.services.validation.val_patterns import validation_patterns



# Function to validate each field
def validate_field(field, pattern, data):
    field_value = data.get(field)  # Get the value of the field
    if field_value is None:  # If the field value is None, handle accordingly
        return False, f"Field '{field}' is missing or null."

    if isinstance(pattern, str):  # If the pattern is a string (regular expression)
        if not re.match(pattern, field_value):
            return False, f"Field '{field}' does not match the pattern: {pattern}"
        return True, ""
    elif isinstance(pattern, list):  # If the pattern is a list (allowed values)
        if not all(item in pattern for item in field_value):
            return False, f"Field '{field}' has invalid values, allowed values are: {pattern}"
        return True, ""
    else:
        if field_value is None:
            return False, f"Field '{field}' is missing or null."
        return True, ""

# Function to validate a JSON file
def validate_json(data):
    # Check each field based on requirements. Return False immediately if any validation fails.
    fields_to_check = [
        ("meeting_id", validation_patterns["meeting_id"]),
        ("meeting", validation_patterns["meeting"]),
        ("document_number", validation_patterns["document_number"]),
        ("dates", validation_patterns["dates"]),
        ("form_version", validation_patterns["form_version"]),
        ("affected_spec", validation_patterns["affected_spec"]),
        ("cr_number", validation_patterns["cr_number"]),
        ("revision", validation_patterns["revision"]),
        ("current_version", validation_patterns["current_version"]),
        ("proposed_change_affects", validation_patterns["proposed_change_affects"]),
        ("category", validation_patterns["category"]),
        ("release", int)  # For release, we expect an integer, so we check this separately
    ]

    # Check each field
    for field, pattern in fields_to_check:
        valid, error_msg = validate_field(field, pattern, data)
        if not valid:
            return False, error_msg  # Return the first invalid field and error message

    # Mandatory fields that should not be null or empty
    mandatory_fields = ["location", "title", "source_wg", "source_tsg", "work_item_code", 
                        "reason_for_change", "summary_of_change", "consequences_if_not_approved", 
                        "affected_clauses", "sections"]
    
    for field in mandatory_fields:
        if not data.get(field):
            return False, f"Mandatory field '{field}' is missing or empty."

    # Additional validation for the 'date_submitted' field (if it exists)
    try:
        if data.get("date_submitted"):
            datetime.strptime(data["date_submitted"], "%Y-%m-%d")
    except ValueError:
        return False, "Field 'date_submitted' is not in the correct format (YYYY-MM-DD)."

    return True, ""  # Return True if all validations pass
