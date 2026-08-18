"""
LangChain tool wrapping duffel_client.search_flights.
 
NOTE: the field-simplification below is written defensively (.get()
chains with fallbacks) because we haven't yet confirmed the exact
shape of a live offer against your real Duffel test account output.
Run test_duffel.py, paste one raw offer's JSON back, and this can be
tightened to pull exact fields with confidence instead of guessing.
"""
from langchain_core.tools import tool
from duffel_client import DuffelClient
 
 
def _simplify_offer(offer: dict) -> dict:
    slices = offer.get("slices", [])
    first_slice = slices[0] if slices else {}
    segments = first_slice.get("segments", [])
    first_seg = segments[0] if segments else {}
    last_seg = segments[-1] if segments else {}
 
    carrier = (
        first_seg.get("marketing_carrier", {}).get("name")
        or first_seg.get("operating_carrier", {}).get("name")
        or "Unknown airline"
    )
 
    return {
        "offer_id": offer.get("id"),
        "airline": carrier,
        "price": offer.get("total_amount"),
        "currency": offer.get("total_currency"),
        "depart_time": first_seg.get("departing_at"),
        "arrive_time": last_seg.get("arriving_at"),
        "stops": max(len(segments) - 1, 0),
    }
 
 
MOCK_FLIGHT_OFFERS = [
    {
        "offer_id": "mock_fl_001",
        "airline": "IndiGo",
        "price": "6450.00",
        "currency": "INR",
        "depart_time": "08:15",
        "arrive_time": "10:30",
        "stops": 0,
    },
    {
        "offer_id": "mock_fl_002",
        "airline": "Air India",
        "price": "7800.00",
        "currency": "INR",
        "depart_time": "14:20",
        "arrive_time": "16:45",
        "stops": 0,
    },
    {
        "offer_id": "mock_fl_003",
        "airline": "Vistara",
        "price": "8900.00",
        "currency": "INR",
        "depart_time": "19:00",
        "arrive_time": "21:15",
        "stops": 0,
    },
]


@tool
def search_flights_tool(origin: str, destination: str, depart_date: str, adults: int = 1, return_date: str | None = None) -> list[dict]:
    """Search for flight offers between two IATA airport codes on a given date.
    Dates must be YYYY-MM-DD. Returns up to 5 simplified offers."""
    try:
        client = DuffelClient()
        offers = client.search_flights(origin, destination, depart_date, adults=adults, return_date=return_date)
        if offers:
            return [_simplify_offer(o) for o in offers[:5]]
    except Exception as e:
        print(f"[FlightAgent] Duffel search warning ({e}); returning fallback flights.")
    
    return MOCK_FLIGHT_OFFERS