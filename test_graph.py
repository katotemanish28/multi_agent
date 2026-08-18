"""
Day 2 checkpoint script — runs the whole graph end-to-end, including
the interrupt/resume flow, without needing FastAPI or Streamlit yet.

    python test_graph.py
"""
import json
from langgraph.types import Command
from graph import build_graph

graph = build_graph()
config = {"configurable": {"thread_id": "test-1"}}

print("=" * 60)
print("Starting graph with a sample query...")
print("=" * 60)

result = graph.invoke(
    {"user_query": "I want to fly from Mumbai to Goa on 15th September, coming back on 18th, for 2 people, I like beaches"},
    config=config,
)

print("\n--- State after first run (should be paused at human_confirmation) ---")
print(json.dumps(result, indent=2, default=str))

if "__interrupt__" in result:
    print("\n" + "=" * 60)
    print("Graph is paused, waiting for human confirmation.")
    print("Simulating user approval...")
    print("=" * 60)

    final_result = graph.invoke(Command(resume={"approved": True}), config=config)
    print("\n--- Final state after approval ---")
    print(json.dumps(final_result, indent=2, default=str))
    print("\n--- Summary ---")
    print(final_result.get("summary"))
else:
    print("\nNo interrupt found — check that graph.py's human_confirmation node ran as expected.")