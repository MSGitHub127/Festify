"""Abstract LLM Provider interface and provider factory."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.config import get_settings
from app.models import BudgetBreakdown, CreativeIdeas


class LLMProvider(ABC):
    @abstractmethod
    def generate_ideas(self, event_type: str, vibe_theme: str | None = None) -> CreativeIdeas:
        """Generate creative themes, dietary-inclusive menus, and speech drafts."""

    @abstractmethod
    def answer_event_query(self, question: str, context: str) -> str:
        """Answer planner or client questions grounded in event context."""

    @abstractmethod
    def optimize_budget(self, event_type: str, total_budget: float, guest_count: int) -> BudgetBreakdown:
        """Produce an optimized, mathematically sound budget allocation."""

    @abstractmethod
    def extract_from_image(self, image_bytes: bytes, mime_type: str) -> str:
        """Extract event details from an uploaded venue contract or invitation image."""


def get_llm_provider() -> LLMProvider:
    """Factory creating the configured LLM provider."""
    settings = get_settings()
    provider_name = settings.llm_provider.lower()

    if provider_name == "anthropic" and settings.anthropic_api_key:
        from app.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)

    from app.llm.mock_provider import MockProvider

    return MockProvider()
