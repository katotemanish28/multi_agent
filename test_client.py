import json
from duffel_client import DuffelClient
 
client = DuffelClient()
 
print("Testing flight search: BOM -> DEL")
offers = client.search_flights("BOM", "DEL", "2026-09-15")
print(f"Found {len(offers)} flight offers")
if offers:
    print(json.dumps(offers[0], indent=2)[:1000])
 
print("\nTesting hotel search: New Delhi (requires approved Stays access)")
try:
    hotels = client.search_hotels(28.6139, 77.2090, "2026-09-15", "2026-09-18")
    print(f"Found {len(hotels)} hotel results")
    if hotels:
        print(json.dumps(hotels[0], indent=2)[:1000])
except Exception as e:
    print(f"Hotel search failed (expected if Stays access is still pending): {e}")
    print("Falling back to mock_hotels.py for now — see that file's docstring.")
    from mock_hotels import mock_search_hotels
    print(mock_search_hotels())