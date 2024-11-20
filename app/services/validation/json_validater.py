import re
from app.services.validation.val_patterns import validation_patterns

# Function to validate a field
def validate_field(field, pattern, data):
    """
    Validates that a field exists and matches the specified pattern.
    """
    field_value = data.get(field)
    if field_value is None:  # Check if the field is missing or null
        return False, f"Field '{field}' is missing or null."

    if not re.match(pattern, field_value):  # Validate against the regex pattern
        return False, f"Field '{field}' does not match the pattern: {pattern}"

    return True, ""

# Function to validate a JSON file
def validate_json(data):
    """
    Validates that `meeting_id` and `cr_number` are present and valid.
    """
    fields_to_check = [
        ("meeting_id", validation_patterns["meeting_id"]),
        ("cr_number", validation_patterns["cr_number"]),
    ]

    # Check only meeting_id and cr_number
    for field, pattern in fields_to_check:
        valid, error_msg = validate_field(field, pattern, data)
        if not valid:
            return False, error_msg  # Return the first invalid field and error message

    return True, ""  # Return True if both fields are valid
