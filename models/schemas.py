from typing import List, Optional
from pydantic import BaseModel, Field

class PRSummary(BaseModel):
    """Represents a structured pull request description output."""
    summary: str = Field(description="A concise 1-2 sentence overview of what changed and why.")
    key_changes: List[str] = Field(description="A list of bullet points detailing the functional changes.")
    review_focus: List[str] = Field(description="Key files, functions, or modules that need critical review.")

class DiffSummaryRequest(BaseModel):
    """Request payload for Git diff summarization."""
    diff: str = Field(
        ...,
        description="The unified Git diff content to summarize. Must not be empty and cannot exceed the configured maximum size."
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional title of the pull request or commit to provide additional context."
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional existing description or context for the changes."
    )
    branch: Optional[str] = Field(
        default=None,
        description="Optional source or target branch name."
    )
