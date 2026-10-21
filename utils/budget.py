
def calculate_total_cost(activities: list[dict]) -> float:
    """Calculate total estimated cost of all activities."""
    return round(
        sum(float(activity.get("cost", 0)) for activity in activities),
        2,
    )


def calculate_remaining_budget(
    total_budget: float,
    activities: list[dict],
) -> float:
    """Calculate remaining budget after planned activities."""
    return round(total_budget - calculate_total_cost(activities), 2)


def build_budget_summary(
    total_budget: float,
    activities: list[dict],
) -> dict:
    """Return a summary of planned expenses."""
    spent = calculate_total_cost(activities)

    return {
        "total_budget": round(total_budget, 2),
        "estimated_spent": spent,
        "remaining_budget": round(total_budget - spent, 2),
        "budget_exceeded": spent > total_budget,
    }
