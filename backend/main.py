import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine, SessionLocal
from .models import User
from .auth_utils import hash_password
from .routers import auth, complaints, contacts, maintenance, notices, polls, residents, rulebook, chatbot

# Create database tables
Base.metadata.create_all(bind=engine)


def create_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if default admin exists
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            # Create default admin user
            default_admin = User(
                name="Admin",
                email="admin@admin.com",
                phone="0000000000",
                hashed_password=hash_password("admin"),
                flat_number="ADMIN",
                role="admin",
                members_count=1,
                vehicle_numbers=""
            )
            db.add(default_admin)
            db.commit()
            print("✅ Default admin created - Username: admin | Password: admin (or email: admin@admin.com)")
        else:
            print("ℹ️  Default admin already exists")
    except Exception as e:
        print(f"❌ Error creating default admin: {e}")
        db.rollback()
    finally:
        db.close()


# Create default admin on startup
create_default_admin()

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
