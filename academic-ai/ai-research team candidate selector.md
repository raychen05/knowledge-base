## AI Researcher Candidate Selector 


**Promtp**: 

```text
Design and implement an AI-powered Researcher Candidate Selector application.
Goal
Enable users to identify and select top research candidates based on customized search requirements for building academic or industry research teams.

Functional Requirements
1. User Input Interface:
    - Users can enter their requirements in a natural language search box (e.g., “Find AI researchers in Europe with high citation counts and experience in healthcare applications”).
    - The system uses an LLM to interpret the input, extract the search scope, selection criteria, and relevant entities (e.g., research field, region, university, metrics).
2. AI Query Construction:
    - The LLM constructs a structured query based on the extracted parameters.
    - The query is sent to the backend through a REST API.
3. Backend Services:
    - The backend APIs fetch or simulate researcher data (mock data acceptable for prototyping).
    - APIs return a ranked list of top researcher candidates according to the defined criteria.
4. Results & Team Building:
    - The UI displays a ranked candidate list with details such as name, institution, expertise, metrics, and collaboration potential.
    - Users can select candidates and add them to a team for further analysis or export.

Technical Design Requirements
- AI/NLP Layer:
    - Use an LLM (e.g., GPT-4 or similar) for intent extraction, criteria parsing, and query generation.
- Backend Framework:
    - Implement REST APIs using FastAPI or Flask.
    - Use mock data (JSON or SQLite) to simulate researcher profiles.
- Frontend Framework:
    - Develop the UI in Streamlit.
    - Provide a clean, intuitive layout with:
        1. Search input box
        2. Parsed criteria summary
        3. Results table (sortable & filterable)
        4. Candidate profile viewer
        5. “Add to team” panel
        6. Team summary view
        7. Export / Save button

Deliverables
- Recommended approach and system architecture (AI + backend + UI).
- Streamlit implementation of the prototype UI.
- A series of backend REST APIs returning mock researcher data for testing.
```

---

**ChatGPT**:

Nice — I built a complete plan plus a working single-file prototype (Streamlit frontend + FastAPI mock backend) and put the runnable code into a canvas titled "AI Researcher Candidate Selector - Streamlit + FastAPI (mock)" so you can open, run, and iterate on it.

Below I’ll summarize the recommended approach, framework choices, system architecture, UI design (7 layout options), API surface (with request/response shapes), and how the included prototype works and how to extend it for production.

---

### 1) High-level approach


- **Goal**: Let a user type natural-language requirements into a search box. An LLM parses intent (scope, filters, ranking criteria), we construct a structured query, call backend retrieval APIs, then present a ranked candidate list. User can pick candidates into a team and save/manage teams.
- **Pipeline** (production):
    1. LLM Intent Parser — parse user's free text to structured query (scope: academic/industry/all; criteria: keywords, min_h_index, recency, country/region; advanced: funding/venue experience, collaboration history). Use a small robust prompt template and validation.
    2. Query Constructor — translate parsed object into one or more backend queries:
        - Elasticsearch/BM25 for lexical filters (affiliations, region, field)
        - Vector search (FAISS/Qdrant) for semantic match on abstract/keywords/skills
        - Metadata filters (h-index, recent pubs) applied in DB or ES
    3. Candidate Scoring / Rerank — combine retrieval scores into a composite score and rerank. Optionally call a second-stage LLM reranker that ingests candidate short profiles + user intent and returns final rank & justification.
    4. Diversity & Conflict Checks — deduplicate, ensure diversity (region, career-stage), run conflict-of-interest checks (same institution/author list).
    5. UI + Team Builder — let users inspect, compare, select, and save to a team. Provide explanation per candidate (why chosen) from the reranker.
- **Core components / tech stack suggestion**
    - Frontend: Streamlit (fast prototyping) or React (production)
    - Backend: FastAPI for REST endpoints (or Flask), separate microservices for retrieval and reranking
    - Retriever stack: Elasticsearch (text & filters) + FAISS/Qdrant (vectors)
    - Embeddings: OpenAI / HuggingFace embeddings or in-house models
    - LLMs: OpenAI, Anthropic, or local LLM for parsing and reranking
    - DB: Postgres for teams, Redis for caching, S3 for profile documents
    - Orchestration: Kubernetes / Cloud run for production
    - Monitoring: Prometheus / Sentry

---

### 2) System architecture (concise)

