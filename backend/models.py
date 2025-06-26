from pydantic import BaseModel
from typing import List

class Employee(BaseModel):
    id: int
    name: str
    skills: List[str]
    experience_years: int
    projects: List[str]
    availability: str

class ChatQuery(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    employees: List[Employee] = [] 