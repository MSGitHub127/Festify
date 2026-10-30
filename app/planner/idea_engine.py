"""Creative personalization engine: cohesive themes, color palettes, dietary menus, and speech drafting."""
from __future__ import annotations

from app.models import CreativeIdeas, EventType, MenuItem, SpeechDraft, ThemeConcept

THEME_TEMPLATES: dict[str, list[dict]] = {
    EventType.WEDDING.value: [
        {
            "name": "Ethereal Botanical Glasshouse",
            "tagline": "Lush romantic greenery meets modern clean architectural glass",
            "description": "An intimate, candlelit celebration framed by climbing ivy, white garden roses, warm bistro lighting, and minimalist brass accents.",
            "color_palette": ["#134B46", "#F4F7F2", "#B8977E", "#2B3A42", "#E8D8C8"],
            "decor_accents": ["Smoked glass votives", "Wild eucalyptus table runners", "Handmade deckled-edge stationery", "Suspended floral chandeliers"],
        },
        {
            "name": "Mid-Century Modern Terracotta",
            "tagline": "Warm desert neutrals with geometric vintage sophistication",
            "description": "Vibrant earthy tones featuring architectural dried palms, rust linens, velvet lounge furniture, and retro cocktail service.",
            "color_palette": ["#A64B2A", "#D7A86E", "#F8F1EB", "#3C2A21", "#7E634E"],
            "decor_accents": ["Terracotta urns with pampas grass", "Rattan bar carts", "Retro vinyl record guestbook", "Amber glassware"],
        },
        {
            "name": "Midnight Celestial Elegance",
            "tagline": "Moody deep navy velvet with constellation gold leaf accents",
            "description": "A dramatic nighttime celebration under fairy-light canopies, dark floral arrangements, and gold foil celestial table numbers.",
            "color_palette": ["#0F172A", "#1E293B", "#F8FAFC", "#D4AF37", "#475569"],
            "decor_accents": ["Fairy-light curtain backdrop", "Gold dipped flatware", "Constellation map seating chart", "Smoky dry ice cocktails"],
        },
    ],
    EventType.BIRTHDAY.value: [
        {
            "name": "Vintage Golden Hour Speakeasy",
            "tagline": "Jazz era glamour with craft mixology and intimate lounge vibes",
            "description": "A sophisticated milestone celebration featuring prohibition cocktails, jazz vinyl, leather chesterfield lounges, and vintage polaroid stations.",
            "color_palette": ["#1E1E1E", "#B8860B", "#FDFBF7", "#4A0E17", "#8C7853"],
            "decor_accents": ["Art deco gold signage", "Custom monogrammed cocktail napkins", "Vintage cigar & chocolate bar", "Brass candleholders"],
        },
        {
            "name": "Neon Cyberpunk Sunset",
            "tagline": "Electric futuristic energy with high-contrast immersive lights",
            "description": "An energetic party powered by synthwave beats, reactive neon LED lighting tubes, glow cocktails, and interactive arcade games.",
            "color_palette": ["#0D0221", "#FF007F", "#00F0FF", "#FFE600", "#7122FA"],
            "decor_accents": ["Custom neon name sign", "Glow-in-the-dark cocktail garnishes", "Retro arcade station", "Holographic party favors"],
        },
        {
            "name": "Mediterranean Coastal Garden",
            "tagline": "Sun-drenched citrus, terracotta, and crisp coastal linens",
            "description": "A relaxed, joyous daytime gathering inspired by the Amalfi Coast, featuring Aperol spritz carts, fresh lemons, and rustic olive oil tasting.",
            "color_palette": ["#1A508B", "#FFD166", "#FAF9F6", "#06D6A0", "#EF476F"],
            "decor_accents": ["Fresh lemon & olive branch garlands", "Painted ceramic tile placecards", "Aperol spritz fountain", "Striped blue linen umbrellas"],
        },
    ],
    EventType.COMMUNITY.value: [
        {
            "name": "Harvest & Heritage Community Fair",
            "tagline": "Celebrating local agriculture, artisanal crafts, and neighborhood roots",
            "description": "A wholesome open-air gathering with rustic wooden booth stalls, local farm fresh produce tastings, bluegrass music, and hay bale seating.",
            "color_palette": ["#2D5A27", "#C87D55", "#F7F5EB", "#8B4513", "#D2B48C"],
            "decor_accents": ["Burlap bunting banners", "Chalkboard wayfinding signs", "Wildflower mason jars", "Produce display crates"],
        },
        {
            "name": "Unity in Rhythm Multicultural Festival",
            "tagline": "Global music, dance, and vibrant shared culinary traditions",
            "description": "A celebration of diversity featuring international food pavilions, world music percussion circles, collaborative chalk murals, and folk dance workshops.",
            "color_palette": ["#800020", "#FFB703", "#023047", "#219EBC", "#FB8500"],
            "decor_accents": ["World flag streamers", "Interactive community wish tree", "Handmade textile tapestries", "Illuminated lantern archways"],
        },
        {
            "name": "Eco-Green Neighborhood Block Jam",
            "tagline": "Zero-waste sustainability, local acoustic music, and green workshops",
            "description": "A family-friendly festival focused on community resilience, solar-powered sound stages, plant-swap booths, and reusable cup loan stations.",
            "color_palette": ["#1B4332", "#40916C", "#D8F3DC", "#B7E4C7", "#2D6A4F"],
            "decor_accents": ["Recycled pallet wood furniture", "Native seed packet favors", "Solar fairy light jars", "Chalk art hopscotch zones"],
        },
    ],
}

