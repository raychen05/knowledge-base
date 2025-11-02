

## Streamlit Project Skeleton for Multi-subproject App 


Perfect 🔥 — here’s a complete, scalable Streamlit project skeleton for your multi-subproject app (academic-agent) — including:

- ✅ modular navigation (sidebar → loads sub-apps dynamically)
- ✅ isolated sub-project folders (academic-compass, researcher-selector, team-builder, impact-analyzer)
- ✅ shared utils/global_state.py for global session handling
- ✅ support for advanced UI (dynamic tabs, typeahead search)
- ✅ future extensibility for backend integration


---

### 🧱 Folder Structure

```css
academic-agent/
│
├── app.py                     # Main navigation + launcher
├── backend/
│   └── main.py                # (Optional) FastAPI backend
│
├── components/
│   ├── ui_helpers.py          # Shared UI helpers (cards, tables, etc.)
│   └── searchbox.py           # Custom Streamlit search component
│
├── utils/
│   ├── global_state.py        # Global session state manager
│   └── api_client.py          # Call LLM or profile APIs
│
├── academic_compass/
│   └── app.py
│
├── researcher_selector/
│   └── app.py
│
├── team_builder/
│   └── app.py
│
└── impact_analyzer/
    └── app.py

```

---

### 🧭 app.py (root launcher)

```python

st.set_page_config(page_title="Academic Agent", layout="wide")

# Initialize global state
global_state.init_globals()

st.sidebar.title("🎓 Academic Agent")
menu = st.sidebar.radio(
    "Choose an agent:",
    [
        "🧑‍🔬 Researcher Selector",
        "👥 Team Builder",
        "👥 Academic UI",
        "📘 Academic Compass",
        "📈 Impact Analyzer",
        "📄 Research Assistant",
        "🧠 Expert Finder",
    ]
)

st.sidebar.markdown("---")

# Map menu to sub-apps
module_map = {
    "🧑‍🔬 Researcher Selector": "researcher-selector.app",
    "👥 Team Builder": "team-builder.app",
    "👥 Academic UI": "academic-ui.app",
    "📘 Academic Compass": "academic-compass.app",
    "📈 Impact Analyzer": "impact-analysis.app",
    "📄 Research Assistant": "research-assistant.app",
    "🧠 Expert Finder": "expert-finder.app",
}

selected_module = module_map[menu]
subapp = importlib.import_module(selected_module)

# Run selected app
subapp.render()
```

To implement **render()** function in the file **app.py** for each sub project (e.g. academic-compass)


---

### 🌍 utils/global_state.py


```python
import streamlit as st

def init():
    """Initialize all global session variables."""
    defaults = {
        "selected_authors": [],
        "selected_topics": [],
        "display_to_author": {},
        "display_to_topic": {},
        "summary": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def get(key):
    return st.session_state.get(key)

def set(key, value):
    st.session_state[key] = value

def clear(key):
    if key in st.session_state:
        del st.session_state[key]

def has(key):
    return key in st.session_state and bool(st.session_state[key])

```

💡 **Benefits**
-	No direct access to st.session_state outside global_state.py.
-	Automatically prevents duplicates.
-   Automatically initializes the list if it doesn’t exist.
-	Centralizes list management for data.
-	Cleaner, more maintainable, and consistent with  list handling.
-	Keeps all session-state logic centralized in global_state.py


---

### 🔍 Example Sub-App — researcher_selector/app.py

```python
import streamlit as st
from utils import global_state
from components.searchbox import st_searchbox
from components.ui_helpers import display_key_value_cards

def render():
    st.title("🧑‍🔬 Researcher Selector")

    # Mock search function
    def search_authors(query: str):
        return [f"Author {i}" for i in range(1, 6) if query.lower() in f"author {i}".lower()]

    selected_author = st_searchbox(
        search_function=search_authors,
        placeholder="Search authors...",
        key="author_search"
    )

    if selected_author and selected_author not in global_state.get("selected_authors"):
        global_state.get("selected_authors").append({"name": selected_author})

    # Tabs for selected authors
    authors = global_state.get("selected_authors")
    if authors:
        tabs = st.tabs([f"🧠 {a['name']}" for a in authors])
        for i, tab in enumerate(tabs):
            with tab:
                display_key_value_cards({
                    "Name": authors[i]["name"],
                    "Expertise": "Biomedical Research",
                    "Impact": "High"
                })

```

**Sub-project Guidelines**

1.	Each sub-project has its own app.py and implements run_app() function.
2.	Can have a components/ folder for reusable UI pieces.
3.	All global/shared data goes through utils/global_state.py.
4.	main.py handles navigation via sidebar radio or buttons.


**Benefits**

-	Modular: easy to add/remove sub-projects.
-	Centralized session/global state (global_state.py).
-	Dynamic loading via import_module, avoids repetitive imports.
-	Each sub-project self-contained: can run its own UI independently.

