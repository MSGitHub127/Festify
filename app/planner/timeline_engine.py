"""Run-of-show timeline engine, countdown milestone planner, and schedule conflict detector."""
from __future__ import annotations

from app.models import EventType, RunOfShowItem, TimelineMilestone, TimelinePlan

MACRO_MILESTONE_TEMPLATES: dict[str, list[dict[str, str]]] = {
    EventType.WEDDING.value: [
        {
            "timeframe": "12–9 Months Out",
            "title": "Establish Budget & Secure Primary Venue",
            "description": "Finalize estimated guest list, set hard financial cap, and place deposit on ceremony & reception venues.",
            "due_or_time": "Month 12",
            "owner": "Couple / Lead Planner",
        },
        {
            "timeframe": "9–6 Months Out",
            "title": "Hire Core Vendors (Photo, Video, DJ, Catering)",
            "description": "Book primary vendors that can only take one event per day. Schedule catering menu tastings.",
            "due_or_time": "Month 8",
            "owner": "Lead Planner",
        },
        {
            "timeframe": "6–4 Months Out",
            "title": "Send Save-the-Dates & Order Attire",
            "description": "Mail or publish digital Save-the-Dates. Order wedding attire and schedule first fitting appointments.",
            "due_or_time": "Month 6",
            "owner": "Couple",
        },
        {
            "timeframe": "3–2 Months Out",
            "title": "Send Formal Invitations & Plan Ceremony Script",
            "description": "Mail formal invitations with RSVP deadline 4 weeks out. Finalize ceremony vows, music cues, and floral mockups.",
            "due_or_time": "Month 3",
            "owner": "Couple & Officiant",
        },
        {
            "timeframe": "4–2 Weeks Out",
            "title": "Lock Final RSVP Headcount & Seating Chart",
            "description": "Deliver final meal counts and dietary breakdowns to caterer. Create escort card display and vendor payment schedule.",
            "due_or_time": "Week 3",
            "owner": "Lead Planner",
        },
        {
            "timeframe": "1 Week Out",
            "title": "Rehearsal, Final Walkthrough & Vendor Confirmations",
            "description": "Conduct ceremony rehearsal with wedding party. Confirm day-of load-in timelines with all external vendors.",
            "due_or_time": "Day -2",
            "owner": "Lead Planner & Venue Manager",
        },
    ],
    EventType.BIRTHDAY.value: [
        {
            "timeframe": "6–4 Weeks Out",
            "title": "Choose Theme, Date & Reserve Space",
            "description": "Select birthday concept, reserve venue or private party room, and create guest RSVP link.",
            "due_or_time": "Week 6",
            "owner": "Party Host",
        },
        {
            "timeframe": "3–2 Weeks Out",
            "title": "Order Custom Cake & Entertainment Bookings",
            "description": "Confirm bakery order with custom flavor and design. Book DJ, entertainer, or photo booth rental.",
            "due_or_time": "Week 3",
            "owner": "Party Host",
        },
        {
            "timeframe": "1 Week Out",
            "title": "Assemble Decor & Playlist Curation",
            "description": "Gather balloons, signage, photo backdrops, and finalize celebratory music playlist and games.",
            "due_or_time": "Week 1",
            "owner": "Party Host / Friends",
        },
        {
            "timeframe": "2 Days Out",
            "title": "Final Headcount & Refreshment Pickup",
            "description": "Confirm headcount for finger foods, pick up party favors, and confirm arrival window with venue.",
            "due_or_time": "Day -2",
            "owner": "Party Host",
        },
    ],
    EventType.COMMUNITY.value: [
        {
            "timeframe": "3–4 Months Out",
            "title": "Permits, Venue Reservation & Committee Formation",
            "description": "Submit municipal sound permits, park pavilion reservation, and insurance indemnity waivers.",
            "due_or_time": "Month 4",
            "owner": "Event Director",
        },
        {
            "timeframe": "2 Months Out",
            "title": "Vendor & Performer Call / Sponsorship Drive",
            "description": "Recruit local community organizations, food trucks, musical acts, and local business sponsors.",
            "due_or_time": "Month 2",
            "owner": "Vendor Coordinator",
        },
        {
            "timeframe": "1 Month Out",
            "title": "Public Marketing, Volunteer Training & AV Staging",
            "description": "Distribute community posters and social campaigns. Secure stage, sound system, and portable restrooms.",
            "due_or_time": "Month 1",
            "owner": "Volunteer Lead & AV Tech",
        },
        {
            "timeframe": "1 Week Out",
            "title": "Logistics Mapping & Emergency Services Notification",
            "description": "Finalize site map, volunteer shift schedules, and alert local precinct/EMS of event gathering.",
            "due_or_time": "Day -5",
            "owner": "Safety Coordinator",
        },
    ],
}

