"""
LangChain tool for hotel search. Backed by mock_hotels.py until Duffel
Stays access is approved. To go live later: swap the mock_search_hotels
call below for DuffelClient().search_hotels() with the same arguments —
the field names in mock_hotels.py were chosen to match Duffel's real
Stays response shape, so this should be a near drop-in swap.
"""
from langchain_core.tools import tool
from mock_hotels import mock_search_hotels
# from duffel_client import DuffelClient  # swap in once Stays access is approved


@tool
def search_hotels_tool(city: str, latitude: float, longitude: float, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> list[dict]:
    """Search for hotel offers in a city for given check-in/check-out
    dates (YYYY-MM-DD). Returns up to 5 simplified offers."""
    results = mock_search_hotels(
        city=city,
        latitude=latitude,
        longitude=longitude,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        adults=adults,
        rooms=rooms,
    )
    simplified = []
    for h in results[:5]:
        simplified.append({
            "offer_id": h["id"],
            "name": h["name"],
            "price_per_night": float(h["cheapest_rate_total_amount"]),
            "currency": h.get("cheapest_rate_currency", "INR"),
            "rating": h.get("rating"),
            "address": h.get("address"),
        })
    return simplified