"""Event scenario comparison engine: compare budgets, venues, and tradeoffs."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models import BudgetBreakdown, EventType
from app.planner.budget_engine import generate_budget_breakdown

router = APIRouter(prefix="/api/events", tags=["Compare Scenarios"])


class ScenarioInput(BaseModel):
    name: str = Field(..., description="Scenario title (e.g. 'Option A: Downtown Ballroom')")
    event_type: EventType = Field(default=EventType.WEDDING)
    total_budget: float = Field(..., ge=100.0)
    guest_count: int = Field(..., ge=1)
    venue_style: str = Field(default="Indoor")


class CategoryDiff(BaseModel):
    category: str
    scenario_a_amount: float
    scenario_b_amount: float
    difference: float
    percent_shift: float


class ScenarioCompareResponse(BaseModel):
    scenario_a_name: str
    scenario_b_name: str
    total_budget_diff: float
    guest_count_diff: int
    cost_per_guest_diff: float
    scenario_a_budget: BudgetBreakdown
    scenario_b_budget: BudgetBreakdown
    category_diffs: list[CategoryDiff]
    recommendation: str


@router.post("/compare", response_model=ScenarioCompareResponse)
def compare_event_scenarios(
    scenario_a: ScenarioInput,
    scenario_b: ScenarioInput,
) -> ScenarioCompareResponse:
    """Compare two event planning scenarios to evaluate cost tradeoffs, guest economics, and category allocations."""
    budget_a = generate_budget_breakdown(scenario_a.event_type.value, scenario_a.total_budget, scenario_a.guest_count)
    budget_b = generate_budget_breakdown(scenario_b.event_type.value, scenario_b.total_budget, scenario_b.guest_count)

    budget_diff = round(scenario_b.total_budget - scenario_a.total_budget, 2)
    guest_diff = scenario_b.guest_count - scenario_a.guest_count
    cost_per_guest_diff = round(budget_b.cost_per_guest - budget_a.cost_per_guest, 2)

    cat_map_a = {c.category: c.allocated_amount for c in budget_a.categories}
    cat_map_b = {c.category: c.allocated_amount for c in budget_b.categories}

    all_categories = sorted(set(cat_map_a.keys()) | set(cat_map_b.keys()))
    category_diffs: list[CategoryDiff] = []

    for cat in all_categories:
        amt_a = cat_map_a.get(cat, 0.0)
        amt_b = cat_map_b.get(cat, 0.0)
        diff = round(amt_b - amt_a, 2)
        pct = round((diff / amt_a * 100), 1) if amt_a > 0 else 0.0
        category_diffs.append(
            CategoryDiff(
                category=cat,
                scenario_a_amount=amt_a,
                scenario_b_amount=amt_b,
                difference=diff,
                percent_shift=pct,
            )
        )

    if budget_b.cost_per_guest < budget_a.cost_per_guest:
        recommendation = (
            f"'{scenario_b.name}' delivers better per-guest economic efficiency "
            f"(${budget_b.cost_per_guest:.2f}/guest vs ${budget_a.cost_per_guest:.2f}/guest), "
            f"saving ${abs(cost_per_guest_diff):.2f} per attendee while preserving contingency buffers."
        )
    else:
        recommendation = (
            f"'{scenario_a.name}' offers a more conservative per-guest spend "
            f"(${budget_a.cost_per_guest:.2f}/guest vs ${budget_b.cost_per_guest:.2f}/guest). "
            f"Choosing '{scenario_b.name}' increases per-attendee investment by ${cost_per_guest_diff:.2f}."
        )

    return ScenarioCompareResponse(
        scenario_a_name=scenario_a.name,
        scenario_b_name=scenario_b.name,
        total_budget_diff=budget_diff,
        guest_count_diff=guest_diff,
        cost_per_guest_diff=cost_per_guest_diff,
        scenario_a_budget=budget_a,
        scenario_b_budget=budget_b,
        category_diffs=category_diffs,
        recommendation=recommendation,
    )