- UI (Streamlit) ↔ API Gateway (FastAPI) ↔
    - LLM Parser Service (stateless)
    - Retriever Service (ES + Vector DB)
    - Reranker Service (LLM-based, optional)
    - Team Store (Postgres)
    - Audit & Logging (Elasticsearch / Logging backend)

---

### 3) API surface (mock / prod-ready)

(These endpoints are implemented in the included prototype as mock endpoints.)

1. POST /parse_query
    - Input: { "text": "<user natural language>" }
    - Output: { "scope": "academic|industry|any", "criteria": {...}, "filters": {...} }
    - Purpose: convert free text to structured query.
2. POST /search_candidates
    - Input: { "parsed": { ... }, "top_k": 10 }
    - Output: { "results": [ { candidate object with score }, ... ] }
    - Purpose: return ranked candidates using parsed query.
3. GET /candidate/{id}
    - Output: candidate full profile JSON.
4. POST /add_to_team
    - Input: { "team_id": "<optional>", "candidate_id": "c123" }
    - Output: { "team_id": "team_...", "members": ["c1","c2",...] }
5. GET /team/{team_id}
    - Output: team members (full candidate profiles).
6. (Optional production endpoints)
    - POST /rerank — accept top-N candidate summaries + intent, return new ordering + justification strings.
    - GET /conflicts/{candidate_id} — return conflicts (coauthors, same grant, same institution).
    - POST /feedback — user feedback (was this candidate useful?) to feed model.

---

### 4) Candidate data model (minimal)

```json
{
  "id": "c1",
  "name": "Dr. Alice Zhang",
  "affiliation": "University of Midville",
  "expertise": ["natural language processing","information retrieval"],
  "keywords": ["NLP","IR"],
  "h_index": 32,
  "recent_publications": 18,
  "region": "North America",
  "bio": "...",
  "score": 2.34
}

```

---

### 5) UI design and 7 layout variants

Each layout supports: search box, parsed query preview, filters, results list/cards, candidate detail panel, team builder (sidebar), saved teams, and export.

1. Simple List (compact)
    - Single-column: query on top → compact list of results (name, affiliation, score). Quick add buttons. Best for heavy-users.
2. Card Grid (visual)
    - Grid of cards with avatar, top 3 expertise, h-index badge, quick-add. Good when visual scanning matters.
3. Two-column Compare View
    - Left: candidate list. Right: selected candidate details. Include a “Compare” mode to select 2–4 and show side-by-side metrics.
4. Team Builder Kanban
    - Left pane candidate pool; middle columns as team roles (Lead, Co-PI, Collaborator); drag & drop candidates into roles.
5. Matrix (skills × seniority)
    - Visual 2D matrix plotting candidates by two dimensions (e.g., expertise closeness vs h-index). Click to view profile.
6. Map / Regional View
    - World map heatmap of candidate density with clustering; good if geography matters.
7. Interview / Shortlist Workflow
    - Pipeline view: Shortlist -> Contacted -> Interviewed -> Accepted. Each candidate moves through stages. Integrates email templates and calendar links.

---

### 6) Streamlit prototype (what I delivered in the canvas)


I added a runnable single-file prototype in the canvas that:

- Starts a FastAPI mock backend exposing the listed endpoints.
- Includes a Streamlit UI (streamlit_ui.py) that calls the backend:
    - Accepts a free-text query
    - Calls /parse_query then /search_candidates
    - Displays results as a list of cards and allows 'Add to team'
    - Supports showing team members via the sidebar
- Uses mock candidate data and a simple heuristic parser & scorer so you can run end-to-end locally without external APIs.

Open the canvas document titled "AI Researcher Candidate Selector - Streamlit + FastAPI (mock)" to see the code and run it locally. (It contains run instructions in the header.)

---

### 7) How to run the prototype


- Install Python dependencies: pip install fastapi uvicorn streamlit httpx pydantic
- Run the single file available in the canvas (filename and exact run instructions are included there). The file will:
    - Start FastAPI at http://127.0.0.1:8000
    - Launch Streamlit (interactive UI)

---

### 8) How to move from prototype → production

- Replace simple_parse() with a robust LLM call (carefully craft prompt and temperature; validate output schema). Add input validation & schema enforcement.
- Replace heuristic scoring with a retrieval pipeline:
    - Precompute embedding vectors for candidate profiles.
    - Use FAISS / Qdrant for vector search + ES for metadata filters.
    - Implement hybrid retrieval (combine BM25 and vector scores).
