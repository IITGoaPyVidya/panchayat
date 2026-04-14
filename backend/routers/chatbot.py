from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import User
from ..ai.chatbot import SocietyChatbot

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = []


@router.post("/ask")
def ask_bot(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bot = SocietyChatbot(db)
    answer = bot.ask(payload.message, payload.history)
    return {"bot_name": bot.name, "answer": answer}