DAY_OF_RUN_OF_SHOW_TEMPLATES: dict[str, list[dict[str, str]]] = {
    EventType.WEDDING.value: [
        {"time": "09:00", "activity": "Hair & Makeup Prep and Vendor Load-In", "location": "Bridal Suite / Venue", "responsible": "Beauty Team & Venue Manager", "notes": "Snacks and coffee ready for wedding party. Florals delivered."},
        {"time": "13:30", "activity": "Photographer Arrives & Detail Shots", "location": "Bridal Suite & Grounds", "responsible": "Lead Photographer", "notes": "Rings, dress, stationery suite, and shoes ready for flat lays."},
        {"time": "14:30", "activity": "Couple's First Look & Romantic Portraits", "location": "Private Garden Courtyard", "responsible": "Photo / Video & Planner", "notes": "Keep guests and family away from first-look area for privacy."},
        {"time": "15:30", "activity": "Bridal Party & Immediate Family Photos", "location": "Main Lawn", "responsible": "Photographer & Coordinator", "notes": "Have printed family shot list with names to move quickly."},
        {"time": "16:30", "activity": "Guest Arrival & Pre-Ceremony Music", "location": "Ceremony Foyer", "responsible": "DJ / String Quartet & Ushers", "notes": "Welcome drinks and programs distributed. Cellphones silenced."},
        {"time": "17:00", "activity": "Ceremony Processional & Exchange of Vows", "location": "Ceremony Altar", "responsible": "Officiant & Wedding Party", "notes": "Sound tech monitors officiant and groom lavalier microphones."},
        {"time": "17:35", "activity": "Cocktail Hour & Extended Family Photos", "location": "Veranda / Terrace", "responsible": "Catering Staff & DJ", "notes": "Passed canapés and open bar opens. Couple signs marriage license."},
        {"time": "18:45", "activity": "Guests Invited into Grand Ballroom", "location": "Grand Ballroom", "responsible": "Lead Planner & MC", "notes": "Verify champagne poured at all tables for welcome toast."},
        {"time": "19:00", "activity": "Grand Entrance & Host Welcome Speech", "location": "Ballroom Dance Floor", "responsible": "DJ / MC & Hosts", "notes": "Spotlight on entrance doors. Welcome remarks 3-5 mins."},
        {"time": "19:15", "activity": "Dinner Service & Speeches", "location": "Dining Tables", "responsible": "Catering Lead & Speakers", "notes": "Speeches (Best Man, Maid of Honor) given between courses."},
        {"time": "20:30", "activity": "Cake Cutting & First Dance", "location": "Dance Floor", "responsible": "Couple & DJ", "notes": "Dim ambient lights, transition music from dinner to dance party."},
        {"time": "21:00", "activity": "Open Dance Floor & Dessert Station", "location": "Main Ballroom", "responsible": "DJ & Bartenders", "notes": "Late-night sliders and fries served at 22:00."},
        {"time": "23:00", "activity": "Grand Sparkler Send-Off & Vendor Breakdown", "location": "Front Driveway", "responsible": "Lead Planner & Security", "notes": "Safety buckets with water for spent sparklers."},
    ],
    EventType.BIRTHDAY.value: [
        {"time": "14:00", "activity": "Host Arrival & Party Setup", "location": "Event Room", "responsible": "Host & Decor Team", "notes": "Inflate balloon garland, place tableware, test sound playlist."},
        {"time": "15:00", "activity": "Guests Arrive & Welcome Drinks", "location": "Lounge Area", "responsible": "Host", "notes": "Upbeat party playlist playing, signature drinks & mocktails served."},
        {"time": "15:45", "activity": "Interactive Party Games & Photo Booth", "location": "Activity Stage", "responsible": "Game Host / MC", "notes": "Milestone trivia, polaroid photo guestbook signing."},
        {"time": "17:00", "activity": "Appetizer & Finger Food Buffet", "location": "Dining Buffet", "responsible": "Catering Lead", "notes": "Restock drinks and warm items."},
        {"time": "18:00", "activity": "Happy Birthday Song, Cake Cutting & Toast", "location": "Center Table", "responsible": "Host & Friends", "notes": "Sparkler candles lit, champagne & sparkling cider poured."},
        {"time": "18:30", "activity": "Open Dancing & Social Hour", "location": "Dance Area", "responsible": "DJ", "notes": "Party hits playlist, group photo on main backdrop."},
        {"time": "20:00", "activity": "Favors Handed Out & Event Wrap", "location": "Exit Table", "responsible": "Host", "notes": "Distribute personalized gift boxes. Room cleanup."},
    ],
    EventType.COMMUNITY.value: [
        {"time": "08:00", "activity": "Staging & Technical Load-In", "location": "Main Park Plaza", "responsible": "Production Lead & AV Crew", "notes": "Erect canopy tents, position stage, route heavy power cables."},
        {"time": "09:30", "activity": "Vendor & Community Partner Arrival", "location": "Perimeter Booths", "responsible": "Vendor Liaison", "notes": "Distribute badges, direct vehicle unloading, check food permits."},
        {"time": "10:30", "activity": "Volunteer Briefing & Safety Inspection", "location": "Information Tent", "responsible": "Safety Coordinator", "notes": "Distribute radios, check first aid kit, review emergency protocols."},
        {"time": "11:00", "activity": "Festival Opening & Welcome Address", "location": "Main Stage", "responsible": "Community Leader / MC", "notes": "National anthem, sponsor acknowledgments, schedule announcements."},
        {"time": "11:30", "activity": "Cultural Performances & Kids Zone Opens", "location": "Main Stage & Lawn", "responsible": "Stage Manager & Volunteers", "notes": "Face painting, bounce house monitor on duty."},
        {"time": "13:00", "activity": "Community Lunch & Food Truck Rush", "location": "Food Court", "responsible": "Sanitation Volunteers", "notes": "Empty recycling bins frequently, monitor water stations."},
        {"time": "15:00", "activity": "Keynote Performance & Community Awards", "location": "Main Stage", "responsible": "MC & Board Members", "notes": "Volunteer of the year awards presented."},
        {"time": "17:00", "activity": "Closing Ceremony & Clean-Up Sprint", "location": "Park Grounds", "responsible": "All Volunteers & City Staff", "notes": "Litter sweep, vendor load-out, stage disassembly."},
    ],
}


