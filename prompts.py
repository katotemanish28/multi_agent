"""
Centralizes the intent-extraction system prompt and the chosen model
name, so the actual graph and any test/eval script stay in sync.
llama3.1:8b was chosen on day 1 for being conservative about unstated
fields (null over fabrication) — see /areas/travel-multiagent-project
notes / README_DAY1.md.
"""
import datetime
 
MODEL_NAME = "qwen2.5:0.5b"
 
 
def build_intent_system_prompt() -> str:
    today = datetime.date.today().isoformat()
    return f"""You extract trip details from user requests into JSON matching this schema:
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
Today's actual date is {today}. Resolve any relative date ("next weekend",
"tomorrow", etc.) against this date — never against a year you remember
from training data.

Important Location Guidelines:
- If a requested destination does NOT have its own airport (e.g. Kasol, Manali, Rishikesh, Ooty, Munnar), use the nearest commercial airport IATA code (e.g. Kasol/Manali -> KUU, Rishikesh -> DED, Ooty -> CJB, Leh -> IXL). Do NOT invent non-existent 3-letter codes for small towns.
- Only fill a field if the user's request actually implies it. If the
user doesn't mention a return trip, set return_date to null — do NOT
invent a plausible-looking date."""