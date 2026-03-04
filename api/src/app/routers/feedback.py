"""Feedback endpoints for engineer RCA ratings."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, timezone

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackSubmission(BaseModel):
    rating: Literal["correct", "partially_correct", "incorrect"]
    comment: Optional[str] = None
    submitted_by: str = "anonymous"


class FeedbackResponse(BaseModel):
    status: str
    investigation_id: str
    rating: str
    message: str


@router.get("")
async def list_feedback():
    """
    List all feedback submissions.
    """
    from ..services.mock_data import get_feedback
    return get_feedback()


@router.post("/{investigation_id}", response_model=FeedbackResponse)
async def submit_feedback(investigation_id: str, feedback: FeedbackSubmission):
    """
    Submit RCA accuracy rating for a completed investigation.
    
    Ratings:
    - correct: archived as positive eval example
    - partially_correct: flagged for SRE SME review
    - incorrect: immediate alert to Platform Tech Lead; regression test added
    """
    from ..services.mock_data import get_investigation_by_id

    investigation = get_investigation_by_id(investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail=f"Investigation '{investigation_id}' not found")

    # In production: write to Part 1's eval dataset
    actions = {
        "correct": "Archived to eval dataset as positive example. Confidence calibration updated.",
        "partially_correct": "Flagged for SRE SME review. Added as hard negative for next eval run.",
        "incorrect": "Alert sent to Platform Tech Lead. Regression test will be added to Part 1 eval harness."
    }

    return FeedbackResponse(
        status="accepted",
        investigation_id=investigation_id,
        rating=feedback.rating,
        message=actions[feedback.rating]
    )
