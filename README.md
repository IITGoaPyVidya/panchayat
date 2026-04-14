# Society Management System

Production-ready MVP for a residential society with **FastAPI backend** and **Streamlit frontend**.

## Features

- JWT Authentication (Admin / Resident)
- Guest emergency contacts view
- Useful contacts directory (owner/admin edit controls)
- Complaint management with status workflow and photo upload
- Rulebook upload/search and PDF hosting
- SocietyBot 🏠 chatbot (LangChain + OpenAI fallback logic)
- Notice board with pin/expiry behavior
- Maintenance tracker with overdue tagging and CSV export
- Resident directory with self-profile updates and admin export
- Polls and voting with one-vote-per-user and charted results
- Admin dashboard analytics cards and charts

## Project Structure

```
backend/
  main.py
  database.py
  models.py
  schemas.py
  auth_utils.py
  routers/
  ai/
frontend/
  app.py
  pages/
  components/
  styles/mobile.css
data/
  uploads/
  vector_store/
```

## Environment Variables

Create `.env`:

```env
OPENAI_API_KEY=your_key_here
JWT_SECRET=your_jwt_secret
DATABASE_URL=sqlite:///./data/society.db
UPLOAD_DIR=./data/uploads
API_BASE_URL=http://localhost:8000
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

## Run Frontend

```bash
streamlit run frontend/app.py --server.port 8501
```

## Notes

- SQLite is used for MVP; swap `DATABASE_URL` to PostgreSQL without model rewrites.
- Uploaded files are stored locally under `data/uploads`.
- Chatbot uses OpenAI if API key is present; otherwise it falls back to retrieval-only response mode.
