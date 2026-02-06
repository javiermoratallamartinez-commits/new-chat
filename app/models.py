from dataclasses import dataclass
from typing import Optional
from app.state import ChatState

@dataclass
class ChatContext:
    session_id: str
    state: ChatState = ChatState.START

    name: Optional[str] = None
    phone: Optional[str] = None


    
from datetime import datetime
from app.db import get_db

def save_appointment(ctx, session_id: str):
    db = get_db()

    db.execute("""
        INSERT INTO appointments (
            session_id,
            name,
            phone,
            reason,
            date_text,
            date_iso,
            half_day,
            time_text,
            time_24h,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        ctx.name,
        ctx.phone,
        ctx.reason,
        ctx.date_text,
        ctx.date_iso,
        ctx.half_day,
        ctx.time_text,
        ctx.time_24h,
        "confirmed",
        datetime.utcnow().isoformat()
    ))

    db.commit()
    db.close()
