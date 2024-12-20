
extracted_data = {
    "meeting_id":None,
    "meeting": None,
    "document_number": None,
    "location": None,
    "dates": None,
    "form_version": None,
    "affected_spec": None,
    "cr_number": None,
    "revision": None,
    "current_version": None,
    "proposed_change_affects": None,
    "title": None,
    "source_wg": None,
    "source_tsg": None,
    "work_item_code": None,
    "date_submitted": None,
    "category": None,
    "release": None,
    "reason_for_change": None,
    "summary_of_change": None,
    "consequences_if_not_approved": None,
    "affected_clauses": None,
    "other_core_specs_affected": None,
    "other_test_specs_affected": None,
    "other_o_m_specs_affected": None,
    "other_comments": None,
    "this_CR_revision_history": None,
    "sections": [],
    "change_links":[],
  
}

pdf_patterns = {
        
        "meeting": r"(3GPP TSG-[^\s]+(?: [A-Za-z0-9]+)? Meeting #\s*\d+)\s+(R\d+-\d+)",
        "document_number": r"Meeting #\s*\d+\s+(R\d+-\d+)",
        "location": r"([A-Za-z\s]+,\s[A-Za-z\s]+)",  
        "dates": r"([A-Za-z\s]+,\s[A-Za-z\s]+),\s*(.*)(?=\s*CR-Form)",
        "form_version": r"CR-Form\s*[-–]?\s*v?\s*(\d+\.\d+)", 
        "affected_spec": r"(\d{2}\.\d{3})\s+CR",
        "cr_number": r"CR\s*(\d+)",  
        "revision": r"rev\s*\s*([\d-]*)",
        "current_version": r"Current version:\s+([\d.]+)",
        "proposed_change_affects": r"Proposed change\s+affects:\s+(.*)",
        "title":r"Title:\s+([\s\S]*?)(?=Source to WG)",
        "source_wg": r"Source to WG:\s+([\s\S]*?)(?=Source to TSG)",
        "source_tsg": r"Source to TSG:\s+([\s\S]*?)(?=Work item code)",
        "work_item_code": r"Work item code\s*:\s+([\s\S]*?)(?=Date)",
        "date_submitted": r"Date:\s*(\d{4}-\d{2}-\d{2})",
        "category": r"Category:\s+(\w+)",
        "release": r"Release:\s+Rel-(\d+)",
        "reason_for_change": r"Reason for change:\s+([\s\S]+?)(?=Summary of change)",
        "summary_of_change": r"Summary of change\s*:\s*([\s\S]+?)(?=Consequences if not)",
        "consequences_if_not_approved": r"Consequences if not\s*([\s\S]+?)(?=Clauses affected)",
        "affected_clauses": r"Clauses affected:\s*([\s\S]+?)(?=Other specs)",
        "other_core_specs_affected": r"Other core specifications\s+([\s\S]+?)(?=Test specifications|O&M Specifications|$)",
        "other_test_specs_affected": r"Test specifications\s+([\s\S]+?)(?=O&M Specifications|$)",
        "other_o_m_specs_affected": r"O&M Specifications\s+([\s\S]+?)(?=$|Other comments:)",
        "other_comments": r"Other comments:\s+([\s\S]+?)(?=This CR's revision history)",
        "this_CR_revision_history":r"This CR's revision history:\s+([\s\S]+?)(?=hange)"
    }