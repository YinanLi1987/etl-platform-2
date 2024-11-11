# Define validation patterns and allowed values
validation_patterns = {
    "meeting_id": r"^\d{4}|\d{6}$",
    "meeting": r"^3GPP .* #\d+$",
    "document_number": r"^(C[1346]-|R[1234]-|RA-|S[1-6]-)\d+$",
    "dates": r"^\d{2}/\d{2}-\d{2}/\d{2} \d{4}$",
    "form_version": r"^(5|6|6\.1|5\.1|7|7\.1|8|9(\.\d)?|10|11(\.\d)?|12(\.\d)?)|13(\.\d)?$",
    "affected_spec": r"^\d{1,2}\..+$",
    "cr_number": r"^\d{4}$",
    "revision": r"^(\d+|-)$",
    "current_version": r"^\d{1,2}\..+$",
    "proposed_change_affects": ["UICC apps", "ME", "Radio Access Network", "Core Network"],
    "category": ["F", "A", "B", "C", "D"],
}