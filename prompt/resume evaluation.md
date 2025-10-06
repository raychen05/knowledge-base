## AI Resume Evaluation


You’re asking a very valuable and difficult question — how to detect authenticity and depth of experience in resumes that are full of similar buzzwords and overlapping project descriptions.

While it’s not 100% reliably possible to detect resume faking or shallow involvement from text alone, you can use a combination of prompt engineering + reasoning chains to infer the likelihood of authenticity. Here’s a framework and prompt design approach to do this.


---

### 🧠 Core Strategy


1.	Contextual Interrogation: Instead of asking “is this fake?”, ask the model to evaluate depth, coherence, and likely authorship based on clues in the resume.
2.	Behavioral Reasoning: Focus on whether the person seems to understand trade-offs, decisions, constraints, or real challenges.
3.	Comparison to Real Practitioners: Evaluate whether the language and detail match how an actual practitioner would describe the work.
4.	Project Role Clarity: Judge if the person likely led, contributed, or just observed.

---

### 🧰 Prompt Template to Evaluate Resume Authenticity

Here’s a system prompt you can use with GPT-4 or GPT-4o, or as part of a LangChain or evaluation agent.


🔍 Prompt: Experience Depth and Authenticity Assessment


```plaintext

System Message:

You are an expert in evaluating software engineering resumes to assess whether the candidate had real, hands-on experience in the projects listed. You analyze project descriptions for signs of authenticity, depth of knowledge, and likely involvement. You identify resumes that include surface-level keywords but lack signs of real contribution.

User Message:

Here’s a resume section:

---

Worked on a distributed microservices system using Kubernetes and Docker. Improved performance by 30%. Collaborated with DevOps team and used Grafana and Prometheus for monitoring.

Based on this text, please evaluate:
	1.	How likely is it that the candidate actually led or contributed significantly to this project?
	2.	What signs suggest real or fake experience?
	3.	What key details are missing that would indicate shallow or copied experience?
	4.	How would an experienced engineer describe the same work differently?

Give a score from 1 (likely fake or exaggerated) to 5 (very likely real and deep experience), with explanation.

---
```


### ✅ What to Look For in LLM Evaluation


The model will be looking for:

-	Lack of specific contributions (“what exactly did you do?”)
-	Overuse of buzzwords with no glue logic (“just listing tools”)
-	No mention of business problem, trade-offs, failure modes
-	Absence of metrics that are explained (e.g. “Improved 30%” without how)
-	Generic language that looks AI-written or template-based
-	Inconsistent tool combinations (e.g. using tools unlikely to be paired)


---

### 🧪 Real Example Response Summary


Given a typical line like:

“Built a CI/CD pipeline using Jenkins, GitLab, Docker, Kubernetes. Improved deployment time by 50%.”

The model might respond:
-	Score: 2/5
-	Reasoning: While tools are listed, the sentence lacks clear contribution, implementation details, or understanding of why the stack was chosen. No context about the project size, complexity, or challenges. Could be copied or lightly involved.


---

### 🧭 Bonus: Cross-checking Strategy


To go beyond a prompt and build an agent:

1.	Extract claims → list projects, responsibilities, metrics
2.	Ask follow-up generation → “Given this claim, what questions would validate their role?”
3.	Generate clarification questions → Use the model to ask “What kind of challenges did you face in this pipeline?”
4.	Score likelihood based on realism of answers (you could use this as an interview prep tool)


---

### 🧠 Optional Advanced Use: Compare Multiple Candidates

Prompt:

```plaintext
Given these 3 resumes with very similar project descriptions using the same technologies, evaluate which candidate is most likely to have real, deep experience based on language specificity, use of technical vocabulary, and demonstration of ownership. Rank them from most to least likely to be authentic.

---

❗Important Caveats
-	LLMs can help infer but not definitively detect lying
-	This works best as a pre-screening tool before interviews
-	Combine with structured follow-up questions for live interviews

---

```

Would you like a working example implemented in LangChain or a Python script to do this at scale across many resumes?


Absolutely — time duration is a crucial signal for evaluating the depth of involvement and authenticity of experience. It’s one of the most underused but highly informative heuristics in resume analysis.

Here’s how you can systematically use duration + tech matching + role context to assess whether the candidate was truly involved or just superficially associated.


---

### 🔍 1. Why Duration Matters


| Duration      | Implication                                                                                  |
|---------------|---------------------------------------------------------------------------------------------|
| < 3 months    | Likely an internship, proof of concept (POC), or minor support role; limited ownership      |
| 3–6 months    | Typical for short-term projects; suggests contributor role, less likely to be the architect |
| 6–12 months   | Indicates deeper involvement; possible full project lifecycle participation                 |
| > 12 months   | Strong signal of ownership, sustained contribution, and troubleshooting experience          |


✅ Use duration to validate:

-	If project claims match time (you can’t “rebuild a full microservices platform” in 2 months)
-	If tech learning curve aligns (e.g., using Kubernetes + Prometheus deeply in just 1 month is unlikely unless previously known)

---

### 🧠 2. Prompt Logic Incorporating Duration

Add to your evaluation prompts:

