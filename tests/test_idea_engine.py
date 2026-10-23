"""Tests for creative idea generation: themes, dietary menus, activities, favors, and speech drafting."""
from __future__ import annotations

from app.planner.idea_engine import generate_creative_ideas


def test_wedding_creative_ideas():
    ideas = generate_creative_ideas("wedding", "Modern Elegance")

    assert len(ideas.themes) >= 3
    for theme in ideas.themes:
        assert theme.name
        assert theme.tagline
        assert len(theme.color_palette) >= 4
        assert len(theme.decor_accents) >= 3

    assert len(ideas.curated_menu) >= 4
    # Ensure dietary options are provided
    all_dietary = [tag for m in ideas.curated_menu for tag in m.dietary_tags]
    assert "Vegetarian" in all_dietary
    assert any("Gluten-Free" in tag for tag in all_dietary)
    assert any("Vegan" in tag for tag in all_dietary)

    assert len(ideas.entertainment_activities) >= 3
    assert len(ideas.bespoke_favors) >= 3
    assert ideas.speech_toast.draft_text
    assert ideas.speech_toast.speaker_role


def test_birthday_creative_ideas():
    ideas = generate_creative_ideas("birthday", "1920s Speakeasy")

    assert len(ideas.themes) >= 3
    theme_names = [t.name for t in ideas.themes]
    assert any("Speakeasy" in n for n in theme_names)

    assert len(ideas.curated_menu) >= 3
    cake_menu = next(m for m in ideas.curated_menu if "Cake" in m.item_name)
    assert cake_menu.course == "Celebration Dessert"


def test_community_creative_ideas():
    ideas = generate_creative_ideas("community", "Harvest Festival")

    assert len(ideas.themes) >= 3
    assert len(ideas.entertainment_activities) >= 3
    assert any("Mural" in act or "Scavenger" in act for act in ideas.entertainment_activities)


def test_fallback_creative_ideas():
    ideas = generate_creative_ideas("mystery_party")
    assert len(ideas.themes) >= 3
