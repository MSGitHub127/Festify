"""Algorithmic category budget allocation, cost variance, and optimization engine."""
from __future__ import annotations

from app.models import BudgetBreakdown, CategoryBudget, EventType

# Proven industry standard benchmark allocations per event type
BUDGET_ALLOCATION_PROFILES: dict[str, list[dict]] = {
    EventType.WEDDING.value: [
        {
            "category": "Venue & Catering",
            "percentage": 0.45,
            "items": ["Venue hire / reception hall", "Passed appetizers & dinner plates", "Bar package & bartenders", "Cake & dessert table"],
        },
        {
            "category": "Photography & Videography",
            "percentage": 0.12,
            "items": ["Full-day primary shooter", "Second photographer for ceremony", "Highlight reel & raw footage", "Online digital gallery"],
        },
        {
            "category": "Music & Entertainment",
            "percentage": 0.10,
            "items": ["Live ceremony musicians", "Reception DJ / MC & sound system", "Wireless microphones for speeches", "Dance floor lighting"],
        },
        {
            "category": "Attire & Beauty",
            "percentage": 0.10,
            "items": ["Wedding gown / suit / tuxedo", "Hair & makeup for bridal party", "Alterations & accessories", "Day-of touchup kit"],
        },
        {
            "category": "Floral & Decor",
            "percentage": 0.08,
            "items": ["Bridal bouquet & boutonnieres", "Ceremony arch & altar florals", "Table centerpieces & candles", "Linens & chair rentals"],
        },
        {
            "category": "Stationery & Favors",
            "percentage": 0.05,
            "items": ["Save the dates & invitations", "RSVP tracking & postage", "Welcome signs & seating chart", "Personalized guest favors"],
        },
        {
            "category": "Emergency Contingency Buffer",
            "percentage": 0.10,
            "items": ["Overtime vendor buffer", "Weather backup tent deposits", "Unexpected extra guest plates", "Last-minute tip cash"],
        },
    ],
    EventType.BIRTHDAY.value: [
        {
            "category": "Catering & Signature Cake",
            "percentage": 0.35,
            "items": ["Custom multi-tier birthday cake", "Buffet or plated meal service", "Non-alcoholic & cocktail refreshments", "Party snack stations"],
        },
        {
            "category": "Venue & Activity Space",
            "percentage": 0.30,
            "items": ["Private room or hall rental", "Setup & breakdown fee", "Table & chair arrangements", "Audio-visual screen for retrospectives"],
        },
        {
            "category": "Entertainment & Games",
            "percentage": 0.15,
            "items": ["DJ or curated sound playlist", "Interactive party games / host", "Photo booth with custom props", "Specialty performer / magician"],
        },
        {
            "category": "Theme Decor & Favors",
            "percentage": 0.10,
            "items": ["Balloon arch & photo backdrop", "Custom signage & milestone posters", "Themed table runners & tableware", "Personalized gift bags"],
        },
        {
            "category": "Emergency Contingency Buffer",
            "percentage": 0.10,
            "items": ["Extra food / drink top-ups", "Overtime room rental buffer", "Replacement supplies", "Vendor tipping"],
        },
    ],
    EventType.COMMUNITY.value: [
        {
            "category": "Venue & Municipal Park Permits",
            "percentage": 0.25,
            "items": ["City park or plaza permit", "Amplified sound variance permit", "Insurance rider & event bond", "Restroom trailer rentals"],
        },
        {
            "category": "Sound, Stage & Production",
            "percentage": 0.25,
            "items": ["Covered stage & rigging", "PA sound system & wireless mics", "Stage lighting & power generators", "AV tech support operator"],
        },
        {
            "category": "Public Safety, Security & Sanitation",
            "percentage": 0.15,
            "items": ["Certified crowd safety officers", "First aid tent & paramedic standby", "Trash/recycling bins & hauling", "Crowd barricades & cones"],
        },
        {
            "category": "Signage, Marketing & Volunteer Ops",
            "percentage": 0.15,
            "items": ["Wayfinding banners & maps", "Volunteer t-shirts & lanyards", "Digital promotion & community flyers", "Information booth booth kit"],
        },
        {
            "category": "Hospitality & Refreshments",
            "percentage": 0.10,
            "items": ["Water hydration stations", "Volunteer meal vouchers", "Performer green room snacks", "Coffee & continental supplies"],
        },
        {
            "category": "Emergency Contingency Buffer",
            "percentage": 0.10,
            "items": ["Inclement weather supplies", "Emergency equipment repair", "City overtime inspection buffer", "Unexpected logistical supplies"],
        },
    ],
}

