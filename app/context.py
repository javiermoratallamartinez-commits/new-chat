from app.state import ChatState

class ChatContext:
    def __init__(self):
        self.state: ChatState = ChatState.START
        self.is_editing = False
        self.name: str | None = None
        self.phone: str | None = None
        self.reason: str | None = None
        self.date_choice: str | None = None