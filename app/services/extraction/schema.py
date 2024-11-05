from pydantic import BaseModel,Field
from typing import Optional, List


class Section(BaseModel):
    """Schema for dynamic sections with uncertain numbers and titles."""
    section_number: Optional[str] = Field(default=None, description="The number of the section, if present")
    section_title: Optional[str] = Field(default=None, description="The title of the section")
# Define a Sections wrapper model to handle multiple sections
class Sections(BaseModel):
    sections: List[Section]
    meeting: Optional[str] = Field(default=None, description="The name of the meeting")
    document_number: Optional[str] = Field(default=None, description="The document number, if available")