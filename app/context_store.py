from app.context import ChatContext

_CONTEXTS: dict[str, ChatContext] = {}

def get_context(session_id: str) -> ChatContext:
    if session_id not in _CONTEXTS:
        _CONTEXTS[session_id] = ChatContext(session_id=session_id)
    return _CONTEXTS[session_id]
