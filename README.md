# Fictional Spoon

A lightweight FastAPI and Streamlit application that extracts and vectorizes tasks from CDC-style contracts, letting users search them semantically. The tool returns the most relevant contract groupings and an LLM-generated summary.

Here you can prototype clustering and potential consolidation of semantically similar contracts, using their overlapping operational tasks and shared intent.

---

## What This Project Does

- Processes contract documents in `.docx` format  
- Extracts tasks from each contract using an LLM  
- Vectorizes those tasks with OpenAI embeddings  
- Indexes them with FAISS for fast, semantic search  
- Returns the top results for any query  
- Explains why each match matters (with LLM explanations)  
- Summarizes result groups and offers consolidation reasoning  

Use this tool for government contract evaluation, audit review, or procurement design, especially when you need to spot redundant scopes in a pile of contracts.

---

## Project Structure

```text
fictional-spoon/
├── backend/
│   └── app/
│       ├── faiss/                      # FAISS vectorstore artifacts (index.faiss, index.pkl)
│       ├── main.py                     # FastAPI app with /search_task endpoint
│       ├── models.py                   # Pydantic models for task/results/response schemas
│       └── vectorstore.py              # Search, explanation, and summarization logic
├── frontend/
│   └── streamlit_app.py                # Streamlit UI for queries and results
├── scripts/
│   ├── contracts_raw/                  # Raw input .docx contracts
│   └── preprocess_contracts.py         # Task extraction and FAISS indexing
├── requirements.txt                    # Python dependencies
└── README.md                           # This document
```

---

## How to Set Up and Run

### Clone the repository

```bash
git clone https://github.com/your-username/fictional-spoon.git
cd fictional-spoon
```

### Make a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Add your OpenAI key

Create `backend/.env` and add your key:

```env
OPENAI_API_KEY=your-api-key-here
```

### Preprocess contracts (if needed)

```bash
python scripts/preprocess_contracts.py
```

### Run the FastAPI server

```bash
cd backend
uvicorn app.main:app --reload
```

### Run the Streamlit frontend

```bash
cd frontend
streamlit run streamlit_app.py
```

---

## Why This Structure

This layout reflects a fast-running workflow focused on the output rather than heavy modularity.

- We kept things simple. Easy to find, easy to edit.
- The split between backend and frontend is clean even as both run locally.
- Using docx, FAISS, and OpenAI simulates a real CDC contract evaluation pipeline.
- Rich print logging in the terminal makes the app’s reasoning easy to follow.
- The LLM’s chain-of-thought explanations and summaries mirror what a contracting officer might need.

This is a prototype meant for clarity. The bones are strong enough to expand later.

---

## Example Use Case

You enter a query like

> Conduct serological testing for respiratory viruses

The app finds and shows:

- The five most relevant contracts
- Their associated tasks
- An explanation of the match
- A summary describing overlap and suggesting consolidation

---

## Dependencies

- fastapi and uvicorn for the backend API
- streamlit for the frontend
- langchain for task extraction and explanation
- openai for embeddings and language models
- faiss-cpu for vector search
- python-docx for parsing contracts
- python-dotenv for environment variables

---

## What’s Next

You might extend the project to

- Support more file formats like PDF and XLSX
- Add user feedback and approval workflows
- Automate consolidation drafts with templates
- Package and deploy with Docker

---

## Made by Juan Pablo

Built with attention, frustration, and pride. A deep dive into LLM-powered evaluation and decision support, shaped by the urge to make sense of messy contracts and find the pattern in the chaos.