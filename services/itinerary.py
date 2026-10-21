
from math import radians, sin, cos, sqrt, atan2


def calculate_distance_km(place1: dict, place2: dict) -> float:
    """Calculate approximate distance between two coordinates."""
    lat1, lon1 = radians(place1["lat"]), radians(place1["lon"])
    lat2, lon2 = radians(place2["lat"]), radians(place2["lon"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 6371 * 2 * atan2(sqrt(a), sqrt(1 - a))


def group_nearby_attractions(
    attractions: list[dict],
    max_distance_km: float = 5.0,
) -> list[list[dict]]:
    """Group nearby attractions using their geographic coordinates."""
    if not attractions:
        return []

    remaining = attractions.copy()
    groups = []

    while remaining:
        current = [remaining.pop(0)]
        changed = True

        while changed:
            changed = False

            for place in remaining[:]:
                if any(
                    calculate_distance_km(place, visited) <= max_distance_km
                    for visited in current
                ):
                    current.append(place)
                    remaining.remove(place)
                    changed = True

        groups.append(current)

    return groups


def build_day(day_number: int, activities: list[dict]) -> dict:
    """Create a structured day in the itinerary."""
    return {
        "day": day_number,
        "activities": activities,
        "estimated_cost": sum(
            float(activity.get("cost", 0))
            for activity in activities
        ),
    }
