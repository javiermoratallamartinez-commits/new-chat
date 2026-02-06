from app.state import ChatState

class ChatContext:
    def __init__(self):
        self.state = ChatState.START

        self.name: str | None = None
        self.phone: str | None = None
        self.reason: str | None = None

        # Texto del usuario
        self.date_text: str | None = None
        self.time_text: str | None = None
        self.half_day: str | None = None   # "mañana" | "tarde"

        # Normalizado
        self.date_iso: str | None = None   # YYYY-MM-DD
        self.time_24h: str | None = None   # HH:MM
