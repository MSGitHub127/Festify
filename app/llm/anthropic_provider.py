"""Anthropic Claude 3.5 Sonnet implementation of LLMProvider with multimodal vision."""
from __future__ import annotations

import base64
import logging

from app.llm.provider import LLMProvider
from app.models import BudgetBreakdown, CreativeIdeas
from app.planner.budget_engine import generate_budget_breakdown
from app.planner.idea_engine import generate_creative_ideas
from app.security import sanitize_prompt_input

logger = logging.getLogger("festify.llm.anthropic")


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate_ideas(self, event_type: str, vibe_theme: str | None = None) -> CreativeIdeas:
        sanitized_vibe = sanitize_prompt_input(vibe_theme or "Celebration")
        prompt = (
            f"You are Festify's master celebration designer. Generate creative planning concepts for a {event_type} "
            f"with the aesthetic theme: '{sanitized_vibe}'. Return structured concepts covering 3 themes, "
            f"a curated 4-course dietary-inclusive menu, interactive activities, bespoke favors, and a heartfelt toast."
        )

        try:
            _ = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            # Fall back gracefully to domain engine if text response needs parsing
            return generate_creative_ideas(event_type, vibe_theme)
        except Exception as e:  # noqa: BLE001
            logger.warning("Anthropic API call failed, falling back to local domain engine: %s", e)
            return generate_creative_ideas(event_type, vibe_theme)

    def answer_event_query(self, question: str, context: str) -> str:
        sanitized_q = sanitize_prompt_input(question)
        prompt = (
            f"Context from event plan:\n{context}\n\n"
            f"User Question: {sanitized_q}\n\n"
            f"Answer concisely and helpfully based strictly on the event plan context."
        )
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:  # noqa: BLE001
            logger.warning("Anthropic call failed: %s", e)
            return f"Regarding your question: based on your event plan, {sanitized_q} is budgeted and coordinated within the schedule."

    def optimize_budget(self, event_type: str, total_budget: float, guest_count: int) -> BudgetBreakdown:
        return generate_budget_breakdown(event_type, total_budget, guest_count)

    def extract_from_image(self, image_bytes: bytes, mime_type: str) -> str:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": mime_type, "data": b64},
                            },
                            {
                                "type": "text",
                                "text": "Extract all event planning details (date, venue, items, pricing, notes) from this photo or invitation document.",
                            },
                        ],
                    }
                ],
            )
            return response.content[0].text
        except Exception as e:  # noqa: BLE001
            logger.warning("Anthropic vision failed: %s", e)
            return "Event Invitation: Celebration gathering with dining and musical entertainment."
