# backend/models.py
from pydantic import BaseModel # pyright: ignore[reportMissingImports]
from typing import Optional, List
from enum import Enum


class FindingType(str, Enum):
    terminology = "terminology"
    tone = "tone"
    fact_conflict = "fact_conflict"
    unsupported_claim = "unsupported_claim"
    accessibility = "accessibility"


class FindingStatus(str, Enum):
    CONFLICT = "CONFLICT"
    UNVERIFIED = "UNVERIFIED"
    CLEAR = "CLEAR"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Finding(BaseModel):
    type: FindingType
    rule_id: Optional[str] = None
    status: FindingStatus
    explanation: str
    original_snippet: str
    suggested_fix: Optional[str] = None
    severity: Severity


class CheckResponse(BaseModel):
    findings: List[Finding]


class CheckRequest(BaseModel):
    content_id: str
    text: str


class BrandRuleCreate(BaseModel):
    type: str
    title: str
    content: str
    avoid_term: Optional[str] = None
    preferred_term: Optional[str] = None


class ContentCreate(BaseModel):
    title: str
    text: str


class ReviewRequest(BaseModel):
    content_id: str
    decision: str
    comment: Optional[str] = None
    user_name: Optional[str] = "Reviewer"