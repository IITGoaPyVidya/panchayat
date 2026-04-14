from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserSignup(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = ""
    password: str = Field(min_length=6)
    flat_number: str = Field(min_length=1, max_length=20)
    role: Literal["resident", "admin"] = "resident"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    flat_number: str
    members_count: int
    vehicle_numbers: str

    class Config:
        from_attributes = True


class ResidentProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = ""
    email: EmailStr
    members_count: int = Field(ge=1)
    vehicle_numbers: str = ""


class ContactCreate(BaseModel):
    name: str
    category: str
    phone: str


class ContactUpdate(BaseModel):
    name: str
    category: str
    phone: str


class ContactOut(BaseModel):
    id: int
    name: str
    category: str
    phone: str
    added_by_flat: str
    owner_id: int

    class Config:
        from_attributes = True


class ComplaintCreate(BaseModel):
    category: Literal["Water", "Electricity", "Cleanliness", "Noise", "Security", "Parking", "Other"]
    subject: str
    description: str
    priority: Literal["Low", "Medium", "High", "Urgent"]


class ComplaintUpdate(BaseModel):
    status: Literal["Open", "In Progress", "Resolved", "Closed"]
    assigned_to: str | None = None
    resolution_notes: str | None = None


class ComplaintOut(BaseModel):
    id: int
    flat_number: str
    resident_name: str
    category: str
    subject: str
    description: str
    priority: str
    status: str
    photo_path: str | None
    assigned_to: str | None
    resolution_notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class NoticeCreate(BaseModel):
    title: str
    content: str
    is_pinned: bool = False
    expires_on: date | None = None


class NoticeOut(BaseModel):
    id: int
    title: str
    content: str
    image_path: str | None
    is_pinned: bool
    expires_on: date | None
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceCreate(BaseModel):
    flat_number: str
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    amount: int = Field(gt=0)
    due_date: date
    status: Literal["Paid", "Pending", "Overdue"] = "Pending"
    paid_on: date | None = None


class MaintenanceOut(BaseModel):
    id: int
    flat_number: str
    month: str
    amount: int
    due_date: date
    status: str
    paid_on: date | None

    class Config:
        from_attributes = True


class PollCreate(BaseModel):
    question: str
    poll_type: Literal["yesno", "multiple"] = "multiple"
    options: list[str]


class PollVoteCreate(BaseModel):
    selected_option: str


class PollOut(BaseModel):
    id: int
    question: str
    poll_type: str
    options: list[str]
    is_active: bool


class PollResult(BaseModel):
    poll_id: int
    question: str
    counts: dict[str, int]
