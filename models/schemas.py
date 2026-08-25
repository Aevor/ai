from typing import List
from pydantic import BaseModel, Field

class PRSummary(BaseModel):
    """Represents a structured pull request description output."""
    summary: str = Field(description="A concise 1-2 sentence overview of what changed and why.")
    key_changes: List[str] = Field(description="A list of bullet points detailing the functional changes.")
    review_focus: List[str] = Field(description="Key files, functions, or modules that need critical review.")
