# LLM/RAG Knowledge Assistant

Portfolio-ready retrieval service that indexes a small document collection, retrieves the most relevant passages, and returns a grounded answer with citations. The default implementation is deterministic and does not require a paid LLM API.

## Stack

- Python, FastAPI, scikit-learn
- TF-IDF retrieval with cosine similarity
- Grounded response generation and confidence-based abstention
- Pytest coverage

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` and call `POST /ask` with:

```json
{"question": "How is PHI protected?", "top_k": 3}
```

## Design

Documents are chunked, vectorized, ranked, and filtered by a confidence threshold. If retrieval evidence is weak, the service abstains instead of inventing an answer. Replace `compose_answer` with Bedrock, GPT, or Llama for a production LLM implementation.

