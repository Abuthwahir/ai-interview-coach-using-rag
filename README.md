# AI Interview Coach: Adaptive Multi-Turn Interview Simulation Platform

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Orchestrated-1C3C3C)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![AI](https://img.shields.io/badge/AI-Groq%20%2B%20LLM-0F9D58)

An end-to-end AI interview system that simulates realistic technical interviews using LangChain, Groq, adaptive difficulty logic, memory-based conversation, and optional job-description-aware question generation.

Built as a modular product rather than a tutorial script, this project combines multi-turn interviewing, structured evaluation, topic progression, and final reporting into both a command-line workflow and a Streamlit web application.

## Overview

AI Interview Coach is designed to behave like a practical interview simulator for technical roles. It can ask context-aware questions, remember prior responses, score answers with structured feedback, adapt difficulty across the session, and optionally ground questions in a job description using a lightweight RAG pipeline.

This project was implemented step by step across six stages:

- Task 1: Chains and prompt engineering
- Task 2: Conversation memory
- Task 3: Structured answer evaluation
- Task 4: RAG with a lightweight retriever
- Task 5: Function-based adaptive interview flow
- Task 6: Full application with CLI and Streamlit UI

## Demo

### CLI
```bash
python main.py --job data/job_descriptions/senior_python.txt --questions 5 --level senior
```

### Streamlit Web App
```bash
streamlit run app.py
```

## Features

- Multi-turn AI interview flow with conversational memory
- Prompt-based question generation using LangChain chains
- Structured answer evaluation with score, strengths, improvements, and ideal answer
- Adaptive interview difficulty across `easy`, `medium`, and `hard`
- Dynamic topic progression based on answer performance
- Optional RAG using job descriptions for role-specific questions
- Lightweight custom retriever with no ChromaDB dependency
- Function-based adaptive control flow with no `AgentExecutor`
- Final interview report with transcript, scores, and summary insights
- Dual interface support through CLI and Streamlit

## Architecture

```text
                        +----------------------+
                        |      config.py       |
                        |  Settings / .env     |
                        +----------+-----------+
                                   |
                                   v
+----------------+      +---------------------------+      +------------------+
|    main.py     |----->|     interview_coach.py    |<-----|      app.py      |
|   CLI Runner   |      |   Central Orchestrator    |      |  Streamlit UI    |
+----------------+      +------------+--------------+      +------------------+
                                     |
                 +-------------------+-------------------+
                 |                   |                   |
                 v                   v                   v
        +----------------+   +----------------+   +------------------+
        | chains/        |   | agents/        |   | rag/             |
        | interviewer.py |   | tools.py       |   | loader.py        |
        | evaluator.py   |   | coach.py       |   | retriever.py     |
        +----------------+   +----------------+   | setup.py         |
                                                   +------------------+

Flow:
User Answer -> Evaluation -> Adaptive Logic -> Next Question -> Final Report
```

## Folder Structure

```text
interview-coach/
├── app.py
├── config.py
├── interview_coach.py
├── main.py
├── requirements.txt
├── .env
├── changes_made.txt
├── README.md
├── agents/
│   ├── coach.py
│   └── tools.py
├── chains/
│   ├── evaluator.py
│   ├── interviewer.py
│   └── question_generator.py
├── data/
│   └── job_descriptions/
│       └── senior_python.txt
├── memory/
│   └── conversation.py
└── rag/
    ├── loader.py
    ├── retriever.py
    └── setup.py
```

## How It Works

1. The session starts through the CLI or Streamlit app.
2. `InterviewCoach` initializes the interviewer chain, evaluator chain, adaptive logic, and optional RAG pipeline.
3. The first question is generated based on role, level, focus area, and job description context if provided.
4. The user submits an answer.
5. The evaluator chain returns structured feedback:
   - score
   - strengths
   - improvements
   - correct answer
6. The adaptive logic updates difficulty and topic progression based on the score.
7. The next question is generated using:
   - RAG question generation if a job description exists
   - fallback interview generation if no job description is provided
8. The process repeats until the interview reaches the configured question limit.
9. A final report is generated with average score, round-by-round results, strengths, improvement areas, and transcript.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/interview-coach.git
cd interview-coach
```

### 2. Create a virtual environment
#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file
```env
GROQ_API_KEY=your_groq_api_key
MODEL_NAME=llama-3.1-8b-instant
TEMPERATURE=0.7
EVALUATOR_TEMPERATURE=0.2
MAX_QUESTIONS=5
DEFAULT_POSITION=Python Developer
DEFAULT_LEVEL=mid
DEFAULT_INTERVIEW_TYPE=technical
DEFAULT_FOCUS_AREA=Python fundamentals and problem solving
```

## Usage

### Run the CLI Interview
```bash
python main.py --job data/job_descriptions/senior_python.txt --questions 5 --level senior
```

### Run Without RAG
```bash
python main.py --questions 5 --level mid
```

### Launch the Streamlit App
```bash
streamlit run app.py
```

## Example Output

```text
==================================================
AI Interview Coach
==================================================
Position: Python Developer
Level: senior
Interview Type: technical
RAG Enabled: Yes

Question 1: How would you design asynchronous task handling in a FastAPI-based backend?

Your answer: I would use async endpoints for I/O-heavy tasks and move long-running jobs to a queue like Celery or RQ...

Feedback
----------------------------------------
Score: 8/10
Strengths: Clear architecture thinking and good separation of async I/O from background processing.
Improvements: Mention failure handling, retries, and observability.
Correct Answer: A strong answer should explain async request handling, background workers, queue selection, retry policies, and monitoring.

Question 2: Explain how message queues help improve scalability in distributed systems.

...

Final Report
==================================================
Average Score: 7.8/10
Overall Assessment: Good performance with a few gaps
Top Strengths:
- Good system-level reasoning
- Clear explanations with practical examples

Top Improvements:
- Go deeper on trade-offs
- Add more production-grade considerations
```

## Tech Stack

- Python 3.8+
- LangChain
- Groq API
- Streamlit
- Pydantic Settings
- Prompt engineering
- Conversation memory
- Lightweight RAG pipeline
- Custom adaptive interview controller

## Design Decisions

### Why No `AgentExecutor`?

This project intentionally avoids LangChain `AgentExecutor` because the interview flow is deterministic and state-driven. The system already knows the sequence of actions it needs to perform:

- ask a question
- collect an answer
- evaluate the answer
- adjust difficulty
- generate the next question
- produce a final report

Using an agent loop here would add complexity, unpredictability, and unnecessary runtime overhead for a workflow that is better modeled as explicit orchestration.

### Why No ChromaDB?

The RAG layer uses a lightweight custom retriever because the project only needs simple job-description-aware context injection rather than full vector database infrastructure.

This decision keeps the system:

- easier to run locally
- simpler to explain in interviews
- compatible with Python 3.8
- free from avoidable ChromaDB setup issues

### Why Function-Based Adaptive Logic?

The adaptive interview behavior is implemented through a custom function-based controller instead of a ReAct-style agent because the decision logic is simple, transparent, and easy to validate.

Benefits of this approach:

- predictable control flow
- easier debugging
- lower latency
- better maintainability
- clear separation between LLM generation and application logic

## Limitations

- Evaluation quality depends on the underlying LLM response consistency
- The custom retriever is intentionally simple and not semantic-search based
- The adaptive scoring logic is lightweight and can be improved with richer heuristics
- The system currently focuses more on technical interviews than broader hiring workflows
- No persistent database or user authentication is included
- Streaming responses and analytics dashboards are not yet implemented

## Future Improvements

- Add semantic retrieval with embeddings while preserving lightweight local setup
- Support multiple interview modes such as behavioral, HR, and system design
- Add persistent session storage and historical candidate tracking
- Introduce richer scoring rubrics and rubric-based evaluation
- Export interview reports as PDF or JSON
- Add authentication and recruiter dashboards
- Enable interview analytics across multiple sessions
- Support audio-based mock interviews with speech-to-text

## Resume-Ready Description

> Built a modular AI Interview Coach using Python, LangChain, Groq, and Streamlit that simulates multi-turn technical interviews with conversational memory, structured answer evaluation, adaptive difficulty control, job-description-aware RAG, and final report generation through both CLI and web interfaces.

## License

This repository currently does not include a license file. If you plan to open-source the project publicly, adding an MIT License is a simple and common choice.
