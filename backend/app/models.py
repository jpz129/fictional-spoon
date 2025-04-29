from typing import List
from pydantic import BaseModel

class SearchResult(BaseModel):
    task_text: str
    contract_text: str
    contract_id: str
    similarity: float

class ContractTasks(BaseModel):
    contract_id: str
    contract_text: str
    tasks: List[str]

class ContractResult(BaseModel):
    contract_id: str
    similarity: float
    explanation: str
    tasks: List[str]

class SearchTaskResponse(BaseModel):
    contracts: List[ContractResult]
    final_summary: str