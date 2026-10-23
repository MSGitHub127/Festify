"""Vendor vetting checklists, contract risk rubrics, and deliverable milestones."""
from __future__ import annotations

from app.models import EventType, VendorChecklistItem

VENDOR_CATEGORY_RUBRICS: dict[str, list[dict]] = {
    EventType.WEDDING.value: [
        {
            "category": "Catering & Bar Services",
            "benchmark_percentage": 45.0,
            "must_ask_questions": [
                "Is a complimentary menu tasting included prior to contract signing or only after paying a retainer?",
                "What is your server-to-guest ratio for plated dinner service (industry standard is 1:10 to 1:12)?",
                "Do you provide bar setup, ice, glassware, and certified liquor liability insurance?",
                "What are your dietary handling protocols for severe nut, celiac, and vegan restrictions?",
                "What is your exact policy and fee structure for vendor meals for photographers and DJs?",
            ],
            "contract_red_flags": [
                "Mandatory 22%+ service charge that explicitly excludes gratuity without clear staff distribution disclosure.",
                "Non-refundable initial deposit exceeding 35% of the total estimated food and beverage minimum.",
                "Lack of a force majeure clause covering health emergency venue closures or government bans.",
                "Short notice cutoff for final headcount changes (less than 14 days before the event).",
            ],
            "deliverable_milestones": [
                "Tasting scheduled 4–6 months out",
                "Final menu selections and wine pairings locked 60 days out",
                "Guaranteed headcount and dietary list delivered 14 days out",
                "Final balance paid 7–10 days out",
            ],
        },
        {
            "category": "Photography & Videography",
            "benchmark_percentage": 12.0,
            "must_ask_questions": [
                "Will you personally shoot the wedding, or do you subcontract to an associate shooter?",
                "What is your exact backup equipment strategy if a camera body or SD card fails during the ceremony?",
                "Do you provide a full release for personal printing and high-resolution digital file downloads?",
                "What is your guaranteed delivery timeline for the sneak peek album (e.g. 48 hours) and full gallery (6–8 weeks)?",
            ],
            "contract_red_flags": [
                "Contract does not guarantee the primary photographer by name in writing.",
                "Hourly rate overtime charges exceeding 150% of the standard prorated rate without 30-minute grace buffers.",
                "Clause allowing the studio to withhold finished digital negatives for post-event upcharges.",
            ],
            "deliverable_milestones": [
                "Engagement shoot completed 8–10 months out",
                "Shot list questionnaire completed 30 days out",
                "Sneak peek gallery delivered within 72 hours of wedding",
                "Full digital gallery and raw video delivered within 8 weeks",
            ],
        },
        {
            "category": "Music & Entertainment (DJ / Band)",
            "benchmark_percentage": 10.0,
            "must_ask_questions": [
                "Do you provide your own complete PA system, wireless microphones, and dance floor lighting?",
                "How do you handle our 'Must Play' and 'Do Not Play' request lists?",
                "What is your contingency plan if the scheduled DJ or musician falls ill on the morning of the event?",
                "Will you act as the official Master of Ceremonies (MC) for announcements, entrances, and dances?",
            ],
            "contract_red_flags": [
                "No backup DJ or equipment rider specified in the contract terms.",
                "Strict cancellation fee requiring 100% payment even if canceled 6+ months in advance.",
            ],
            "deliverable_milestones": [
                "Music taste profile and special song choices submitted 45 days out",
                "Phonetic pronunciation list of wedding party names delivered 14 days out",
                "Sound check completed 2 hours prior to guest arrival on day-of",
            ],
        },
        {
            "category": "Floral & Event Design",
            "benchmark_percentage": 8.0,
            "must_ask_questions": [
                "Can you provide a mock-up sample centerpiece or digital sketch prior to ordering bulk florals?",
                "What substitutions will you make if specific blooms (e.g. peonies) are unavailable due to seasonal frost?",
                "Does your quote include day-of delivery, ceremony arch setup, and late-night breakdown/removal?",
            ],
            "contract_red_flags": [
                "Contract permits arbitrary floral substitutions with lower-tier blooms without price adjustments.",
                "Hidden disposal and tear-down fees not itemized in the initial invoice quote.",
            ],
            "deliverable_milestones": [
                "Color palette and design board finalized 4 months out",
                "Final centerpiece count adjusted with RSVP numbers 21 days out",
                "Day-of delivery completed 3 hours prior to ceremony start",
            ],
        },
    ],
    EventType.BIRTHDAY.value: [
        {
            "category": "Venue & Space Rental",
            "benchmark_percentage": 30.0,
            "must_ask_questions": [
                "How many hours are included for setup before the party and cleanup afterwards?",
                "Are we permitted to bring an outside specialty cake or outside caterer?",
                "Is there built-in AV (projector, Bluetooth sound) and who operates it?",
            ],
            "contract_red_flags": [
                "Security deposit retention for normal cosmetic cleaning or glitter/confetti penalties without notice.",
                "Excessive room rental overtime penalty (more than 1 hour rate for 15 minutes over).",
            ],
            "deliverable_milestones": [
                "Room walkthrough and deposit paid 6 weeks out",
                "Music playlist and AV setup tested 1 day prior",
            ],
        },
        {
            "category": "Bakery & Custom Cake",
            "benchmark_percentage": 15.0,
            "must_ask_questions": [
                "Do you deliver and assemble tiered cakes on-site, or is it pickup only?",
                "Can you accommodate severe dairy, egg, or nut allergies with certified sanitized equipment?",
            ],
            "contract_red_flags": [
                "No refund policy if cake is structurally damaged during bakery delivery transit.",
            ],
            "deliverable_milestones": [
                "Flavor tasting and sketch approved 4 weeks out",
                "Delivery confirmed to venue 2 hours before party start",
            ],
        },
    ],
    EventType.COMMUNITY.value: [
        {
            "category": "Stage, Sound & Rigging",
            "benchmark_percentage": 25.0,
            "must_ask_questions": [
                "Does the stage include weatherproofing canopies and certified structural engineer stamp?",
                "Are heavy-duty quiet power generators and cable crossover protectors included?",
                "Is an on-site audio engineer present throughout all community performances?",
            ],
            "contract_red_flags": [
                "Contract charges full fee for weather cancellations without reschedule or postponement provisions.",
            ],
            "deliverable_milestones": [
                "City electrical permit and site inspection approved 3 weeks out",
                "Stage erection and sound check completed by 09:00 on event day",
            ],
        },
        {
            "category": "Public Sanitation & Restroom Trailers",
            "benchmark_percentage": 15.0,
            "must_ask_questions": [
                "What is the ratio of ADA-compliant restroom stalls per 250 expected attendees?",
                "Are regular pump-outs and hand-sanitizer restocking included during a full-day event?",
            ],
            "contract_red_flags": [
                "Hidden disposal pumping charges added after the event.",
            ],
            "deliverable_milestones": [
                "Units delivered and leveled 1 day prior to event",
                "Final pickup and park lawn inspection morning after event",
            ],
        },
    ],
}


def get_vendor_checklists(event_type: str) -> list[VendorChecklistItem]:
    """Retrieve structured vetting questions, red flags, and delivery milestones."""
    key = event_type.lower()
    raw = VENDOR_CATEGORY_RUBRICS.get(key, VENDOR_CATEGORY_RUBRICS[EventType.WEDDING.value])
    return [VendorChecklistItem(**item) for item in raw]
