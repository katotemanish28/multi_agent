"""
Small static IATA lookup for validating what the LLM extracts. Both
qwen2.5 and llama3.1 will occasionally hallucinate airport codes
(seen: Chennai -> 'MMA' and 'CJF' in two separate qwen runs, correct
is 'MAA') even while producing perfectly schema-valid JSON. Schema
validity is not the same as correctness — this closes that gap.
 
Extend this dict as your demo cities require. For a resume project,
~20-30 major Indian cities + a handful of international ones is
plenty; you don't need full global coverage.
"""
 
IATA_CODES = {
    "mumbai": "BOM", "bombay": "BOM",
    "delhi": "DEL", "new delhi": "DEL",
    "bangalore": "BLR", "bengaluru": "BLR",
    "chennai": "MAA", "madras": "MAA",
    "goa": "GOI",
    "pune": "PNQ",
    "hyderabad": "HYD",
    "kolkata": "CCU", "calcutta": "CCU",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "kochi": "COK", "cochin": "COK",
    "lucknow": "LKO",
    "chandigarh": "IXC",
    "srinagar": "SXR",
    "amritsar": "ATQ",
    "varanasi": "VNS",
    "indore": "IDR",
    "nagpur": "NAG",
    "bhubaneswar": "BBI",
    "guwahati": "GAU",
    "trivandrum": "TRV", "thiruvananthapuram": "TRV",
    "nashik": "ISK",
    # Hill stations & non-airport destinations mapped to nearest airport
    "kasol": "KUU", "manali": "KUU", "kullu": "KUU",
    "leh": "IXL", "ladakh": "IXL",
    "shimla": "SLV",
    "dharamshala": "DHM", "mcleodganj": "DHM",
    "rishikesh": "DED", "haridwar": "DED", "dehradun": "DED",
    "ooty": "CJB",
    "munnar": "COK",
    "udaipur": "UDR",
    "london": "LON",
    "new york": "NYC",
    "dubai": "DXB",
    "singapore": "SIN",
}
 
VALID_IATA_CODES = set(IATA_CODES.values())
 
# IATA code -> (lat, lon), for hotel search radius queries. Same city set
# as IATA_CODES above — extend both together.
IATA_COORDINATES = {
    "BOM": (19.0760, 72.8777),
    "DEL": (28.6139, 77.2090),
    "BLR": (12.9716, 77.5946),
    "MAA": (13.0827, 80.2707),
    "GOI": (15.3800, 73.8310),
    "PNQ": (18.5204, 73.8567),
    "HYD": (17.3850, 78.4867),
    "CCU": (22.5726, 88.3639),
    "AMD": (23.0225, 72.5714),
    "JAI": (26.9124, 75.7873),
    "COK": (9.9312, 76.2673),
    "LKO": (26.8467, 80.9462),
    "IXC": (30.7333, 76.7794),
    "VNS": (25.3176, 82.9739),
    "ISK": (19.9975, 73.7898),
    "KUU": (31.8763, 77.1541),  # Kullu / Bhuntar (for Kasol & Manali)
    "IXL": (34.1359, 77.5771),  # Leh
    "SLV": (31.0818, 77.0601),  # Shimla
    "DHM": (32.1651, 76.2634),  # Dharamshala
    "DED": (30.1897, 78.1803),  # Dehradun (for Rishikesh/Haridwar)
    "CJB": (11.0300, 77.0434),  # Coimbatore (for Ooty)
    "UDR": (24.6177, 73.8961),  # Udaipur
}
 
# IATA code -> display/content-lookup city name, for the itinerary agent's
# destination_data.py keys.
IATA_TO_CITY = {
    "BOM": "Mumbai",
    "DEL": "Delhi",
    "BLR": "Bangalore",
    "MAA": "Chennai",
    "GOI": "Goa",
    "PNQ": "Pune",
    "HYD": "Hyderabad",
    "KUU": "Kasol",
    "IXL": "Leh",
    "SLV": "Shimla",
    "DHM": "Dharamshala",
    "DED": "Rishikesh",
    "CJB": "Ooty",
    "UDR": "Udaipur",
}
 
 
import datetime
 
 
def validate_iata_code(code: str) -> bool:
    """True if code is a 3-letter alphabetic string or in known lookup."""
    if not code or not isinstance(code, str):
        return False
    c = code.strip().upper()
    return len(c) == 3 and c.isalpha()


def resolve_city_to_iata(name: str) -> str | None:
    """City/place name -> IATA code, or None if not in the lookup."""
    if not name or not isinstance(name, str):
        return None
    cleaned = name.strip().lower()
    if cleaned in IATA_CODES:
        return IATA_CODES[cleaned]
    # If name is already a 3-letter IATA code
    if len(cleaned) == 3 and cleaned.isalpha():
        return cleaned.upper()
    return None


def validate_trip_intent(intent) -> list[str]:
    """
    Validates intent and applies smart defaults so graph execution doesn't crash:
    - Auto-fills origin to 'BOM' if omitted or invalid
    - Accepts any 3-letter IATA destination code or resolves city name
    - Auto-fills depart_date to 14 days from today if missing
    """
    warnings = []
    
    # 1. Origin Handling
    resolved_origin = resolve_city_to_iata(str(intent.origin or "")) if intent.origin else None
    if resolved_origin:
        intent.origin = resolved_origin
    elif not validate_iata_code(str(intent.origin or "")):
        intent.origin = "BOM"  # Default to Mumbai (BOM)
        warnings.append("Origin was not specified or unrecognized; defaulted to 'BOM' (Mumbai).")

    # 2. Destination Handling
    resolved_dest = resolve_city_to_iata(str(intent.destination or "")) if intent.destination else None
    if resolved_dest:
        intent.destination = resolved_dest
    elif not validate_iata_code(str(intent.destination or "")):
        # Best effort fallback: extract uppercase IATA or keep fallback
        if intent.destination and isinstance(intent.destination, str):
            intent.destination = intent.destination[:3].upper()
        else:
            intent.destination = "GOI"
            warnings.append("Destination was unrecognized; defaulted to 'GOI' (Goa).")

    # 3. Depart Date Handling
    if not intent.depart_date:
        default_date = datetime.date.today() + datetime.timedelta(days=14)
        intent.depart_date = default_date
        warnings.append(f"Departure date was not specified; defaulted to {default_date.isoformat()}.")

    return warnings