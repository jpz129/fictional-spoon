from fastapi import FastAPI, Query
from typing import List
from .vectorstore import search_tasks
from .models import SearchTaskResponse

app = FastAPI()

@app.get("/search_task", response_model=SearchTaskResponse)
def search_task(query: str = Query(..., description="Task query text")):
    return search_tasks(query)