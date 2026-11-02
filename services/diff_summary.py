"""Service layer for Git diff summarization."""

import logging
from typing import Optional
from models.base import BaseModelProvider
from models.gemini import GeminiProvider
from models.schemas import PRSummary
from prompts.diff_summary import DIFF_SYSTEM_INSTRUCTION, build_diff_summary_prompt
from services.core.config import settings

logger = logging.getLogger("services.diff_summary")


class DiffValidationError(ValueError):
    """Base exception for diff validation errors."""
    pass


class DiffEmptyError(DiffValidationError):
    """Raised when the provided diff is empty or whitespace-only."""
    pass


class DiffSizeLimitExceededError(DiffValidationError):
    """Raised when the provided diff exceeds the maximum allowed character limit."""
    pass


class DiffSummaryService:
    """Orchestrates diff validation, prompt formatting, and structured summary generation."""

    def __init__(
        self,
        provider: Optional[BaseModelProvider] = None,
        max_diff_size: Optional[int] = None,
    ):
        self.provider = provider or GeminiProvider()
        self.max_diff_size = max_diff_size if max_diff_size is not None else settings.MAX_DIFF_SIZE_CHARS

    async def summarize_diff(
        self,
        diff: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> PRSummary:
        """Validates the input diff, constructs the prompt, and generates a PRSummary.

        Security note: Diff text, API keys, or raw provider response bodies are NEVER logged.
        """
        if not diff or not diff.strip():
            logger.warning("Diff summarization rejected: diff is empty or whitespace")
            raise DiffEmptyError("Diff content cannot be empty.")

        diff_len = len(diff)
        if diff_len > self.max_diff_size:
            logger.warning(
                "Diff summarization rejected: diff length (%d characters) exceeds limit (%d)",
                diff_len,
                self.max_diff_size,
            )
            raise DiffSizeLimitExceededError(
                f"Diff size ({diff_len} characters) exceeds maximum allowed limit of {self.max_diff_size} characters."
            )

        logger.info("Building diff summary prompt for diff of length: %d characters", diff_len)
        prompt = build_diff_summary_prompt(
            diff=diff,
            title=title,
            description=description,
            branch=branch,
        )

        logger.info("Invoking AI model provider for structured diff summary")
        summary = await self.provider.generate_structured(
            prompt=prompt,
            system_instruction=DIFF_SYSTEM_INSTRUCTION,
            response_schema=PRSummary,
        )
        logger.info("Successfully generated structured PR summary")
        return summary