MENU_TEMPLATES: dict[str, list[dict]] = {
    EventType.WEDDING.value: [
        {"course": "Hors d'oeuvres", "item_name": "Crispy Wild Mushroom Arancini with Truffle Aioli", "dietary_tags": ["Vegetarian"], "pairing": "Prosecco DOCG"},
        {"course": "Appetizer", "item_name": "Burrata with Heirloom Tomatoes & Basil Emulsion", "dietary_tags": ["Vegetarian", "Gluten-Free"], "pairing": "Sauvignon Blanc"},
        {"course": "Entrée (Meat)", "item_name": "Braised Short Rib with Parsnip Puree & Red Wine Demi-Glace", "dietary_tags": ["Gluten-Free", "Halal"], "pairing": "Cabernet Sauvignon"},
        {"course": "Entrée (Plant-Based)", "item_name": "Pan-Seared King Oyster Mushroom 'Scallops' with Cauliflower Cream", "dietary_tags": ["Vegan", "Gluten-Free", "Nut-Free"], "pairing": "Chardonnay"},
        {"course": "Dessert", "item_name": "Vanilla Bean Sponge Cake with Raspberry Coulis & Macarons", "dietary_tags": ["Vegetarian"], "pairing": "Late Harvest Riesling"},
    ],
    EventType.BIRTHDAY.value: [
        {"course": "Welcome Bite", "item_name": "Artisanal Flatbreads (Fig & Prosciutto / Roast Pepper & Vegan Cheese)", "dietary_tags": ["Dairy-Free Option", "Vegan Option"], "pairing": "Sparkling Rosé"},
        {"course": "Main Feast", "item_name": "Sliders & Skewer Bar (Wagyu Beef, Chimichurri Chicken, and BBQ Jackfruit)", "dietary_tags": ["Halal", "Vegan Option", "Gluten-Free Option"], "pairing": "Craft Hazy IPA / Mocktails"},
        {"course": "Celebration Dessert", "item_name": "Decadent Valrhona Chocolate Mousse Cake with Gold Leaf", "dietary_tags": ["Vegetarian"], "pairing": "Espresso Martinis"},
    ],
    EventType.COMMUNITY.value: [
        {"course": "Street Food Pavilion", "item_name": "Baja Fish & Crispy Cauliflower Street Tacos with Fresh Slaw", "dietary_tags": ["Gluten-Free", "Vegan Option", "Dairy-Free"], "pairing": "Agua Fresca"},
        {"course": "Comfort Corner", "item_name": "Fire-Roasted Corn on the Cob with Lime & Cotija Cheese", "dietary_tags": ["Vegetarian", "Gluten-Free"], "pairing": "Local Apple Cider"},
        {"course": "Community Treat", "item_name": "Artisan Gelato & Fresh Berry Sorbet Cups", "dietary_tags": ["Vegan Option", "Gluten-Free"], "pairing": "Fresh Lemonade"},
    ],
}

ACTIVITIES: dict[str, list[str]] = {
    EventType.WEDDING.value: [
        "Interactive Audio Guestbook: Guests pick up a vintage rotary telephone to record voicemail heartfelt congratulations.",
        "The Shoe Game: Couple sits back-to-back testing who knows who better with humorous audience prompts.",
        "Late-Night Vinyl Lounge: Cozy lounge corner with a turntable where guests choose records to spin.",
        "Polaroid Wall: Instant photo station where guests tape a picture alongside their personal note in the leather guestbook.",
    ],
    EventType.BIRTHDAY.value: [
        "Milestone Trivia Smackdown: High-energy multiple-choice trivia quiz hosted on guests' smartphones about the guest of honor.",
        "Custom 360-degree slow motion video booth with personalized celebration overlay graphic.",
        "Time Capsule Box: Guests write predictions or memories to be sealed and opened at the next milestone birthday.",
        "Mixology Challenge: Guests vote on their favorite custom cocktail creation from a DIY flavor garnish bar.",
    ],
    EventType.COMMUNITY.value: [
        "Collaborative Community Mural: Canvas banner where all neighborhood attendees contribute a painted tile or handprint.",
        "Local Maker Scavenger Hunt: Families complete clues visiting 5 community booths to win a local business prize basket.",
        "Open Mic Acoustic Jam: 15-minute showcase sets for local neighborhood youth bands and spoken word poets.",
        "Seed Bomb Workshop: Children mold clay and native wildflower seeds to plant in community park gardens.",
    ],
}

