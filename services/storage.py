
import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path("data")
TRIPS_FILE = DATA_DIR / "trips.json"


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not TRIPS_FILE.exists():
        TRIPS_FILE.write_text("[]", encoding="utf-8")


def get_all_trips() -> list[dict]:
    _ensure_storage()

    try:
        data = json.loads(TRIPS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_trip(trip: dict) -> dict:
    trips = get_all_trips()

    trip = trip.copy()
    trip.setdefault("id", datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"))
    trip["updated_at"] = datetime.now(timezone.utc).isoformat()

    existing_index = next(
        (i for i, item in enumerate(trips) if item.get("id") == trip["id"]),
        None,
    )

    if existing_index is None:
        trip["created_at"] = trip["updated_at"]
        trips.append(trip)
    else:
        trip["created_at"] = trips[existing_index].get(
            "created_at", trip["updated_at"]
        )
        trips[existing_index] = trip

    _ensure_storage()
    TRIPS_FILE.write_text(
        json.dumps(trips, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return trip


def delete_trip(trip_id: str) -> bool:
    trips = get_all_trips()
    updated_trips = [trip for trip in trips if trip.get("id") != trip_id]

    if len(updated_trips) == len(trips):
        return False

    _ensure_storage()
    TRIPS_FILE.write_text(
        json.dumps(updated_trips, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return True