- Add a second-stage reranker (LLM) that takes top-20 candidate summaries plus the parsed intent and outputs a ranked list and a short explanation for each result.
- Add authentication, rate limiting, logging, monitoring, and tests.
- Add CI/CD, containerization, infra (K8s), and secret management (for LLM keys).

---

### 9) Extensibility & UX improvements

- Allow advanced query UI to reveal the parsed query for direct editing.
- Provide “Why this candidate?” explanations and citations (paper titles, grants).
- Add export (CSV) and integration to reference managers, calendar invites.
- Add collaborative team editing with role assignments and version history.

If you want I can:
- Walk through the code in the canvas and explain any specific function line-by-line.
- Convert the prototype into a multi-file repo (separate services, tests, Dockerfile, docker-compose).
- Swap the mock LLM parser for a real LLM prompt + example prompt templates.
- Produce React + Tailwind UI components instead of Streamlit.

Which one would you like next?

---

**ChatGPT**:

Excellent — let’s turn the single-file prototype into a clean, multi-file repo structured for real development and easy migration from mock to production.


### 📁 Repository Structure

```css
ai_researcher_selector/
│
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routers/
│   │   ├── parse.py            # /parse_query endpoint
│   │   ├── search.py           # /search_candidates endpoint
│   │   ├── candidate.py        # /candidate/{id} endpoint
│   │   ├── team.py             # /add_to_team and /team/{id}
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── parser_service.py   # Mock or real LLM parser
│   │   ├── scoring_service.py  # Candidate scoring logic
│   │   ├── data_service.py     # Mock candidate and team store
│   ├── __init__.py
│
├── frontend/
│   ├── app.py                  # Streamlit app entry point
│   ├── components/
│   │   ├── candidate_card.py   # UI component for candidate
│   │   ├── team_sidebar.py     # Sidebar to manage team
│   │   ├── query_parser_view.py# Shows parsed query
│   ├── utils/
│   │   ├── api_client.py       # HTTPX client to backend
│   ├── __init__.py
│
├── data/
│   └── mock_candidates.json    # Mock researcher data
│
├── requirements.txt
├── README.md
└── run.sh                      # Convenience launcher for backend + Streamlit
```

---

### 🧩 1. backend/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import parse, search, candidate, team

