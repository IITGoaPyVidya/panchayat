import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import auth, complaints, contacts, maintenance, notices, polls, residents, rulebook, chatbot

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Society Management System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = os.getenv("UPLOAD_DIR", "./data/uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(complaints.router)
app.include_router(rulebook.router)
app.include_router(chatbot.router)
app.include_router(notices.router)
app.include_router(maintenance.router)
app.include_router(residents.router)
app.include_router(polls.router)


@app.get("/")
def health_check():
    return {"status": "ok", "app": "Society Management System"}
