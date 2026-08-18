"""
FastAPI wrapper around the LangGraph graph. Two endpoints:
  POST /trip/start   -> runs until the human_confirmation interrupt, returns the pending state
  POST /trip/confirm -> resumes with the user's approve/reject decision, returns the final result
 
Run: uvicorn app:app --reload
"""
from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.types import Command
 
from graph import build_graph
 
app = FastAPI(title="Travel Multi-Agent API")
graph = build_graph()
 
 
class StartRequest(BaseModel):
    query: str
    thread_id: str = "default"
 
 
class ConfirmRequest(BaseModel):
    approved: bool
    thread_id: str = "default"
 
 
@app.post("/trip/start")
def start_trip(req: StartRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke({"user_query": req.query}, config=config)
    # When interrupted, LangGraph surfaces the interrupt payload under
    # "__interrupt__" in the result rather than raising — check for it.
    return result
 
 
@app.post("/trip/confirm")
def confirm_trip(req: ConfirmRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke(Command(resume={"approved": req.approved}), config=config)
    return result