import os
import requests
from dotenv import load_dotenv
 
load_dotenv()
 
DUFFEL_BASE = "https://api.duffel.com"
DUFFEL_VERSION = "v2"
 
 
class DuffelClient:
    def __init__(self):
        self.token = os.environ["DUFFEL_ACCESS_TOKEN"]
 
    def _headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Duffel-Version": DUFFEL_VERSION,
            "Authorization": f"Bearer {self.token}",
        }
 
    def search_flights(self, origin, destination, depart_date, adults=1, return_date=None, cabin_class="economy"):
        slices = [{"origin": origin, "destination": destination, "departure_date": str(depart_date)}]
        if return_date:
            slices.append({"origin": destination, "destination": origin, "departure_date": str(return_date)})
        payload = {
            "data": {
                "slices": slices,
                "passengers": [{"type": "adult"} for _ in range(adults)],
                "cabin_class": cabin_class,
            }
        }
        resp = requests.post(
            f"{DUFFEL_BASE}/air/offer_requests",
            headers=self._headers(),
            params={"return_offers": "true"},
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["data"]["offers"]
 
    def search_hotels(self, latitude, longitude, check_in_date, check_out_date, adults=1, rooms=1, radius_km=5):
        """Requires approved Stays access — will 403 until then."""
        payload = {
            "data": {
                "rooms": rooms,
                "location": {
                    "radius": radius_km,
                    "geographic_coordinates": {"latitude": latitude, "longitude": longitude},
                },
                "guests": [{"type": "adult"} for _ in range(adults)],
                "check_in_date": str(check_in_date),
                "check_out_date": str(check_out_date),
            }
        }
        resp = requests.post(
            f"{DUFFEL_BASE}/stays/search",
            headers=self._headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["data"]["results"]