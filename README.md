# AI Code Review & Security Analysis Agent - Milestone 1

## Setup
```
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # then paste GEMINI_API_KEY inside .env (optional)
python -m scripts.build_kb     # build the vector index
streamlit run app.py
```
No API key? It still works using the built-in local embedder. Get a free Gemini key at https://aistudio.google.com/apikey

## Structure
- `modules/code_submission.py` - paste/upload + Python (ast) and Java (javalang) syntax validation
- `knowledge_base/` - OWASP, injection/XSS/CSRF, secrets/auth, Python, Java, code smell docs
- `rag/` - chunking, embeddings (Gemini/local), ChromaDB store, indexing pipeline
- `app.py` - Streamlit portal
- `docs/architecture.md` - design document
- `sample_code/` - vulnerable samples for demos

## Demo flow
1. Show architecture doc -> 2. Submit sample_code files (and a broken one to show validation errors) -> 3. Build index -> 4. Ask "How to prevent SQL injection in Java?"
