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

from schemas import TripItinerary
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

    system_prompt = f"""You are a travel itinerary planner. Using ONLY the reference
context below (don't invent attractions not mentioned in it), create a
{num_days}-day itinerary for {city}. Respond with ONLY JSON matching:
{{"destination": "{city}", "days": [{{"day_number": 1, "theme": "short theme", "activities": ["activity 1", "activity 2", "activity 3"]}}]}}

Reference context:
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
    return TripItinerary.model_validate_json(raw)