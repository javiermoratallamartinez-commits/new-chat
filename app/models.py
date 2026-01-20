from dataclasses import dataclass
from typing import Optional
from app.state import ChatState

@dataclass
class ChatContext:
    session_id: str
    state: ChatState = ChatState.START

    name: Optional[str] = None
    phone: Optional[str] = None