app = FastAPI(title="AI Researcher Candidate Selector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse.router)
app.include_router(search.router)
app.include_router(candidate.router)
app.include_router(team.router)

@app.get("/")
def root():
    return {"message": "Researcher Selector API running"}

```

---

### 🧩 2. backend/models/schemas.py


```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ParseRequest(BaseModel):
    text: str

class ParsedOutput(BaseModel):
    scope: Optional[str] = None
    criteria: Dict[str, Any] = {}
    filters: Dict[str, Any] = {}

class SearchRequest(BaseModel):
    parsed: ParsedOutput
    top_k: Optional[int] = 10

class Candidate(BaseModel):
    id: str
    name: str
    affiliation: str
    expertise: List[str]
    h_index: int
    recent_publications: int
    region: str
    score: float
    bio: str
    keywords: List[str]

class TeamAction(BaseModel):
    team_id: Optional[str]
    candidate_id: str


```

---


### 🧩 3. backend/services/data_service.py

```python
import json
import time

with open("data/mock_candidates.json") as f:
    MOCK_CANDIDATES = json.load(f)

MOCK_TEAMS = {}

def get_all_candidates():
    return MOCK_CANDIDATES

def get_candidate(cid: str):
    for c in MOCK_CANDIDATES:
        if c["id"] == cid:
            return c
    return None

def add_to_team(team_id: str, candidate_id: str):
    tid = team_id or f"team_{int(time.time())}"
    if tid not in MOCK_TEAMS:
        MOCK_TEAMS[tid] = []
    if candidate_id not in MOCK_TEAMS[tid]:
        MOCK_TEAMS[tid].append(candidate_id)
    return tid, MOCK_TEAMS[tid]

def get_team(tid: str):
    from .data_service import get_candidate
    members = MOCK_TEAMS.get(tid, [])
    return [get_candidate(cid) for cid in members if get_candidate(cid)]

```

---


### 🧩 4. backend/services/parser_service.py

```python
import re
from models.schemas import ParsedOutput

def simple_parse(text: str) -> ParsedOutput:
    out = ParsedOutput()
    txt = text.lower()
    if "industry" in txt:
        out.scope = "industry"
    elif "academic" in txt or "university" in txt:
        out.scope = "academic"
    else:
        out.scope = "any"

    words = re.findall(r"[a-zA-Z0-9\\-]+", txt)
    stops = {"and", "or", "with", "for", "of", "the", "to"}
    keywords = [w for w in words if w not in stops and len(w) > 2]
    m = re.search(r"h[- ]?index\\s*(?:>|>=)\\s*(\\d+)", txt)
    if m:
        out.criteria["min_h_index"] = int(m.group(1))
    for r in ["north america", "europe", "asia"]:
        if r in txt:
            out.filters["region"] = r.title()
    out.criteria["keywords"] = keywords[:5]
    return out

```

---

### 🧩 5. backend/services/scoring_service.py

```python
from difflib import SequenceMatcher

def score_candidate(parsed, cand):
    score = 0.0
    search_kw = [k.lower() for k in parsed.criteria.get("keywords", [])]
    kw_overlap = sum(1 for k in cand.get("keywords", []) if k.lower() in search_kw)
    score += kw_overlap * 2.0
    exp_overlap = sum(1 for e in cand.get("expertise", []) if any(e.lower().find(k) != -1 for k in search_kw))
    score += exp_overlap * 1.5
    if parsed.criteria.get("min_h_index"):
        if cand.get("h_index", 0) >= parsed.criteria["min_h_index"]:
            score += 3.0
    if parsed.filters.get("region") and cand.get("region", "").lower() == parsed.filters["region"].lower():
        score += 1.0
    for token in search_kw:
        score += SequenceMatcher(None, token, cand.get("affiliation", "").lower()).ratio() * 0.3
    return round(score, 3)

```

---

### 🧩 6. backend/routers/parse.py

```python
from fastapi import APIRouter
from models.schemas import ParseRequest
from services.parser_service import simple_parse

router = APIRouter(prefix="/parse_query", tags=["parse"])

@router.post("")
async def parse_query(req: ParseRequest):
    parsed = simple_parse(req.text)
    return parsed.dict()

```

---

### 🧩 7. backend/routers/search.py


```python
from fastapi import APIRouter
from models.schemas import SearchRequest
from services.data_service import get_all_candidates
from services.scoring_service import score_candidate

router = APIRouter(prefix="/search_candidates", tags=["search"])

@router.post("")
async def search_candidates(req: SearchRequest):
    parsed = req.parsed
    results = []
    for c in get_all_candidates():
        s = score_candidate(parsed, c)
        c2 = c.copy()
        c2["score"] = s
        results.append(c2)
    if parsed.filters.get("region"):
        results = [r for r in results if r.get("region", "").lower() == parsed.filters["region"].lower()]
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return {"results": results[:req.top_k]}

```

---

### 🧩 8. backend/routers/candidate.py

```python
from fastapi import APIRouter, HTTPException
from services.data_service import get_candidate

router = APIRouter(prefix="/candidate", tags=["candidate"])

@router.get("/{cid}")
async def get_candidate_endpoint(cid: str):
    c = get_candidate(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c


```

---


🧩 9. backend/routers/team.py


```python
from fastapi import APIRouter
from models.schemas import TeamAction
from services.data_service import add_to_team, get_team

router = APIRouter(prefix="/team", tags=["team"])

@router.post("/add")
async def add_team(action: TeamAction):
    tid, members = add_to_team(action.team_id, action.candidate_id)
    return {"team_id": tid, "members": members}

@router.get("/{tid}")
async def get_team_members(tid: str):
    members = get_team(tid)
    return {"team_id": tid, "members": members}

```

---

### 🧩 10. frontend/app.py (Streamlit)

```python
import streamlit as st
import httpx
from components.candidate_card import show_candidate_card
from components.team_sidebar import show_team_sidebar
from components.query_parser_view import show_parsed

st.set_page_config(layout="wide", page_title="AI Researcher Selector")

st.title("AI-powered Researcher Candidate Selector")

show_team_sidebar()

query = st.text_input("Describe your ideal researcher (e.g. NLP expert in North America with h-index > 30)")
if st.button("Find candidates"):
    with st.spinner("Parsing query..."):
        parsed = httpx.post("http://127.0.0.1:8000/parse_query", json={"text": query}).json()
    show_parsed(parsed)
    with st.spinner("Searching candidates..."):
        resp = httpx.post("http://127.0.0.1:8000/search_candidates", json={"parsed": parsed, "top_k": 10}).json()
    for cand in resp.get("results", []):
        show_candidate_card(cand)

```

---


### 🧩 11. frontend/components/candidate_card.py

```python
import streamlit as st
import httpx

def show_candidate_card(cand):
    cols = st.columns([1, 4, 1])
    with cols[0]:
        st.image("https://via.placeholder.com/80", width=80)
    with cols[1]:
        st.subheader(cand["name"])
        st.write(cand["affiliation"])
        st.write(f"Expertise: {', '.join(cand['expertise'])}")
        st.write(f"h-index: {cand['h_index']} | Score: {cand['score']}")
        st.write(cand["bio"])
    with cols[2]:
        if st.button(f"Add {cand['id']}"):
            httpx.post("http://127.0.0.1:8000/team/add", json={"team_id": None, "candidate_id": cand["id"]})
            st.success(f"Added {cand['name']} to team")

```

---

🧩 12. frontend/components/team_sidebar.py

```python
import streamlit as st
import httpx

def show_team_sidebar():
    with st.sidebar:
        st.header("Team Builder")
        team_id = st.text_input("Team ID")
        if st.button("Show Team"):
            if team_id:
                r = httpx.get(f"http://127.0.0.1:8000/team/{team_id}").json()
                st.write(r)
            else:
                st.warning("Enter a team ID first")

```

---

### 🧩 13. frontend/components/query_parser_view.py


```python
import streamlit as st

def show_parsed(parsed):
    with st.expander("Parsed Query"):
        st.json(parsed)

```

---


### 🧩 14. data/mock_candidates.json

Same data as before (4 mock candidates).

---

### 🧩 15. requirements.txt

```nginx
fastapi
uvicorn
pydantic
httpx
streamlit
```

---

### 🧩 16. run.sh

```bash
#!/bin/bash
uvicorn backend.main:app --reload --port 8000 &
sleep 2
streamlit run frontend/app.py

```

---

### 🚀 Run Instructions


```bash
git clone <your-repo>
cd ai_researcher_selector
pip install -r requirements.txt
bash run.sh

```

Then open http://localhost:8501 in your browser.

Would you like me to:
- ✅ generate this as a downloadable GitHub-ready zip repo (with all files created)?
- or 🧠 extend it to include LLM-based reranker + justification generator next?


---


## 🧠 AI Researcher Candidate Selector (Streamlit + FastAPI)

This version replaces the mock LLM parser with a **real LLM prompt-based parser*- using OpenAI (or any LLM provider via LangChain). The LLM interprets user input, extracts entities and criteria, and constructs structured search parameters for the backend API.

---

### 🗂️ Repo Structure

```css
ai_researcher_selector/
│
├── backend/
│   ├── main.py                # FastAPI app (mock data + endpoints)
│   ├── schemas.py             # Pydantic models
│   ├── mock_data.py           # Mock researcher records
│   ├── llm_parser.py          # Real LLM prompt-based parser
│
├── frontend/
│   ├── app.py                 # Streamlit UI
│
├── prompts/
│   ├── researcher_query_prompt.txt   # Prompt template
│
├── requirements.txt
└── README.md
```

---

### ⚙️ Backend (`backend/main.py`)

```python
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .schemas import Researcher, ParsedQuery
from .mock_data import MOCK_RESEARCHERS
from .llm_parser import parse_user_query

app = FastAPI(title="AI Researcher Candidate Selector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/parse_query", response_model=ParsedQuery)
def parse_query(input_text: str):
    return parse_user_query(input_text)

@app.get("/search_researchers", response_model=List[Researcher])
def search_researchers(field: str = Query(None), keywords: str = Query(None), region: str = Query(None)):
    results = [r for r in MOCK_RESEARCHERS if (not field or field.lower() in r.field.lower()) and (not region or region.lower() in r.region.lower())]
    return results[:20]
```

---

### 🧩 `schemas.py`

```python
from pydantic import BaseModel
from typing import Optional

class Researcher(BaseModel):
    id: int
    name: str
    field: str
    institution: str
    region: str
    h_index: int

class ParsedQuery(BaseModel):
    field: Optional[str]
    keywords: Optional[str]
    region: Optional[str]
```

---


### 🧠 `llm_parser.py`


```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.chains import LLMChain
from pathlib import Path
import os


# Load template
PROMPT_PATH = Path(__file__).parent.parent / "prompts/researcher_query_prompt.txt"
TEMPLATE = PROMPT_PATH.read_text()


# Define schema for structured parsing
schemas = [
ResponseSchema(name="field", description="Main research field or discipline"),
ResponseSchema(name="keywords", description="Key topics or techniques to search for"),
ResponseSchema(name="region", description="Region or country preference, if mentioned"),
]


parser = StructuredOutputParser.from_response_schemas(schemas)
prompt = PromptTemplate(
template=TEMPLATE + "\n{format_instructions}\nUser query: {query}",
input_variables=["query"],
partial_variables={"format_instructions": parser.get_format_instructions()},
)


llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
chain = LLMChain(llm=llm, prompt=prompt)


def parse_user_query(input_text: str):
response = chain.run(query=input_text)
parsed = parser.parse(response)
return parsed
```


### 🧾 Prompt Template (`prompts/researcher_query_prompt.txt`)


```
You are an intelligent assistant that interprets user input to find suitable researcher candidates.
Given a free-form user input describing a need for researchers, extract and structure the following:
- Field or discipline (e.g., machine learning, bioinformatics)
- Specific keywords or research topics
- Region or country preference (if any)


Return your output strictly in JSON format following the instructions below.
```

---


### 🧪 Mock Data (`mock_data.py`)


```python
MOCK_RESEARCHERS = [
{"id": 1, "name": "Dr. Alice Chen", "field": "Machine Learning", "institution": "Stanford University", "region": "USA", "h_index": 48},
{"id": 2, "name": "Dr. Ravi Kumar", "field": "AI Ethics", "institution": "IIT Delhi", "region": "India", "h_index": 32},
{"id": 3, "name": "Dr. Maria Lopez", "field": "Bioinformatics", "institution": "University of Barcelona", "region": "Spain", "h_index": 41},
]
```


---

### 💡 Streamlit Frontend (`frontend/app.py`)


```python
import streamlit as st
import requests


API_BASE = "http://localhost:8000"


st.set_page_config(page_title="AI Researcher Selector", layout="wide")


st.title("🔍 AI-Powered Researcher Candidate Selector")


user_input = st.text_area("Describe the kind of researcher you’re looking for:",
placeholder="Example: Find AI researchers in Europe with experience in medical image analysis")


if st.button("Find Candidates"):
with st.spinner("Analyzing your request..."):
parsed = requests.get(f"{API_BASE}/parse_query", params={"input_text": user_input}).json()
results = requests.get(f"{API_BASE}/search_researchers", params=parsed).json()


st.subheader("Top Matching Researchers")
for r in results:
with st.container():
st.markdown(f"**{r['name']}** — {r['field']} ")
st.caption(f"{r['institution']} | {r['region']} | H-index: {r['h_index']}")
st.button(f"Add {r['name']} to Team", key=r['id'])
```

---

### 🧰 Example `.env`


```
OPENAI_API_KEY=sk-...
```

---
### 🧪 Run Instructions


```bash
cd ai_researcher_selector
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```

---

### ✅ Summary


This upgraded version:
- Uses a **real LLM (ChatOpenAI)** to parse user intent.
- Separates logic into modular backend and frontend files.
- Supports **future extension** (e.g., real researcher DB, Elasticsearch).
- Provides **example prompt template** for structured extraction.
- Ready for deployment or RAG integration with real academic data sources.


The prototype now uses a real LLM-based parser (via LangChain + structured prompt template) instead of mock logic. It includes modular files, a prompt schema, and an end-to-end setup for Streamlit + FastAPI integration. Would you like me to extend this to support LLM-based explanation generation for top researcher rankings next?


---


**ChatGPT**:


Great — I extended the repo to add an LLM-based reranker + justification generator. Below you’ll find the design plus ready-to-drop-in code for the backend (reranker service + router), the prompt template, and the frontend changes to call the reranker and show justifications.

I focused on a safe, production-friendly pattern:
- Retriever returns a top-N candidate set (fast, deterministic).
- Reranker LLM receives: parsed user intent + flattened candidate summaries.
- LLM returns a JSON array of {id, score, justification} where:
    - score is normalized (0.0–1.0),
    - justification is a short human-readable explanation (1–3 sentences).
- Backend merges reranker output with full candidate objects and returns final ranked list to the UI.

---

### What to add (files & short explanation)


#### 1) backend/llm_reranker.py — LLM chain to rerank & justify

```python
# backend/llm_reranker.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
from pathlib import Path
import os

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "reranker_prompt.txt"
PROMPT_TEMPLATE = PROMPT_PATH.read_text()

# Use low temperature for deterministic ranking
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

prompt = PromptTemplate(
    input_variables=["query_summary", "candidates_json"],
    template=PROMPT_TEMPLATE
)

chain = LLMChain(llm=llm, prompt=prompt)

def rerank_and_justify(parsed_query: dict, candidates: list):
    """
    parsed_query: dict produced by the parser endpoint (field/keywords/region/...)
    candidates: list of candidate dicts (id, name, affiliation, expertise, h_index, short_bio, ...)
    Returns list of {id, score (0-1), justification} in descending order of score
    """
    # Build compact candidate summaries for LLM
    candidates_for_llm = []
    for c in candidates:
        candidates_for_llm.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "affiliation": c.get("affiliation"),
            "expertise": c.get("expertise"),
            "h_index": c.get("h_index"),
            "bio": c.get("bio", "")[:400]  # keep prompt short
        })

    # Provide query_summary as a short string description
    q_parts = []
    if parsed_query.get("scope"):
        q_parts.append(f"scope: {parsed_query['scope']}")
    if parsed_query.get("criteria"):
        q_parts.append("criteria: " + ", ".join(f"{k}={v}" for k,v in parsed_query['criteria'].items()))
    if parsed_query.get("filters"):
        q_parts.append("filters: " + ", ".join(f"{k}={v}" for k,v in parsed_query['filters'].items()))
    query_summary = "; ".join(q_parts) or ""

    # Run LLM chain
    candidates_json = json.dumps(candidates_for_llm, ensure_ascii=False)
    resp = chain.run(query_summary=query_summary, candidates_json=candidates_json)

    # Expect resp to be an explicit JSON array string. Try to parse
    try:
        parsed = json.loads(resp)
        # Validate structure: list of objects {id, score, justification}
        out = []
        for item in parsed:
            out.append({
                "id": item.get("id"),
                "score": float(item.get("score")),
                "justification": item.get("justification", "")
            })
        # sort by score desc
        out = sorted(out, key=lambda x: x["score"], reverse=True)
        return out
    except Exception as e:
        # Fallback: if LLM didn't emit strict JSON, attempt to extract JSON substring
        import re
        m = re.search(r"(\[.*\])", resp, flags=re.S)
        if m:
            try:
                parsed = json.loads(m.group(1))
                out = []
                for item in parsed:
                    out.append({
                        "id": item.get("id"),
                        "score": float(item.get("score")),
                        "justification": item.get("justification", "")
                    })
                return sorted(out, key=lambda x: x["score"], reverse=True)
            except Exception:
                raise RuntimeError(f"Failed to parse LLM response as JSON. raw:\n{resp}") from e
        raise RuntimeError(f"Failed to parse LLM response as JSON. raw:\n{resp}") from e

