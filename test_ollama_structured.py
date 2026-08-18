import datetime
import ollama
from schemas import TripIntent
from validators import validate_trip_intent
 
TODAY = datetime.date.today().isoformat()
 
# (query, expected_origin, expected_destination) — expected values let us
# check CORRECTNESS, not just schema validity. A hallucinated but
# well-formed IATA code passes schema validation and still fails here.
TEST_QUERIES = [
    ("I want to fly from Mumbai to Delhi on 15th September, coming back on 20th, for 2 people, budget around 30000 rupees", "BOM", "DEL"),
    ("Book me a trip to Goa next weekend from Pune, just me, I like beaches", "PNQ", "GOI"),
    ("Flight from BLR to Chennai on 2026-10-01, one way, 1 adult", "BLR", "MAA"),
]
 
SYSTEM_PROMPT = f"""You extract trip details from user requests into JSON matching this schema:
{{
  "origin": "IATA code, e.g. BOM",
  "destination": "IATA code, e.g. DEL",
  "depart_date": "YYYY-MM-DD",
  "return_date": "YYYY-MM-DD or null",
  "adults": integer,
  "budget_inr": integer or null,
  "preferences": ["list", "of", "strings"]
}}
Respond with ONLY the JSON object, no other text.
Today's actual date is {TODAY}. Resolve any relative date ("next weekend",
"tomorrow", etc.) against this date — never against a year you remember
from training data."""
 
 
def test_model(model_name):
    print(f"\n{'=' * 50}\nTesting model: {model_name}\n{'=' * 50}")
    valid_count = 0
    correct_count = 0
    for query, expected_origin, expected_destination in TEST_QUERIES:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            format="json",
        )
        raw = response["message"]["content"]
        try:
            parsed = TripIntent.model_validate_json(raw)
            valid_count += 1
            warnings = validate_trip_intent(parsed)
            codes_correct = parsed.origin == expected_origin and parsed.destination == expected_destination
            date_sane = parsed.depart_date.year >= datetime.date.today().year
            if codes_correct and not warnings and date_sane:
                correct_count += 1
                print(f"CORRECT: {query[:55]}")
            else:
                print(f"VALID BUT WRONG: {query[:55]}")
                if not codes_correct:
                    print(f"       -> expected {expected_origin}->{expected_destination}, got {parsed.origin}->{parsed.destination}")
                if warnings:
                    print(f"       -> {warnings}")
                if not date_sane:
                    print(f"       -> suspicious date: {parsed.depart_date}")
            print(f"       -> {parsed.model_dump()}")
        except Exception as e:
            print(f"FAILED : {query[:55]}")
            print(f"       -> raw output: {raw}")
            print(f"       -> error: {e}")
    print(f"\n{model_name}: {valid_count}/{len(TEST_QUERIES)} schema-valid, {correct_count}/{len(TEST_QUERIES)} actually correct")
    return correct_count
 
 
if __name__ == "__main__":
    results = {}
    for model in ["qwen2.5:7b-instruct", "llama3.1:8b"]:
        results[model] = test_model(model)
    print(f"\n{'=' * 50}\nSummary (correct, not just valid): {results}\n{'=' * 50}")
    print("Use whichever model scored higher here. If both still miss cases,")
    print("plan on a resolve_city_to_iata() fallback + retry loop for day 2 —")
    print("that fallback is worth having no matter which model wins.")