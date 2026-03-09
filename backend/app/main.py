from fastapi import FastAPI
from pydantic import BaseModel
from app.rag_logic import conditional_rag_answer

app = FastAPI(title="Conditional RAG API")

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=AnswerResponse)
def ask(payload: QuestionRequest):
    answer = conditional_rag_answer(payload.question)
    return {"answer": answer}