```

**Notes**:
- gpt-4o-mini used as example — replace with whichever model/provider you use.
- Keep LLM temperature low for deterministic ranking.
- We do basic robust JSON parsing with a fallback to extract bracketed JSON.

---

#### 2) prompts/reranker_prompt.txt — Reranker prompt

```swift
You are a strict JSON-output generator. Given a short summary of a user's researcher requirements and a JSON array of candidate summaries, produce a JSON array where each entry has the following fields:

- id: the candidate id (string/int) from the input list
- score: a float between 0.0 and 1.0 (higher is better). Score should reflect suitability relative to other provided candidates.
- justification: 1-3 short sentences (max ~40 words) explaining why the candidate matches the user needs.

Make decisions based ONLY on the information provided in `candidates_json` and the `query_summary`. Do not add external facts.

Return ONLY the JSON array and nothing else.

Query summary:
{query_summary}

Candidates (JSON array):
{candidates_json}

Output format example:
[
  {"id": "c1", "score": 0.92, "justification": "Strong match on keywords X and Y; h-index 45; recent papers in relevant venue."},
  {"id": "c2", "score": 0.72, "justification": "Relevant expertise but lower h-index and fewer recent publications."}
]
```

---

#### 3) backend/routers/rerank.py — FastAPI router

```python
# backend/routers/rerank.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.llm_reranker import rerank_and_justify
from backend.services.data_service import get_candidate

