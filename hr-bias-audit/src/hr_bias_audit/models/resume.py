from pydantic import BaseModel
from typing import Optional
from datetime import date


class ResumeProfile(BaseModel):
    id: str
    name: str
    email: str
    raw_text: str
    inferred_gender: Optional[str] = None
    inferred_age_group: Optional[str] = None
    inferred_ethnicity: Optional[str] = None
    education: list[str] = []
    skills: list[str] = []
    years_experience: float = 0.0
    screening_score: float = 0.0
    passed_screen: bool = False
    source: str = ""
