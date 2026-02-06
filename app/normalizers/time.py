import re

TIME_RE = re.compile(r"^([01]?\d|2[0-3])(:[0-5]\d)?$")

def normalize_time(text: str) -> str | None:
    m = TIME_RE.match(text.strip())
    if not m:
        return None

    hour = int(m.group(1))
    minute = m.group(2) or ":00"

    return f"{hour:02d}{minute}"
