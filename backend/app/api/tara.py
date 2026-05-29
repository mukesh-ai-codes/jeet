"""JEET Backend — Tara AI Tutor routes.
  POST /api/tara/chat — student chats with Tara (RAG + modes + frustration->handoff)
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.deps import require_role
from app.services.tara_service import ask_tara

router = APIRouter(prefix="/api/tara", tags=["Tara"])

class TaraMemoryTurn(BaseModel):
    role: str
    text: str

class TaraChatRequest(BaseModel):
    message: str
    mode: str = "saathi"
    memory: Optional[List[TaraMemoryTurn]] = None

class TaraChatResponse(BaseModel):
    reply: str
    mode: str
    sources: List[Optional[str]] = []
    frustration_detected: bool = False
    handoff_created: bool = False

@router.post("/chat", response_model=TaraChatResponse)
def tara_chat(
    body: TaraChatRequest,
    payload: dict = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    student_id = payload["sub"]
    mem = [{"role": m.role, "text": m.text} for m in (body.memory or [])]
    result = ask_tara(body.message, mode=body.mode, memory=mem)

    # MENTOR HANDOFF: if Tara detects real frustration, write a wellness-check
    # intervention into the SAME table the mentor queue + parent dashboard read.
    handoff = False
    if result["frustration_detected"]:
        mentor_row = db.execute(text("""
            SELECT c.mentor_user_id
            FROM enrollments e JOIN cohorts c ON c.id = e.cohort_id
            WHERE e.student_user_id = :sid AND e.status = 'active'
            LIMIT 1
        """), {"sid": student_id}).mappings().fetchone()
        if mentor_row and mentor_row["mentor_user_id"]:
            db.execute(text("""
                INSERT INTO interventions
                    (student_user_id, initiated_by_user_id, intervention_type,
                     trigger_reason, notes, outcome)
                VALUES
                    (:sid, :mentor, 'wellness_check',
                     'Tara detected student distress',
                     'Flagged automatically by Tara AI tutor — student expressed '
                     'discouragement during a study session. Suggest a check-in.',
                     'pending')
            """), {"sid": student_id, "mentor": mentor_row["mentor_user_id"]})
            db.commit()
            handoff = True

    return TaraChatResponse(
        reply=result["reply"], mode=result["mode"],
        sources=result["sources"],
        frustration_detected=result["frustration_detected"],
        handoff_created=handoff,
    )
