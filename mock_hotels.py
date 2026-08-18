"""
Fallback hotel data, shaped like Duffel's Stays search response, for use
while Stays access is pending. Keyed by city name (matching
destination_data.py's keys) so results actually match the destination —
a single flat list previously caused every search to return Delhi
hotels regardless of where the trip was actually going.

Once real Stays access comes through, this whole file can be swapped
out for a live DuffelClient().search_hotels() call in hotel_agent.py —
downstream nodes only care about the field names, not the source.
"""

MOCK_HOTELS_BY_CITY = {
    "Delhi": [
        {"id": "mock_del_001", "name": "Taj Palace", "cheapest_rate_total_amount": "8500.00", "cheapest_rate_currency": "INR", "rating": 5, "address": "Diplomatic Enclave, New Delhi"},
        {"id": "mock_del_002", "name": "Ibis New Delhi Aerocity", "cheapest_rate_total_amount": "4200.00", "cheapest_rate_currency": "INR", "rating": 3, "address": "Aerocity, New Delhi"},
        {"id": "mock_del_003", "name": "The Lalit New Delhi", "cheapest_rate_total_amount": "6800.00", "cheapest_rate_currency": "INR", "rating": 4, "address": "Barakhamba Avenue, Connaught Place, New Delhi"},
    ],
    "Goa": [
        {"id": "mock_goi_001", "name": "Taj Fort Aguada Resort", "cheapest_rate_total_amount": "9200.00", "cheapest_rate_currency": "INR", "rating": 5, "address": "Sinquerim Beach, North Goa"},
        {"id": "mock_goi_002", "name": "Ibis Styles Goa Calangute", "cheapest_rate_total_amount": "3800.00", "cheapest_rate_currency": "INR", "rating": 3, "address": "Calangute, North Goa"},
        {"id": "mock_goi_003", "name": "Alila Diwa Goa", "cheapest_rate_total_amount": "6200.00", "cheapest_rate_currency": "INR", "rating": 4, "address": "Majorda, South Goa"},
    ],
    "Mumbai": [
        {"id": "mock_bom_001", "name": "Taj Mahal Palace", "cheapest_rate_total_amount": "12500.00", "cheapest_rate_currency": "INR", "rating": 5, "address": "Colaba, Mumbai"},
        {"id": "mock_bom_002", "name": "Ibis Mumbai Airport", "cheapest_rate_total_amount": "4500.00", "cheapest_rate_currency": "INR", "rating": 3, "address": "Kurla, Mumbai"},
        {"id": "mock_bom_003", "name": "Trident Bandra Kurla", "cheapest_rate_total_amount": "7800.00", "cheapest_rate_currency": "INR", "rating": 4, "address": "Bandra Kurla Complex, Mumbai"},
    ],
    "Bangalore": [
        {"id": "mock_blr_001", "name": "The Leela Palace Bengaluru", "cheapest_rate_total_amount": "10500.00", "cheapest_rate_currency": "INR", "rating": 5, "address": "Old Airport Road, Bangalore"},
        {"id": "mock_blr_002", "name": "Ibis Bengaluru Techpark", "cheapest_rate_total_amount": "3900.00", "cheapest_rate_currency": "INR", "rating": 3, "address": "Marathahalli, Bangalore"},
        {"id": "mock_blr_003", "name": "Vivanta Bengaluru", "cheapest_rate_total_amount": "6500.00", "cheapest_rate_currency": "INR", "rating": 4, "address": "MG Road, Bangalore"},
    ],
    "Chennai": [
        {"id": "mock_maa_001", "name": "Taj Fisherman's Cove Resort", "cheapest_rate_total_amount": "8900.00", "cheapest_rate_currency": "INR", "rating": 5, "address": "Covelong Beach, Chennai"},
        {"id": "mock_maa_002", "name": "Ibis Chennai City Centre", "cheapest_rate_total_amount": "3700.00", "cheapest_rate_currency": "INR", "rating": 3, "address": "Nungambakkam, Chennai"},
        {"id": "mock_maa_003", "name": "The Raintree Anna Salai", "cheapest_rate_total_amount": "6000.00", "cheapest_rate_currency": "INR", "rating": 4, "address": "Anna Salai, Chennai"},
    ],
}

DEFAULT_CITY = "Delhi"


def mock_search_hotels(city=None, latitude=None, longitude=None, check_in_date=None, check_out_date=None, adults=1, rooms=1, radius_km=5):
    if city in MOCK_HOTELS_BY_CITY:
        return MOCK_HOTELS_BY_CITY[city]
    
    # Dynamic fallback for any location in the world (e.g. Leh, Paris, etc.)
    city_name = str(city).title() if city else "City Center"
    return [
        {"id": f"mock_custom_001", "name": f"Grand {city_name} Resort & Spa", "cheapest_rate_total_amount": "7500.00", "cheapest_rate_currency": "INR", "rating": 5, "address": f"Central Avenue, {city_name}"},
        {"id": f"mock_custom_002", "name": f"Ibis {city_name}", "cheapest_rate_total_amount": "3900.00", "cheapest_rate_currency": "INR", "rating": 3, "address": f"Downtown, {city_name}"},
        {"id": f"mock_custom_003", "name": f"The Heritage Hotel {city_name}", "cheapest_rate_total_amount": "5800.00", "cheapest_rate_currency": "INR", "rating": 4, "address": f"Old Town, {city_name}"},
    ]