---

### 💡 components/ui_helpers.py

```python
import streamlit as st

def display_key_value_cards(data: dict):
    """Show key-value pairs in a single styled card."""
    card_html = """
    <style>
    .flashcard {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        font-family: 'Inter', sans-serif;
    }
    .card-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
    .card-key { font-weight: 600; color: #2c3e50; }
    .card-value { color: #34495e; }
    </style>
    <div class="flashcard">
    """
    for k, v in data.items():
        card_html += f'<div class="card-row"><div class="card-key">{k}</div><div class="card-value">{v}</div></div>'
    card_html += "</div>"
    st.markdown(card_html, unsafe_allow_html=True)
```

---

### 🧠 Dynamic Tabs Example (for any sub-project)

```python
sections = {
    "Overview": "Summary of research focus areas.",
    "Publications": "Top 5 most cited works.",
    "Collaborations": "Partner institutions worldwide."
}

tabs = st.tabs(list(sections.keys()))
for i, section in enumerate(sections):
    with tabs[i]:
        st.markdown(f"### {section}")
        st.info(sections[section])

```

---

### 🚀 Run Project

```bash
# Start backend + Streamlit
bash start.sh
```

**start.sh**
```python
#!/bin/bash
# Start Uvicorn and Streamlit in background, record PIDs
uvicorn backend.main:app --reload --port 8001 &
UVICORN_PID=$!

sleep 2
streamlit run app.py &
STREAMLIT_PID=$!

echo "Uvicorn PID: $UVICORN_PID"
echo "Streamlit PID: $STREAMLIT_PID"

# Save PIDs for later termination
echo $UVICORN_PID > uvicorn.pid
echo $STREAMLIT_PID > streamlit.pid

echo "Servers are running..."

```

**stop.sh**
```python
#!/bin/bash
# Read PIDs and terminate processes

if [ -f uvicorn.pid ]; then
  kill $(cat uvicorn.pid) 2>/dev/null && echo "Uvicorn stopped."
  rm uvicorn.pid
else
  echo "No uvicorn.pid found."
fi

if [ -f streamlit.pid ]; then
  kill $(cat streamlit.pid) 2>/dev/null && echo "Streamlit stopped."
  rm streamlit.pid
else
  echo "No streamlit.pid found."
fi
```

---

### 🚀 Extended Architecture Plan

1. Shared Navigation State Across Sub-Apps

We’ll make a SessionState manager (or use Streamlit’s st.session_state) to:
-	Keep global selections (e.g., author, topic, timeframe)
-	Share navigation history between components
-	Support back-navigation or multi-view memory

2. Typeahead Search + Multi-Select with Chips

We’ll use:
-	st_tags (via streamlit-tags) or a custom chip component
-	Autocomplete backed by your API (e.g., /api/authors/search)
-	Multi-select with remove buttons for each tag/chip



---


##  Project Namespace and import Resolution
 

### Project Struture


```text

academic-agent/             # root project - academic-agent
├── app.py
├── components/             # global components
│   ├── __init__.py
│   └── cards.py
├── utils/                  # global utils
│   ├── __init__.py
│   └── global_state.py
└── academic-compass/       # sub project - academic_compass
    ├── app.py
    ├── components/         # sub components
    │   ├── __init__.py
    │   └── planner.py
    │   └── candidate_card.py
    ├── service/            # sub servicd
    │   ├── __init__.py
    │   └── llm_service.py
    └── utils/              # sub utils
        ├── __init__.py
        └── semantic_search.py

```

---

###  Import Resolution Mismatch


#### Use a Relative import:

**How to resolve relative imports in Python**

**academic-agent/app.py**

```python
from utils import global_state. # global utils
```

**academic-compass/app.py**

```python
from .components.planner import Planner  # sub components
```

**academic-compass/components/planner.py**

```python
from ..utitls.semantic_search import SemanticSearchTool     # sub utils
from . import candidate_card
```

**academic-compass/components/planner.py**

```python
from ..service.llm_service import llm_service     # sub service
```

#### Use the Absolute import:

```python
from academic-compass.services.llm_service import llm_service
```

**Explanation**:
-	.. goes up one level from components/ → to academic-compass/
-	then goes into services.llm_service


**Make sure**:

1. Rename the folder to a valid package name
2. Have __init__.py files everywhere, so Python treats them as packages.
3. Match import names to actual file names
4. Run Streamlit from the parent directory of the subproject (academic-agent/).
5. Don’t run directly inside components/ or services/.
6. Run as a module, not as a script


```bash
cd /academic-agent
python -m academic_compass.app
```

🧠 Summary of Import Rules

### Import Rules Cheat Sheet

