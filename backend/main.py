from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from backend.models import Employee, ChatQuery, ChatResponse
from backend.rag import rag_engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat(query: ChatQuery):
    employees, _ = rag_engine.search(query.query)
    response = rag_engine.generate_response(query.query, employees)
    return ChatResponse(response=response, employees=employees)

@app.get("/employees/search", response_model=List[Employee])
async def search_employees(
    skill: Optional[str] = Query(None),
    min_experience: Optional[int] = Query(None),
    project: Optional[str] = Query(None),
    availability: Optional[str] = Query(None)
):
    results = []
    for emp in rag_engine.employees:
        if skill and skill not in emp['skills']:
            continue
        if min_experience and emp['experience_years'] < min_experience:
            continue
        if project and project not in emp['projects']:
            continue
        if availability and emp['availability'] != availability:
            continue
        results.append(emp)
    return results 