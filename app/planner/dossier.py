"""Event dossier compiler: produces a comprehensive, publication-grade client & vendor briefing packet."""
from __future__ import annotations

from app.models import (
    BudgetBreakdown,
    CreativeIdeas,
    StatutoryPermits,
    TimelinePlan,
    VendorChecklistItem,
)


def compile_event_dossier(
    title: str,
    event_type: str,
    guest_count: int,
    total_budget: float,
    vibe_theme: str,
    budget: BudgetBreakdown,
    timeline: TimelinePlan,
    vendor_rubric: list[VendorChecklistItem],
    creative_ideas: CreativeIdeas,
    permits: StatutoryPermits,
) -> str:
    """Produce a complete, structured Markdown Event Dossier ready for clients, vendors, and coordinators."""
    lines: list[str] = [
        f"# 📋 Festify Event Dossier: {title}",
        "",
        f"**Event Type:** {event_type.title()}  ",
        f"**Guest Count:** {guest_count:,} attendees  ",
        f"**Total Budget:** ${total_budget:,.2f} (Est. ${budget.cost_per_guest:.2f} per guest)  ",
        f"**Aesthetic Theme:** {vibe_theme}  ",
        f"**Emergency Contingency Buffer:** ${budget.contingency_buffer:,.2f}  ",
        "",
        "---",
        "",
        "## 1. 💰 Budget Allocation & Expense Architecture",
        "",
        "| Category | Allocation | Per Guest | Recommended Deliverables |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for cat in budget.categories:
        items_str = ", ".join(cat.recommended_items[:2])
        lines.append(f"| **{cat.category}** ({cat.percentage}%) | ${cat.allocated_amount:,.2f} | ${cat.per_guest_amount:.2f} | {items_str} |")

    lines.extend([
        "",
        "### 💡 Smart Cost Optimization Tips",
    ])
    for tip in budget.cost_saving_tips:
        lines.append(f"- {tip}")

    lines.extend([
        "",
        "---",
        "",
        "## 2. ⏱️ Timeline & Day-of Run-of-Show",
        "",
        "### 📅 Macro Countdown Milestones",
    ])
    for m in timeline.macro_milestones:
        lines.append(f"- **{m.timeframe}** — *{m.title}* ({m.owner}): {m.description}")

    lines.extend([
        "",
        "### 🕒 Day-Of Run-of-Show Minute Schedule",
        "",
        "| Time | Activity | Location | Responsible | Key Notes |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])
    for r in timeline.day_of_run_of_show:
        lines.append(f"| **{r.time}** | {r.activity} | {r.location} | {r.responsible} | {r.notes} |")

    if timeline.conflict_warnings:
        lines.extend([
            "",
            "### ⚠️ Schedule Warnings & Buffer Notices",
        ])
        for warn in timeline.conflict_warnings:
            lines.append(f"- ⚠️ {warn}")

    lines.extend([
        "",
        "---",
        "",
        "## 3. 🤝 Vendor Checklists & Contract Risk Rubrics",
        "",
    ])
    for v in vendor_rubric:
        lines.append(f"### {v.category} (Est. {v.benchmark_percentage}% of Budget)")
        lines.append("**Must-Ask Vetting Questions:**")
        for q in v.must_ask_questions:
            lines.append(f"  - [ ] {q}")
        lines.append("**Contract Red Flags to Avoid:**")
        for f in v.contract_red_flags:
            lines.append(f"  - 🚩 {f}")
        lines.append("**Deliverable Milestones:**")
        for d in v.deliverable_milestones:
            lines.append(f"  - 📌 {d}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 4. 🎨 Creative Blueprint: Themes, Menus & Speeches",
        "",
        "### Selected Theme Concepts",
    ])
    for t in creative_ideas.themes:
        palette_hex = " ".join(f"`{c}`" for c in t.color_palette)
        lines.append(f"#### {t.name} (*{t.tagline}*)")
        lines.append(f"{t.description}")
        lines.append(f"- **Color Palette:** {palette_hex}")
        lines.append(f"- **Key Accents:** {', '.join(t.decor_accents)}")
        lines.append("")

    lines.extend([
        "### 🍽️ Curated Dietary-Inclusive Menu",
        "",
        "| Course | Dish Name | Dietary Accommodations | Beverage Pairing |",
        "| :--- | :--- | :--- | :--- |",
    ])
    for menu in creative_ideas.curated_menu:
        tags = ", ".join(menu.dietary_tags)
        lines.append(f"| **{menu.course}** | {menu.item_name} | {tags} | {menu.pairing} |")

    lines.extend([
        "",
        "### 🎤 Toast & Speech Script Draft",
        f"**Speaker:** {creative_ideas.speech_toast.speaker_role}  ",
        f"**Tone:** {creative_ideas.speech_toast.tone}  ",
        f"> *\"{creative_ideas.speech_toast.draft_text}\"*",
        "",
        "---",
        "",
        "## 5. 📜 Statutory Permits & Safety Regulations",
        f"- **Amplified Sound Permit:** {'Required — Municipal variance filing needed' if permits.sound_permit_required else 'Not strictly required for this scale'}",
        f"- **Alcohol Licensing:** {permits.alcohol_license_notes}",
        f"- **Food Hygiene & Safety:** {permits.food_handling_hygiene}",
        f"- **Fire Marshal & Capacity:** {permits.fire_capacity_regulations}",
        f"- **Inclement Weather Backup Plan:** {permits.weather_backup_plan}",
        "",
        "---",
        "*Compiled automatically by Festify Event Intelligence Engine.*",
    ])

    return "\n".join(lines)
