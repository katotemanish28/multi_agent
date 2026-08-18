"""
The actual multi-agent orchestration graph:

  parse_intent
       |
   (fan-out)
   /        \\
search_flights  search_hotels
   \\        /
   (fan-in, both required)
  generate_itinerary
       |
  human_confirmation   <-- real LangGraph interrupt(), pauses execution
       |
   (fan-out)
   /        \\
 book_flight  book_hotel
   \\        /
   (fan-in)
     summary

Booking nodes below produce MOCK confirmations (no real payment/PII
collection) — deliberate for a demo project. The comment in each node
shows exactly what would change to call Duffel's real order-create
endpoint (test mode has unlimited fake balance, so it's genuinely
callable if you want to take this further).
"""
import datetime
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver

from intent_parser import parse_trip_intent
from flight_agent import search_flights_tool
from hotel_agent import search_hotels_tool
from itinerary_agent import generate_itinerary
from validators import IATA_COORDINATES, IATA_TO_CITY


class GraphState(TypedDict, total=False):
    user_query: str
    intent: dict
    intent_warnings: list
    flight_offers: list
    hotel_offers: list
    itinerary: dict
    approved: bool
    flight_booking: Optional[dict]
    hotel_booking: Optional[dict]
    summary: str


def node_parse_intent(state: GraphState) -> dict:
    intent, warnings = parse_trip_intent(state["user_query"])
    return {"intent": intent.model_dump(mode="json"), "intent_warnings": warnings}


def node_search_flights(state: GraphState) -> dict:
    intent = state["intent"]
    offers = search_flights_tool.invoke({
        "origin": intent["origin"],
        "destination": intent["destination"],
        "depart_date": str(intent["depart_date"]),
        "adults": intent.get("adults", 1),
        "return_date": str(intent["return_date"]) if intent.get("return_date") else None,
    })
    return {"flight_offers": offers}


def node_search_hotels(state: GraphState) -> dict:
    intent = state["intent"]
    dest = intent["destination"]
    city = IATA_TO_CITY.get(dest, dest)
    lat, lon = IATA_COORDINATES.get(dest, IATA_COORDINATES["DEL"])
    check_out = intent.get("return_date") or intent["depart_date"]
    offers = search_hotels_tool.invoke({
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "check_in_date": str(intent["depart_date"]),
        "check_out_date": str(check_out),
        "adults": intent.get("adults", 1),
        "rooms": 1,
    })
    return {"hotel_offers": offers}


def node_generate_itinerary(state: GraphState) -> dict:
    intent = state["intent"]
    city = IATA_TO_CITY.get(intent["destination"], intent["destination"])

    num_days = 3
    if intent.get("return_date"):
        d1 = datetime.date.fromisoformat(str(intent["depart_date"]))
        d2 = datetime.date.fromisoformat(str(intent["return_date"]))
        num_days = max(1, (d2 - d1).days)

    itinerary = generate_itinerary(city, num_days, intent.get("preferences", []))
    return {"itinerary": itinerary.model_dump(mode="json")}


def node_human_confirmation(state: GraphState) -> dict:
    decision = interrupt({
        "message": "Review the options below and confirm to proceed with booking.",
        "flight_offers": state.get("flight_offers"),
        "hotel_offers": state.get("hotel_offers"),
        "itinerary": state.get("itinerary"),
        "intent_warnings": state.get("intent_warnings"),
    })
    return {"approved": bool(decision.get("approved"))}


def node_book_flight(state: GraphState) -> dict:
    if not state.get("approved") or not state.get("flight_offers"):
        return {"flight_booking": None}
    chosen = state["flight_offers"][0]
    # Real booking would call: DuffelClient order-create with this
    # offer_id + passenger details (name, DOB, email, phone) + a
    # "balance" payment matching the offer's total_amount/currency.
    # Skipped here deliberately — no passenger PII collection in this demo.
    return {
        "flight_booking": {
            "status": "confirmed (mock)",
            "offer_id": chosen.get("offer_id"),
            "reference": f"MOCK-FL-{str(chosen.get('offer_id'))[-6:]}",
        }
    }


def node_book_hotel(state: GraphState) -> dict:
    if not state.get("approved") or not state.get("hotel_offers"):
        return {"hotel_booking": None}
    chosen = state["hotel_offers"][0]
    return {
        "hotel_booking": {
            "status": "confirmed (mock)",
            "offer_id": chosen.get("offer_id"),
            "reference": f"MOCK-HT-{str(chosen.get('offer_id'))[-6:]}",
        }
    }


def node_summary(state: GraphState) -> dict:
    if not state.get("approved"):
        return {"summary": "Trip not confirmed — no bookings were made."}
    intent = state["intent"]
    lines = [
        f"Trip: {intent['origin']} -> {intent['destination']}",
        f"Flight: {state.get('flight_booking')}",
        f"Hotel: {state.get('hotel_booking')}",
        f"Itinerary: {state.get('itinerary')}",
    ]
    return {"summary": "\n".join(lines)}


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("parse_intent", node_parse_intent)
    graph.add_node("search_flights", node_search_flights)
    graph.add_node("search_hotels", node_search_hotels)
    graph.add_node("generate_itinerary", node_generate_itinerary)
    graph.add_node("human_confirmation", node_human_confirmation)
    graph.add_node("book_flight", node_book_flight)
    graph.add_node("book_hotel", node_book_hotel)
    graph.add_node("summary", node_summary)

    graph.set_entry_point("parse_intent")
    # fan-out: both run off intent, generate_itinerary waits for both
    graph.add_edge("parse_intent", "search_flights")
    graph.add_edge("parse_intent", "search_hotels")
    graph.add_edge("search_flights", "generate_itinerary")
    graph.add_edge("search_hotels", "generate_itinerary")
    graph.add_edge("generate_itinerary", "human_confirmation")
    # fan-out again after human approval
    graph.add_edge("human_confirmation", "book_flight")
    graph.add_edge("human_confirmation", "book_hotel")
    graph.add_edge("book_flight", "summary")
    graph.add_edge("book_hotel", "summary")
    graph.add_edge("summary", END)

    return graph.compile(checkpointer=MemorySaver())