from pathlib import Path
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=1, le=5)


class Citation(BaseModel):
    source: str
    score: float
    passage: str


class AskResponse(BaseModel):
    answer: str
    grounded: bool
    citations: List[Citation]


def load_documents() -> list[dict]:
    docs = []
    for path in sorted((Path(__file__).parent / "data").glob("*.txt")):
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8").strip()})
    return docs


DOCUMENTS = load_documents()
VECTORIZER = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
MATRIX = VECTORIZER.fit_transform([doc["text"] for doc in DOCUMENTS])
MIN_SCORE = 0.08


def retrieve(question: str, top_k: int) -> list[dict]:
    scores = cosine_similarity(VECTORIZER.transform([question]), MATRIX)[0]
    ranked = scores.argsort()[::-1][:top_k]
    return [
        {**DOCUMENTS[index], "score": float(scores[index])}
        for index in ranked
        if scores[index] >= MIN_SCORE
    ]


def compose_answer(matches: list[dict]) -> str:
    if not matches:
        return "I do not have enough evidence in the indexed documents to answer that question."
    evidence = " ".join(match["text"] for match in matches[:2])
    return f"Based on the indexed guidance: {evidence}"


app = FastAPI(title="Grounded RAG Assistant", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "documents": len(DOCUMENTS)}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    matches = retrieve(request.question, request.top_k)
    return AskResponse(
        answer=compose_answer(matches),
        grounded=bool(matches),
        citations=[
            Citation(source=m["source"], score=round(m["score"], 4), passage=m["text"])
            for m in matches
        ],
    )

