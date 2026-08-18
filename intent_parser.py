import ollama
from schemas import TripIntent
from validators import validate_trip_intent
from prompts import build_intent_system_prompt, MODEL_NAME
 
MAX_ATTEMPTS = 3

 
def parse_trip_intent(user_query: str) -> tuple[TripIntent, list[str]]:
    messages = [
        {"role": "system", "content": build_intent_system_prompt()},
        {"role": "user", "content": user_query},
    ]
    intent = None
    warnings: list[str] = []
 
    for attempt in range(MAX_ATTEMPTS):
        response = ollama.chat(model=MODEL_NAME, messages=messages, format="json")
        raw = response["message"]["content"]
 
        try:
            intent = TripIntent.model_validate_json(raw)
        except Exception as e:
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"That wasn't valid JSON matching the schema ({e}). "
                           f"Respond with ONLY the corrected JSON object.",
            })
            continue
 
        warnings = validate_trip_intent(intent)
        if not warnings:
            return intent, []
 
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": f"Issues found: {warnings}. Double-check the IATA codes "
                       f"against real airport codes and respond with ONLY the "
                       f"corrected JSON object.",
        })
 
    # Exhausted retries — return best-effort intent with warnings attached
    # so the caller (graph) can decide whether to surface this to the user
    # rather than silently booking against a possibly-wrong code.
    return intent, warnings