FAVORS: dict[str, list[str]] = {
    EventType.WEDDING.value: [
        "Miniature bottles of infused Tuscan olive oil with custom calligraphy tags.",
        "Hand-poured soy wax candles with signature wedding day scent (white amber & fig).",
        "Wildflower seed packets inscribed with 'Watch Our Love Grow'.",
        "Artisanal dark chocolate bars wrapped in custom monogram foil.",
    ],
    EventType.BIRTHDAY.value: [
        "Custom embroidered hotel keychains with party slogan and milestone date.",
        "Individually boxed gourmet French macarons in the party's color palette.",
        "Personalized travel recovery kits (hydration electrolytes, artisan mints, eye mask).",
    ],
    EventType.COMMUNITY.value: [
        "Screen-printed organic cotton tote bags designed by local student artists.",
        "Packets of non-GMO heirloom seeds for neighborhood pollinator gardens.",
        "Commemorative reusable stainless-steel festival water tumblers.",
    ],
}

SPEECHES: dict[str, dict[str, str]] = {
    EventType.WEDDING.value: {
        "speaker_role": "Host / Maid of Honor / Best Man",
        "tone": "Heartfelt, Warm & Lightly Humorous",
        "draft_text": (
            "Good evening everyone! Standing here tonight looking out at all of your smiling faces, "
            "one thing is undeniably clear: love is not just something you feel, it's something you build together every single day. "
            "To the couple: may your love always be modern enough to survive the times, and old-fashioned enough to last forever. "
            "Please raise your glasses with me to a lifetime of laughter, shared adventures, and unwavering partnership. To the newlyweds!"
        ),
    },
    EventType.BIRTHDAY.value: {
        "speaker_role": "Guest of Honor / Best Friend",
        "tone": "Celebratory, Uplifting & Nostalgic",
        "draft_text": (
            "Welcome everyone, and thank you so much for being here tonight! "
            "They say that life is not measured by the number of breaths you take, but by the moments and the people who take your breath away. "
            "Looking around this room at friends, family, and lifelong partners in crime, I couldn't feel more grateful. "
            "Here's to celebrating another year of wisdom, bold moves, and unforgettable stories. Cheers!"
        ),
    },
    EventType.COMMUNITY.value: {
        "speaker_role": "Community Director / Welcome Lead",
        "tone": "Inspiring, Welcoming & Community-Focused",
        "draft_text": (
            "Welcome to all our neighbors, families, and friends! "
            "A neighborhood isn't defined by the lines on a city map; it's defined by the people who show up for one another, "
            "share meals, create art, and make this a place where everyone belongs. "
            "Thank you to our volunteers, performers, local businesses, and each of you for making today possible. Enjoy the festival!"
        ),
    },
}


def generate_creative_ideas(event_type: str, vibe_theme: str | None = None) -> CreativeIdeas:
    """Generate cohesive creative packages: 3 complete themes, dietary menus, activities, favors, and speeches.

    Args:
        event_type: Category identifier ('wedding', 'birthday', 'community').
        vibe_theme: User-requested aesthetic or mood keyword (optional).

    Returns:
        CreativeIdeas: Packaged themes with 5-tone palettes, dietary menus, activities, and speeches.
    """
    key = event_type.lower()
    themes_raw = THEME_TEMPLATES.get(key, THEME_TEMPLATES[EventType.WEDDING.value])
    menu_raw = MENU_TEMPLATES.get(key, MENU_TEMPLATES[EventType.WEDDING.value])
    activities = ACTIVITIES.get(key, ACTIVITIES[EventType.WEDDING.value])
    favors = FAVORS.get(key, FAVORS[EventType.WEDDING.value])
    speech_dict = SPEECHES.get(key, SPEECHES[EventType.WEDDING.value])

    themes = [ThemeConcept(**t) for t in themes_raw]
    menus = [MenuItem(**m) for m in menu_raw]
    speech = SpeechDraft(**speech_dict)

    return CreativeIdeas(
        themes=themes,
        curated_menu=menus,
        entertainment_activities=activities,
        bespoke_favors=favors,
        speech_toast=speech,
    )
