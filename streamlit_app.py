"""
Streamlit UI for the travel multi-agent pipeline. Talks to graph.py
directly (not through app.py/FastAPI) — simpler for a live demo, one
process instead of two. app.py stays as the documented API-served
version of the same graph, worth mentioning as a deliberate choice in
an interview: same orchestration logic, two different serving layers.
 
Run: streamlit run streamlit_app.py
"""
import uuid
import streamlit as st
from langgraph.types import Command
from graph import build_graph
 
st.set_page_config(page_title="AI Travel Planner", page_icon="\u2708\ufe0f", layout="wide")
 
# Rough, fixed display-only conversion — Duffel is returning prices in
# EUR for this account/locale rather than INR. Not a live FX rate;
# labeled as approximate so it's not misleading in a demo.
EUR_TO_INR_APPROX = 90.0
 
 
@st.cache_resource
def get_graph():
    return build_graph()
 
 
graph = get_graph()
 
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "result" not in st.session_state:
    st.session_state.result = None
 
st.title("\u2708\ufe0f AI Travel Planner")
st.caption(
    "Multi-agent flight + hotel booking with an AI-generated itinerary — "
    "orchestrated with LangGraph, running entirely on local LLMs via Ollama."
)
 
config = {"configurable": {"thread_id": st.session_state.thread_id}}
 
# ---------------------------------------------------------------- INPUT
if st.session_state.stage == "input":
    query = st.text_area(
        "Describe your trip",
        placeholder="e.g. I want to fly from Mumbai to Goa on 15th September, "
                    "coming back on 18th, for 2 people, I like beaches",
        height=100,
    )
    if st.button("Plan my trip", type="primary"):
        if not query.strip():
            st.warning("Enter a trip request first.")
        else:
            status_box = st.status("🧠 AI Agents actively working...", expanded=True)
            status_box.write("Step 1/3: Extracting trip intent with local LLM...")
            
            # Stream graph updates step by step
            for chunk in graph.stream({"user_query": query}, config=config, stream_mode="values"):
                if "intent" in chunk and "flight_offers" not in chunk:
                    status_box.write("Step 2/3: Searching flights & hotels in parallel...")
                elif "flight_offers" in chunk and "itinerary" not in chunk:
                    status_box.write("Step 3/3: Generating RAG itinerary with destination knowledge...")
            
            # Retrieve current graph state
            state_snapshot = graph.get_state(config)
            result = state_snapshot.values
            
            status_box.update(label="✅ Planning complete!", state="complete", expanded=False)
            st.session_state.result = result
            st.session_state.stage = "review"
            st.rerun()
 
# ---------------------------------------------------------------- REVIEW
elif st.session_state.stage == "review":
    result = st.session_state.result
    intent = result["intent"]
 
    st.subheader("Trip details")
    cols = st.columns(4)
    cols[0].metric("From", intent["origin"])
    
    # Show destination IATA and mapped city if available
    dest_code = intent["destination"]
    from validators import IATA_TO_CITY
    dest_display = f"{dest_code} ({IATA_TO_CITY[dest_code]})" if dest_code in IATA_TO_CITY else dest_code
    
    cols[1].metric("To", dest_display)
    cols[2].metric("Depart", intent["depart_date"])
    cols[3].metric("Return", intent["return_date"] or "\u2014")
 
    if result.get("intent_warnings"):
        st.warning(f"The model flagged some uncertainty on this request: {result['intent_warnings']}")
 
    st.subheader("\u2708\ufe0f Flight options")
    for f in result["flight_offers"]:
        try:
            price_eur = float(f["price"])
            price_inr_approx = price_eur * EUR_TO_INR_APPROX
            price_display = f"\u20ac{price_eur:.2f} (~\u20b9{price_inr_approx:,.0f}, approx.)"
        except (TypeError, ValueError):
            price_display = f"{f['price']} {f['currency']}"
        st.write(
            f"**{f['airline']}** — {price_display} — "
            f"{f['depart_time']} \u2192 {f['arrive_time']} ({f['stops']} stop(s))"
        )
 
    st.subheader("\U0001F3E8 Hotel options")
    for h in result["hotel_offers"]:
        stars = "\u2b50" * (h.get("rating") or 0)
        st.write(f"**{h['name']}** {stars} — \u20b9{h['price_per_night']:,.0f}/night — {h['address']}")
 
    st.subheader("\U0001F5FA\ufe0f Itinerary")
    for day in result["itinerary"]["days"]:
        with st.expander(f"Day {day['day_number']}: {day['theme']}"):
            for act in day["activities"]:
                st.write(f"- {act}")
 
    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("\u2705 Confirm & book", type="primary"):
        with st.spinner("Booking..."):
            final = graph.invoke(Command(resume={"approved": True}), config=config)
        st.session_state.result = final
        st.session_state.stage = "done"
        st.rerun()
    if col2.button("\u274c Cancel"):
        with st.spinner("Cancelling..."):
            final = graph.invoke(Command(resume={"approved": False}), config=config)
        st.session_state.result = final
        st.session_state.stage = "done"
        st.rerun()
 
# ---------------------------------------------------------------- DONE
elif st.session_state.stage == "done":
    result = st.session_state.result
    if result.get("approved"):
        st.success("Trip booked! (mock confirmation — no real charge or ticket issued)")
        st.write(f"**Flight reference:** {result['flight_booking']['reference']}")
        st.write(f"**Hotel reference:** {result['hotel_booking']['reference']}")
    else:
        st.info("Booking cancelled — nothing was booked.")
 
    if st.button("Plan another trip"):
        st.session_state.stage = "input"
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.result = None
        st.rerun()