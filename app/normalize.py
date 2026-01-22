from datetime import datetime, timedelta
import re

# =========================
# FECHA
# =========================
def normalize_date(text: str) -> str | None:
    t = text.lower().strip()

    today = datetime.now().date()

    if t == "hoy":
        return today.isoformat()

    if t == "mañana":
        return (today + timedelta(days=1)).isoformat()

    # dd/mm o dd-mm
    m = re.match(r"(\d{1,2})[/-](\d{1,2})", t)
    if m:
        day, month = map(int, m.groups())
        year = today.year
        return datetime(year, month, day).date().isoformat()

    # dd de mes
    m = re.match(r"(\d{1,2}) de (\w+)", t)
    if m:
        months = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        day = int(m.group(1))
        month = months.get(m.group(2))
        if month:
            return datetime(today.year, month, day).date().isoformat()

    return None


# =========================
# HORA
# =========================
def normalize_time(text: str) -> str | None:
    t = text.strip()

    # 10 → 10:00
    if re.fullmatch(r"\d{1,2}", t):
        return f"{int(t):02d}:00"

    # 10:30
    if re.fullmatch(r"\d{1,2}:\d{2}", t):
        h, m = map(int, t.split(":"))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"

    return None
