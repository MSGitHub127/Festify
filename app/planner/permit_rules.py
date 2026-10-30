"""Statutory permits, municipal noise rules, alcohol licensing, and safety capacity evaluator."""
from __future__ import annotations

from app.models import EventType, StatutoryPermits


def evaluate_statutory_permits(event_type: str, guest_count: int, location: str | None = None) -> StatutoryPermits:
    """Evaluate context-aware statutory rules, permit requirements, and capacity safety thresholds.

    Args:
        event_type: Category identifier ('wedding', 'birthday', 'community').
        guest_count: Expected attendance.
        location: Venue address or descriptive venue type (optional).

    Returns:
        StatutoryPermits: Permit statuses, liquor guidelines, food hygiene rules, and capacity limits.
    """
    e_type = event_type.lower()

    if e_type == EventType.COMMUNITY.value:
        sound_req = True
        alcohol_notes = (
            "Public Park / Plaza: Requires a municipal Special One-Day Event Liquor License. "
            "Alcohol must be confined within a perimeter fenced beer garden with ID-wristband check stations "
            "and certified security personnel at all egress points."
        )
        food_hygiene = (
            "Temporary Food Facility (TFF) permits required for all food vendors and food trucks. "
            "All operators must display local County Health Department inspection certificates, hand-washing stations, "
            "and NSF-certified mechanical hot/cold holding equipment."
        )
        capacity = (
            f"Expected attendance {guest_count:,} requires minimum 2 ADA-accessible portable restrooms per 250 people, "
            "and certified crowd managers (1 per 250 attendees). Minimum 7 sq ft per standing attendee required in viewing plazas."
        )
        weather = (
            "Mandatory outdoor severe weather contingency: High-wind threshold (35 mph) triggers canopy teardown. "
            "Rain backup date or enclosed indoor auditorium reservation required within 48-hour municipal window."
        )

    elif e_type == EventType.WEDDING.value:
        sound_req = guest_count > 120 or (location and "outdoor" in location.lower())
        alcohol_notes = (
            "Private Venue: Verify whether venue holds a permanent premise liquor license or requires an ABC/TABC "
            "Catering Authorization. Bartenders must carry state-certified alcohol service credentials (e.g. TIPS / LEAD) "
            "and commercial general liquor liability insurance ($1,000,000+ policy)."
        )
        food_hygiene = (
            "Catering kitchen must be fully licensed and permitted. Ensure temperature logs for passed raw shellfish/sushi "
            "and verify dedicated non-cross-contaminated preparation zones for gluten and severe nut allergies."
        )
        capacity = (
            f"Seated banquet dining for {guest_count} guests requires minimum 15 sq ft per guest (minimum {guest_count * 15:,} sq ft ballroom). "
            "Ensure emergency exit doors remain unobstructed with 36-inch clear aisle pathways between round banquet tables."
        )
        weather = (
            "Outdoor Garden / Tent: Tent reservation contract with sidewalls, heater units, and flooring must be locked "
            "with vendor deposit. Weather call decision deadline is 48 hours prior to ceremony."
        )

    else:  # Birthday
        sound_req = False
        alcohol_notes = (
            "Private Residence or Rented Hall: Host liquor liability is typically covered under personal umbrella "
            "or event insurance rider ($50–$150). If selling tickets or charging for drinks, a temporary permit is required."
        )
        food_hygiene = (
            "Ensure bakery storage under 40°F for dairy custard and fresh fruit cakes until 30 minutes before cutting."
        )
        capacity = (
            f"Standing cocktail party for {guest_count} guests requires 8–10 sq ft per person (minimum {guest_count * 9} sq ft). "
            "Verify smoke detector and fire extinguisher placements."
        )
        weather = "Indoor backup space or patio pop-up canopy ready in case of rain."

    return StatutoryPermits(
        sound_permit_required=sound_req,
        alcohol_license_notes=alcohol_notes,
        food_handling_hygiene=food_hygiene,
        fire_capacity_regulations=capacity,
        weather_backup_plan=weather,
    )
