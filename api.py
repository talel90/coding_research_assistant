"""
FastAPI wrapper around the existing Tools Digger Workflow (src/workflow.py).

Run locally:
    uvicorn api:app --reload --port 8000

Then POST to http://localhost:8000/research with {"query": "..."}
Docs are auto-generated at http://localhost:8000/docs
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.workflow import Workflow  # your existing LangGraph workflow

app = FastAPI(title="Tools Digger API")

# --- CORS -------------------------------------------------------------
# Needed only if the frontend is hosted on a DIFFERENT origin than this API
# (e.g. frontend on Netlify, API on Render). If you serve the frontend
# from this same FastAPI app (see bottom of file / the notes below),
# you can remove this middleware entirely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your real frontend domain before going live
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Build the workflow once at startup, reuse it across requests.
workflow = Workflow()


# --- Schemas ------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str


class ToolOut(BaseModel):
    name: str
    website: Optional[str] = None
    pricing: Optional[str] = None
    open_source: Optional[bool] = None
    api_available: Optional[bool] = None
    tech_stack: List[str] = []
    languages: List[str] = []
    integrations: List[str] = []


class ResearchResponse(BaseModel):
    query: str
    tools: List[ToolOut]
    recommendation: str


# --- Routes ---------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/research", response_model=ResearchResponse)
def research(payload: QueryRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        state = workflow.run(query)
    except Exception as exc:  # keep the frontend from hanging on a stack trace
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # NOTE: adjust these attribute names to match your actual
    # CompanyInfo / ResearchState fields in src/models.py.
    tools_out = [
        ToolOut(
            name=c.name,
            website=getattr(c, "website", None),
            pricing=getattr(c, "pricing_model", None),
            open_source=getattr(c, "is_open_source", None),
            api_available=getattr(c, "has_api", None),
            tech_stack=getattr(c, "tech_stack", []) or [],
            languages=getattr(c, "languages", []) or [],
            integrations=getattr(c, "integrations", []) or [],
        )
        for c in state.companies
    ]

    return ResearchResponse(
        query=query,
        tools=tools_out,
        recommendation=getattr(state, "analysis", "") or "",
    )


# --- Optional: serve the frontend from this same app ----------------------
# Uncomment this once you drop tools-digger.html into a ./static folder.
# This makes the whole thing ONE deployable service, no CORS needed at all.
#
# from fastapi.staticfiles import StaticFiles
# app.mount("/", StaticFiles(directory="static", html=True), name="frontend")