router = APIRouter(prefix="/rerank", tags=["rerank"])

class RerankRequest(BaseModel):
    parsed: Dict[str, Any]
    candidates: List[Dict[str, Any]]  # top-N from retriever

@router.post("")
async def rerank(req: RerankRequest):
    try:
        reranked = rerank_and_justify(req.parsed, req.candidates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Merge with full candidate records if available
    merged = []
    for item in reranked:
        cid = item["id"]
        full = next((c for c in req.candidates if c.get("id") == cid), None)
        if full is None:
            # try to fetch full record from data store
            full = get_candidate(cid)
        merged_item = full.copy() if full else {"id": cid}
        merged_item["score"] = item["score"]
        merged_item["justification"] = item["justification"]
        merged.append(merged_item)
    return {"results": merged}

```

Place under backend/routers/ and include in backend/main.py routers.

---

#### 4) Frontend changes (frontend/app.py) — call reranker after search


Replace the portion after initial search with a call to /rerank. Minimal change:

```python
# after you have `resp` from /search_candidates or /search_researchers
top_candidates = resp.get("results", [])
# Call reranker
r = httpx.post("http://127.0.0.1:8000/rerank", json={"parsed": parsed, "candidates": top_candidates}).json()
final = r.get("results", [])
st.subheader("Reranked results (LLM justification)")
for cand in final:
    with st.container():
        st.markdown(f"**{cand['name']}** — {cand.get('affiliation','')}")
        st.caption(f"H-index: {cand.get('h_index','N/A')} | Score: {cand.get('score')}")
        st.write(cand.get("justification", ""))
        if st.button(f"Add {cand['id']} to Team", key=f"add_{cand['id']}"):
            httpx.post("http://127.0.0.1:8000/team/add", json={"team_id": None, "candidate_id": cand["id"]})
            st.success("Added")

```

---

#### 5) Requirements additions (requirements.txt)

Add these lines (or install them):

```sell
langchain>=0.1
openai
tiktoken
python-dotenv
```

(Also keep fastapi uvicorn httpx streamlit pydantic from before.)

Set your environment variable:
```ini
OPENAI_API_KEY=sk-...
```
(Or your provider equivalent; LangChain supports multiple providers.)

---

#### 6) Security, cost & reliability notes

- Costs — Reranker runs an LLM per query. Consider:
    - calling reranker only after user explicitly requests (e.g., “Refine & Rerank”),
    - using a smaller or cheaper model for reranking,
    - caching reranker outputs for repeated searches.
- Determinism — Use low temperature (0.0) to keep rankings consistent.
- Prompt safety — The prompt instructs the model to rely only on given data; however still log & monitor LLM outputs.
- Latency — LLM calls add latency. Consider:
    - returning fast retriever results immediately and showing they are being reranked in background (but you requested no async/promise behavior — so in the prototype we block until rerank completes). For production, consider async UX.
- Rate limits — Add retries/backoff and circuit breaker for LLM calls.

---

#### 7) Run / test locally


1. Install requirements:
```bash
pip install -r requirements.txt
```
2. Ensure environment:
```bash
export OPENAI_API_KEY="sk-..."
```
3. Start backend:
```bash
uvicorn backend.main:app --reload --port 8000
```
4. Start Streamlit UI:
```bash
streamlit run frontend/app.py
```

Type a query in the Streamlit UI (e.g., "Senior NLP researcher in Europe, medical imaging experience, h-index > 30"). Flow:
- Frontend -> /parse_query -> structured parsed query
- Frontend -> /search_candidates -> initial top-N
- Frontend -> /rerank -> LLM reranker returns final ranking + justifications

---

#### 8) Optional improvements & next steps

- Add a second-stage evidence retriever: include 1–2 paper titles and links per candidate for justifications so LLM can cite evidence (requires integrating RAG).
- Add a confidence or explainability flag for the LLM to surface when it’s guessing.
- Add monitoring/alerting around LLM latency / hallucination rates.
- Implement a cheaper fallback model when quotas are hit.
- Add structured schema enforcement (e.g., use ResponseSchema / StructuredOutputParser) to avoid JSON parse issues — the current implementation expects JSON output and has a robust fallback parse.

If you want, I can now:
- implement these files directly into the repo and produce a zip / GitHub-ready repository,
- or switch the reranker to use a structured parser (StructuredOutputParser) so responses are strongly validated,
- or add the evidence-citation step (returning 1–2 paper titles per justification) and show them in the UI.
Which of those would you like me to do next?

---

What's next? I can:
- push this to a GitHub repo (I can generate the git commands and a README),
- swap LangChain -> direct OpenAI calls (if you prefer),
- add Dockerfile(s) and docker-compose for easy local deployment,
- add unit tests / CI config. 