COST_SAVING_TIPS: dict[str, list[str]] = {
    EventType.WEDDING.value: [
        "Select seasonal native flowers (e.g. garden roses or greenery) instead of out-of-season imports to save up to 25% on floral budgets.",
        "Consider an off-peak day (Friday or Sunday) or shoulder-season month (April, November) for 15–30% venue hire discounts.",
        "Opt for a signature cocktail duo plus beer and wine rather than a full open bar to reduce liquor waste and per-head bar costs.",
        "Use digital RSVP portals with QR codes on elegant printed invitations to cut printing, paper, and postage costs in half.",
    ],
    EventType.BIRTHDAY.value: [
        "Host the event between 14:00 and 17:00 for an afternoon dessert-and-cocktail reception rather than a full three-course dinner.",
        "Create a DIY balloon installation and digital photo backdrop using Canva and portable ring lights instead of hiring external prop companies.",
        "Bundle entertainment by hiring a multi-talented MC who doubles as a DJ and activity host.",
    ],
    EventType.COMMUNITY.value: [
        "Partner with local food trucks that pay a vendor pitch fee or provide their own power, turning catering from a cost into an income stream.",
        "Recruit community college and high school volunteer service clubs for setup and recycling in exchange for service hour certifications.",
        "Seek corporate sponsorship from local credit unions or businesses in exchange for logo placement on stage banners and volunteer apparel.",
    ],
}


def generate_budget_breakdown(event_type: str, total_budget: float, guest_count: int) -> BudgetBreakdown:
    """Calculate mathematically balanced category allocations, per-guest numbers, and savings tips.

    Args:
        event_type: Category identifier ('wedding', 'birthday', 'community').
        total_budget: Total target budget ceiling in USD.
        guest_count: Expected headcount of attendees.

    Returns:
        BudgetBreakdown: Complete breakdown with percentages, amounts, contingency, and tips.
    """
    profile = BUDGET_ALLOCATION_PROFILES.get(event_type.lower(), BUDGET_ALLOCATION_PROFILES[EventType.WEDDING.value])
    categories: list[CategoryBudget] = []
    contingency = 0.0

    safe_guests = max(1, guest_count)
    cost_per_guest = round(total_budget / safe_guests, 2)

    for p in profile:
        allocated = round(total_budget * p["percentage"], 2)
        per_guest = round(allocated / safe_guests, 2)
        if "Contingency" in p["category"]:
            contingency = allocated

        categories.append(
            CategoryBudget(
                category=p["category"],
                percentage=round(p["percentage"] * 100, 1),
                allocated_amount=allocated,
                per_guest_amount=per_guest,
                recommended_items=p["items"],
            )
        )

    tips = COST_SAVING_TIPS.get(event_type.lower(), COST_SAVING_TIPS[EventType.WEDDING.value])

    return BudgetBreakdown(
        total_budget=total_budget,
        guest_count=guest_count,
        cost_per_guest=cost_per_guest,
        contingency_buffer=contingency,
        categories=categories,
        cost_saving_tips=tips,
    )


def analyze_budget_variance(allocated: float, actual: float) -> dict[str, str | float]:
    """Calculate variance between allocated budget and vendor quote/invoice.

    Args:
        allocated: The budgeted baseline ceiling in USD.
        actual: The actual quote or invoice amount from the vendor in USD.

    Returns:
        dict[str, str | float]: Variance metrics including difference, percent, status, and alert message.
    """
    diff = round(actual - allocated, 2)
    percent_diff = round((diff / allocated * 100), 1) if allocated > 0 else 0.0

    if diff > 0:
        status = "over_budget"
        alert = f"Quote exceeds allocation by ${diff:,.2f} ({percent_diff:+.1f}%). Suggest reallocating from contingency."
    elif diff < 0:
        status = "under_budget"
        alert = f"Quote is under allocation by ${abs(diff):,.2f} ({abs(percent_diff):.1f}% savings). Can boost decor or savings."
    else:
        status = "on_target"
        alert = "Quote matches allocated budget exactly."

    return {
        "allocated": allocated,
        "actual": actual,
        "difference": diff,
        "percent_variance": percent_diff,
        "status": status,
        "alert": alert,
    }
