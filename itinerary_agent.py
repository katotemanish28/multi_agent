"""
Generates a day-by-day itinerary, grounded by a small FAISS RAG store
over destination_data.py rather than pure LLM memory. This is the same
mitigation as the IATA validator, applied to itinerary content: local
models will happily invent plausible-sounding attractions that don't
exist, so we retrieve real curated content and have the model compose
from it instead of recalling it.

Uses Ollama's embedding model (pull once: `ollama pull nomic-embed-text`)
to keep the whole pipeline local, matching the "no cloud APIs" goal.
"""
import ollama
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from schemas import TripItinerary, ItineraryDay
from destination_data import DESTINATION_CONTENT
from prompts import MODEL_NAME

_vectorstore_cache: dict[str, FAISS] = {}


def _get_vectorstore(city: str) -> FAISS | None:
    if city not in DESTINATION_CONTENT:
        return None
    if city not in _vectorstore_cache:
        docs = [Document(page_content=chunk) for chunk in DESTINATION_CONTENT[city]]
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        _vectorstore_cache[city] = FAISS.from_documents(docs, embeddings)
    return _vectorstore_cache[city]


def generate_itinerary(city: str, num_days: int, preferences: list[str]) -> TripItinerary:
    num_days = max(1, min(num_days, 7))  # keep demo itineraries sane
    vectorstore = _get_vectorstore(city)

    context = ""
    if vectorstore:
        query = f"things to do in {city} " + " ".join(preferences)
        results = vectorstore.similarity_search(query, k=4)
        context = "\n".join(f"- {d.page_content}" for d in results)
    else:
        context = f"(No curated content available for {city} — compose from general knowledge, and note this is unverified.)"

    system_prompt = f"""You are an expert travel planner. Create a realistic {num_days}-day travel itinerary for {city}.
Using the Reference Context below, generate specific activities and attractions for {city}.

Required JSON format:
{{
  "destination": "{city}",
  "days": [
    {{
      "day_number": 1,
      "theme": "City Highlights & Exploration",
      "activities": [
        "Visit popular central landmark",
        "Explore local cultural quarter",
        "Evening local cuisine experience"
      ]
    }}
  ]
}}

Reference context for {city}:
{context}"""

    prefs_text = ", ".join(preferences) if preferences else "general sightseeing"
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Traveler preferences: {prefs_text}"},
        ],
        format="json",
    )
    raw = response["message"]["content"]
    try:
        return TripItinerary.model_validate_json(raw)
    except Exception as e:
        print(f"[ItineraryAgent] Raw JSON validation warning ({e}); applying fallback parser.")
        try:
            import json
            data = json.loads(raw)
            days = []
            if isinstance(data, dict):
                raw_days = data.get("days") or data.get("itinerary") or data.get("schedule") or []
                if isinstance(raw_days, list):
                    for idx, d in enumerate(raw_days, 1):
                        if isinstance(d, dict):
                            theme = d.get("theme") or d.get("title") or f"Day {idx} Exploration"
                            acts = d.get("activities") or d.get("preferred_activities") or d.get("highlights") or []
                            str_acts = [str(a) for a in acts] if isinstance(acts, list) else [str(acts)]
                            days.append(ItineraryDay(day_number=d.get("day_number", idx), theme=str(theme), activities=str_acts or [f"Sightseeing in {city}"]))
            
            if not days:
                days = [
                    ItineraryDay(
                        day_number=i + 1,
                        theme=f"Day {i + 1}: Sightseeing in {city}",
                        activities=[f"Explore popular landmarks in {city}", f"Enjoy local food and culture", f"Evening walk in {city}"]
                    ) for i in range(num_days)
                ]
            return TripItinerary(destination=city, days=days)
        except Exception:
            days = [
                ItineraryDay(
                    day_number=i + 1,
                    theme=f"Day {i + 1}: Exploring {city}",
                    activities=[f"Visit top sights in {city}", f"Sample local food and markets", f"Evening leisure in {city}"]
                ) for i in range(num_days)
            ]
            return TripItinerary(destination=city, days=days)