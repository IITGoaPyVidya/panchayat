from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import Poll, PollVote, User
from ..schemas import PollCreate, PollOut, PollResult, PollVoteCreate

router = APIRouter(prefix="/polls", tags=["polls"])


@router.post("", response_model=PollOut)
def create_poll(payload: PollCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    options = payload.options or (["Yes", "No"] if payload.poll_type == "yesno" else [])
    if payload.poll_type == "yesno":
        options = ["Yes", "No"]
    if len(options) < 2:
        raise HTTPException(status_code=400, detail="At least two options required")
    poll = Poll(
        question=payload.question,
        poll_type=payload.poll_type,
        options_csv="|".join(options),
        created_by=current_user.id,
    )
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return PollOut(id=poll.id, question=poll.question, poll_type=poll.poll_type, options=options, is_active=poll.is_active)


@router.get("", response_model=list[PollOut])
def list_polls(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Poll).order_by(Poll.created_at.desc()).all()
    return [PollOut(id=r.id, question=r.question, poll_type=r.poll_type, options=r.options_csv.split("|"), is_active=r.is_active) for r in rows]


@router.post("/{poll_id}/vote")
def vote(poll_id: int, payload: PollVoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    poll = db.get(Poll, poll_id)
    if not poll or not poll.is_active:
        raise HTTPException(status_code=404, detail="Poll not found")
    options = poll.options_csv.split("|")
    if payload.selected_option not in options:
        raise HTTPException(status_code=400, detail="Invalid option")
    existing = db.query(PollVote).filter(PollVote.poll_id == poll_id, PollVote.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already voted")
    db.add(PollVote(poll_id=poll_id, user_id=current_user.id, selected_option=payload.selected_option))
    db.commit()
    return {"message": "Vote recorded"}


@router.get("/{poll_id}/results", response_model=PollResult)
def results(poll_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    poll = db.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    options = poll.options_csv.split("|")
    counts = {opt: 0 for opt in options}
    for v in db.query(PollVote).filter(PollVote.poll_id == poll_id).all():
        counts[v.selected_option] = counts.get(v.selected_option, 0) + 1
    return PollResult(poll_id=poll_id, question=poll.question, counts=counts)
