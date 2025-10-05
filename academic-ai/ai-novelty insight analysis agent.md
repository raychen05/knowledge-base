## Paper ovelty Insight Analysis Agent


Here is a full runnable Python starter project for your LangChain AI agent that automates novelty and innovation analysis of research papers using Web of Science and NLP tools.

---

### 🧠 Project: novelty_insight_agent


🗂 Folder Structure:

```plaintext
novelty_insight_agent/
├── main.py
├── tools/
│   ├── wos_api.py
│   ├── incites_api.py
│   └── novelty_analysis.py
├── utils/
│   ├── embedding.py
│   └── similarity.py
└── requirements.txt
```

---

### 📄 requirements.txt



```plaintext
langchain
openai
sentence-transformers
faiss-cpu
scikit-learn
numpy
requests
python-dotenv

```

---

### ⚙️ tools/wos_api.py


```python
from langchain.tools import tool

@tool
def search_related_papers(topic: str) -> list:
    """Use Web of Science API to get papers related to the topic."""
    # Placeholder for actual API call
    return [
        {"title": "Graphene biosensor for virus detection", "abstract": "..."},
        {"title": "Rapid COVID testing methods", "abstract": "..."},
    ]

```

---

### ⚙️ tools/novelty_analysis.py


```python
from langchain.tools import tool
from utils.similarity import compute_semantic_similarity
from utils.embedding import get_keywords_tfidf

@tool
def analyze_novelty(abstract: str, related_abstracts: list) -> str:
    """Compare abstract against related ones to evaluate novelty."""
    sim_score = compute_semantic_similarity(abstract, related_abstracts)
    new_keywords = get_keywords_tfidf(abstract, related_abstracts)

    return f"Novelty Score: {1-sim_score:.2f}\nUnique keywords: {', '.join(new_keywords[:5])}"
```

---

### ⚙️ utils/embedding.py


```python
from sklearn.feature_extraction.text import TfidfVectorizer

def get_keywords_tfidf(target_text, other_texts):
    docs = other_texts + [target_text]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    X = vectorizer.fit_transform(docs)
    scores = X[-1].toarray().flatten()
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in ranked[:10]]M
```

---

### ⚙️ utils/similarity.py


```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_semantic_similarity(text: str, others: list) -> float:
    embeddings = model.encode([text] + others)
    query_vec = embeddings[0].reshape(1, -1)
    corpus_vecs = embeddings[1:]
    sims = cosine_similarity(query_vec, corpus_vecs)
    return float(np.mean(sims))
```


---

### 🚀 main.py


```python
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from tools.wos_api import search_related_papers
from tools.novelty_analysis import analyze_novelty

llm = ChatOpenAI(temperature=0.3, model="gpt-4")

tools = [
    search_related_papers,
    analyze_novelty,
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    memory=memory,
    verbose=True
)

if __name__ == "__main__":
    result = agent.run("""
    I want to evaluate the novelty of this paper:
    Title: Graphene-Based Biosensor for Rapid COVID-19 Detection
    Abstract: We present a highly sensitive, low-cost graphene biosensor for SARS-CoV-2 detection...
    """)
    print(result)

```

---


### ✅ Output Example


``` bash
> Entering new AgentExecutor chain...
Thought: I should find related papers first
Action: search_related_papers
Action Input: Graphene-Based Biosensor for Rapid COVID-19 Detection
Observation: 2 papers found...
Thought: Now I will analyze novelty based on similarity and keywords
Action: analyze_novelty
Action Input: (abstract + related abstracts)
Observation:
Novelty Score: 0.67
Unique keywords: graphene, sars-cov-2, biosensor, real-time, nanomaterial

Final Answer:
The paper shows high novelty with specific unique terms and low similarity to prior work.
```

---

### 📌 Next Steps

-	Integrate real Web of Science API via your keys
-	Add citation benchmarking via InCites
-	Generate report with LangChain’s output parser or template

