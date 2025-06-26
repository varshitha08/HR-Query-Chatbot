import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import os
import requests

DATA_PATH = Path(__file__).parent.parent / 'data' / 'employees.json'
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

class RAGEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.employees = self.load_employees()
        self.employee_texts = [self.profile_to_text(emp) for emp in self.employees]
        self.embeddings = self.model.encode(self.employee_texts)

    def load_employees(self):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['employees']

    def profile_to_text(self, emp):
        return f"{emp['name']} | Skills: {', '.join(emp['skills'])} | Experience: {emp['experience_years']} years | Projects: {', '.join(emp['projects'])} | Availability: {emp['availability']}"

    def search(self, query, top_k=3):
        query_emb = self.model.encode([query])
        sims = cosine_similarity(query_emb, self.embeddings)[0]
        top_indices = np.argsort(sims)[::-1][:top_k]
        return [self.employees[i] for i in top_indices], [sims[i] for i in top_indices]

    def call_ollama(self, prompt, model=OLLAMA_MODEL):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert HR assistant. Answer queries about employee allocation using the provided employee data."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"].strip()

    def generate_response(self, query, employees):
        if not employees:
            return "Sorry, I couldn't find any matching employees."
        # Build context for LLM
        context = "\n".join([self.profile_to_text(emp) for emp in employees])
        prompt = f"""
You are an expert HR assistant. A user has asked: \"{query}\"

Here are the most relevant employees:
{context}

For this query, do the following:
1. Highlight the top 1-2 best candidates, giving detailed reasons (skills, experience, project fit, availability).
2. Briefly mention any other relevant candidates and why they may not be the best fit.
3. Conclude with a summary and a follow-up question (e.g., offer to provide more details or check availability).

Respond in a professional, natural, and helpful tone.
"""
        try:
            return self.call_ollama(prompt)
        except Exception as e:
            # Fallback to template if Ollama fails
            lines = [f"Based on your requirements, I found {len(employees)} strong candidate{'s' if len(employees) > 1 else ''}:"]
            for emp in employees:
                highlight = f"\n\n{emp['name']} has {emp['experience_years']} years of experience. "
                if 'Machine Learning' in emp['skills'] or 'Data Science' in emp['skills']:
                    highlight += f"They have worked on projects like {', '.join(emp['projects'])}. "
                else:
                    highlight += f"Key skills: {', '.join(emp['skills'])}. "
                highlight += f"Notable projects: {', '.join(emp['projects'])}. "
                highlight += f"Current availability: {emp['availability']}."
                lines.append(highlight)
            lines.append("\nWould you like more details about their specific projects or to check their availability for meetings?")
            return '\n'.join(lines)

rag_engine = RAGEngine() 