```plaintext
Given that this project lasted only 2 months, and lists complex technologies like Kafka, Kubernetes, and Terraform, evaluate:
-	Is it plausible the candidate used these deeply?
-	What part of the project lifecycle did they likely participate in (design, build, test, operate)?
-	Could they be inflating their contribution or listing team-wide technologies?
```


---

### 🧰 3. Prompt Template with Duration + Tech Use

System Prompt:

```plaintext
You are an expert resume evaluator. Your job is to assess whether the technologies listed were truly used by the candidate in the given time frame, and whether their claimed contribution is realistic based on project duration and description.

User Prompt:

Candidate lists this project:

“Built a scalable data pipeline using Kafka, Spark, and Airflow. Deployed on AWS using Terraform and Kubernetes.”

Duration: 2 months

Evaluate:
	1.	How likely is it that the candidate deeply used each technology?
	2.	Which tools are likely just listed but not actively used?
	3.	What level of contribution is realistic in this time frame?
	4.	Give a 1–5 confidence score on real vs exaggerated experience.

```


---

### 📏 4. Red Flags Based on Duration + Tools


 🚩 Red Flags Table: Duration & Tool Complexity

| Signal                                             | Possible Issue                                                                                  |
|----------------------------------------------------|------------------------------------------------------------------------------------------------|
| Short project + 5+ tools                           | May indicate buzzword stuffing                                                                 |
| No clear role (just “worked on”)                   | Unclear ownership or observer only                                                             |
| Complex infra in short time                        | Implausible solo execution (e.g., “built CI/CD + monitoring + deployment” in 1 month)          |
| Used tools with steep learning curve in short time | Shallow usage or only team-level exposure (e.g., Kubernetes, Terraform, Spark in <3 months)    |


🔧 Bonus: Add a Consistency Checker

If you’re doing this programmatically:

1.	Extract project duration
2.	Parse technology stack
3.	Compare against complexity heuristic (e.g., Terraform + Kubernetes + Kafka + Spark = high)
4.	If duration < 3 months AND complexity > threshold → flag for further review

---

### ✅ Actionable Summary

To better assess authenticity:

-	Always factor in project duration vs tech complexity
-	Ask the model to reason about realistic usage depth
-	Use structured prompts to evaluate role-specific contribution
-	Combine with follow-up question generation to use in interviews


### ✅ Part 1: Python Function to Evaluate Resume Experience

This function will:

-	Take in a resume’s project description, duration, and listed tech
-	Use GPT (via API) to assess authenticity and depth
-	Output a structured evaluation with confidence score and reasoning

### ✅ Python Function (Basic Version)

```python
import openai

def evaluate_resume_experience(project_description: str, duration_months: int, technologies: list[str]) -> dict:
    prompt = f"""
You are an expert in evaluating engineering resumes. Based on the project description, duration, and listed technologies, assess:

1. Whether the candidate is likely to have deeply used the listed technologies.
2. If the contribution level seems high, medium, or low.
3. Any red flags that suggest inflated or fake experience.
4. A confidence score from 1 (fake/exaggerated) to 5 (authentic and deep experience).
5. Explanation with reasoning.

Project Description: "{project_description}"
Duration: {duration_months} months
Technologies: {', '.join(technologies)}
"""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # Or "gpt-4", "gpt-3.5-turbo" if needed
        messages=[
            {"role": "system", "content": "You are a hiring expert analyzing the depth and authenticity of experience in a software engineering resume."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    
    return response['choices'][0]['message']['content']
```

You can scale this to evaluate multiple resume sections, or connect it to a resume parser (e.g. PyMuPDF, spaCy).


### ✅ Part 2: LangChain Agent to Automate Resume Vetting

This agent will:

-	Accept structured resume data (project description, time, stack)
-	Use LLM + rules + toolchain to analyze experience authenticity
-	Support follow-up question generation


Basic Setup

1.	Tools Required:

```bash
pip install langchain openai
```

2.	LangChain Agent Setup

```python
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain.agents.agent_types import AgentType

llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)

def analyze_experience_tool(project: str, duration: str, tech: str) -> str:
    prompt = f"""
You're evaluating a software engineer's resume entry.

Project: {project}
Duration: {duration}
Technologies: {tech}

Assess:
- Depth of involvement
- Technology usage authenticity
- Role (lead, contributor, observer)
- Confidence score (1–5)
- Flags suggesting exaggeration or inaccuracy

Output a structured analysis.
"""
    return llm.predict(prompt)

tools = [
    Tool(
        name="ResumeExperienceAnalyzer",
        func=lambda q: analyze_experience_tool(**eval(q)),
        description="Evaluates depth and authenticity of resume experience based on project, duration, and tech stack."
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
```


Example Usage

```python
query = "{'project': 'Built ML pipeline with Airflow, S3, and SageMaker', 'duration': '2 months', 'tech': 'Airflow, AWS S3, SageMaker'}"
agent.run(f"Use ResumeExperienceAnalyzer to evaluate: {query}")
```

### 📈 Next Steps

-	Add embedding-based similarity scoring to compare resumes with job descriptions
-	Integrate a PDF/Word resume parser to feed data into this pipeline
-	Add another tool that generates interview questions based on suspicious claims