| Direction                | Preferred Import | Example                                                         |
|--------------------------|------------------|-----------------------------------------------------------------|
| components → services    | absolute         | `from impact_analysis.services.llm_helpers import call_llm`      |
| services → components    | absolute         | `from impact_analysis.components.summary_card import render_summary_card` |
| internal dev/testing     | relative         | `from ..services.llm_helpers import call_llm`                   |

- Use **absolute imports** for production code between major folders (e.g., components, services).
- Use **relative imports** only for internal development or testing within the same package.
- Always ensure your package structure supports the chosen import style.


---


###  ModuleNotFoundError

```vbnet
ModuleNotFoundError: No module named 'routers'
```
means that Python couldn’t find a package or module named routers when trying to import it in your file:

```pqsql
from routers import parse, search, candidate, team, rerank, author, profile, topic
```

---

✅ Common Causes and Fixes

#### 1. The routers folder isn’t in the Python path

If your project structure looks like this:

```css
academic_service
├── backend/
    ├── main.py
    ├── routers/
    │   ├── __init__.py
    │   ├── parse.py
    │   ├── search.py
    │   └── ...
```

and you’re running the app from outside the backend directory (e.g. academic_service) , Python may not see routers.

**Fix**:

Run the app from within the backend directory or add it to your path.

```bash
cd backend
uvicorn main:app --reload
```
Or, if you want to run it from the parent directory:

```bash
uvicorn backend.main:app --reload
```
and change your import to:

```python
from backend.routers import parse, search, candidate, team, rerank, author, profile, topic, llm
```

---

#### 2. Missing __init__.py

If your routers folder doesn’t have an __init__.py file, Python won’t recognize it as a package.

**Fix**:

Create an empty file at:
```bash
backend/routers/__init__.py
```

---

#### 3. Virtual environment confusion

Sometimes uvicorn runs from a different virtual environment that doesn’t include your local project.

**Fix**:

Make sure you’re running Uvicorn from the same virtual environment where your code lives:
```bash
which uvicorn
which python

```

They should both point inside the same .venv or environment directory.

---

#### 4. PYTHONPATH not set

If you want to keep your import as-is but run from elsewhere, you can modify PYTHONPATH:

```bash
export PYTHONPATH=$(pwd)/backend
uvicorn main:app --reload

```

---


##  Structuring the Project and Import Resolution


Excellent — you’re structuring this project the right way 👍

When each subproject (like academic_compass, researcher_selector, etc.) has its own components folder, you can cleanly import them without breaking relative paths using one of the following approaches.

---

### ✅ 1. Recommended structure

Here’s an improved layout showing local and shared components:

```text
academic-agent/
│
├── app.py
├── backend/
│   └── main.py
│
├── utils/
│   ├── global_state.py
│   └── api_client.py
│
├── components/                # 🔹 shared components
│   ├── searchbox.py
│   └── ui_helpers.py
│
├── academic_compass/
│   ├── app.py
│   └── components/
│       ├── compass_chart.py
│       └── compass_summary.py
│
├── researcher_selector/
│   ├── app.py
│   └── components/
│       └── author_card.py
│
├── team_builder/
│   ├── app.py
│   └── components/
│       └── team_summary.py
│
└── impact_analyzer/
    ├── app.py
    └── components/
        └── impact_chart.py
```

---

### ✅ 2. Import from local subproject components

Inside academic_compass/app.py:

```python
import streamlit as st

# ✅ Import local component from this subproject
from .components import compass_chart, compass_summary

# ✅ Import shared utility or component
from utils import global_state
from components.ui_helpers import display_key_value_cards

def render():
    st.title("📘 Academic Compass")
    compass_chart.render_chart()
    compass_summary.render_summary()
```

---


### ✅ 3. In each subproject’s component file

Example: academic_compass/components/compass_summary.py

```python
import streamlit as st
from utils import global_state  # shared
from components.ui_helpers import display_key_value_cards  # shared component

def render_summary():
    summary = {
        "Focus Area": "Data Science in Education",
        "Collaborations": "MIT, Stanford",
        "Impact": "Top 10% citations globally"
    }
    display_key_value_cards(summary)
```

---

### ✅ 4. If import errors occur

Sometimes Streamlit’s module discovery doesn’t recognize nested packages.
Fix that by adding __init__.py files in all folders you want treated as packages:

```text
academic-agent/
├── __init__.py
├── utils/
│   └── __init__.py
├── components/
│   └── __init__.py
├── academic_compass/
│   ├── __init__.py
│   └── components/
│       └── __init__.py
...
```

Then, your imports always work cleanly across subprojects.

---

### ✅ 5. Alternative (if relative import issues persist)

You can dynamically add the project root to sys.path at runtime:

```python
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
```

Then you can do:
```python
from components.ui_helpers import display_key_value_cards
from utils import global_state
```