def detect_timeline_conflicts(items: list[RunOfShowItem]) -> list[str]:
    """Inspect run-of-show timing for logistical overlaps and missing buffer windows.

    Args:
        items: List of sequential RunOfShowItem schedule entries.

    Returns:
        list[str]: Warning messages detailing any simultaneous or overlapping events.
    """
    warnings: list[str] = []
    seen_times: dict[str, list[str]] = {}

    for item in items:
        seen_times.setdefault(item.time, []).append(f"{item.activity} ({item.location})")

    for t, acts in seen_times.items():
        if len(acts) > 1:
            warnings.append(f"Simultaneous activities scheduled at {t}: {' vs '.join(acts)}. Ensure distinct coordinators.")

    # Check for rapid transitions without buffer
    for i in range(len(items) - 1):
        curr_item = items[i]
        next_item = items[i + 1]
        if "Ceremony" in curr_item.activity and "Grand Entrance" in next_item.activity:
            warnings.append("Notice: Ensure at least 45 minutes between Ceremony and Grand Entrance for cocktail reception and photos.")

    return warnings


def generate_timeline_plan(event_type: str) -> TimelinePlan:
    """Generate comprehensive macro countdown milestones and micro run-of-show items.

    Args:
        event_type: Celebration category ('wedding', 'birthday', 'community').

    Returns:
        TimelinePlan: Complete countdown milestones, run-of-show table, and conflict alerts.
    """
    type_key = event_type.lower()
    macro_data = MACRO_MILESTONE_TEMPLATES.get(type_key, MACRO_MILESTONE_TEMPLATES[EventType.WEDDING.value])
    day_of_data = DAY_OF_RUN_OF_SHOW_TEMPLATES.get(type_key, DAY_OF_RUN_OF_SHOW_TEMPLATES[EventType.WEDDING.value])

    macro_milestones = [TimelineMilestone(**m) for m in macro_data]
    day_of_items = [RunOfShowItem(**d) for d in day_of_data]
    conflicts = detect_timeline_conflicts(day_of_items)

    return TimelinePlan(
        macro_milestones=macro_milestones,
        day_of_run_of_show=day_of_items,
        conflict_warnings=conflicts,
    )
