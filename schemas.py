"""
schemas.py
----------
Pydantic models used to validate form input coming from the
HTML forms in index.html and result.html.
"""

from pydantic import BaseModel


class UserInput(BaseModel):
    username: str
    user_id: str
    age: int
    weight: str
    goal: str
    intensity: str


class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str
