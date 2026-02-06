# app/normalizers/date.py
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")

MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

WEEKDAYS = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}

def _today() -> date:
    return datetime.now(TZ).date()

def _next_weekday(target_weekday: int, base: date) -> date:
    # próxima ocurrencia (si hoy es el mismo día, lo toma como hoy+7)
    days_ahead = (target_weekday - base.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return base + timedelta(days=days_ahead)

def _safe_date(y: int, m: int, d: int) -> date | None:
    try:
        return date(y, m, d)
    except ValueError:
        return None

def normalize_date(text: str) -> str | None:
    """
    Devuelve ISO YYYY-MM-DD o None.
    Soporta:
    - hoy / mañana / pasado mañana
    - viernes / el viernes
    - 20/01 o 20/01/2026
    - 20 de enero (y opcional año: 20 de enero de 2027)
    Regla: si no hay año y cae en pasado => usamos el próximo año.
    """
    if not text:
        return None

    raw = text.strip().lower()

    # Limpieza básica
    raw = re.sub(r"\s+", " ", raw)

    base = _today()

    # -------------------------
    # Relativas
    # -------------------------
    if raw in ("hoy",):
        return base.isoformat()
    if raw in ("mañana", "manana"):
        return (base + timedelta(days=1)).isoformat()
    if raw in ("pasado mañana", "pasado manana"):
        return (base + timedelta(days=2)).isoformat()

    # -------------------------
    # Día de la semana
    # -------------------------
    # "viernes" o "el viernes"
    m_wd = re.fullmatch(r"(?:el\s+)?(lunes|martes|miercoles|miércoles|jueves|viernes|sabado|sábado|domingo)", raw)
    if m_wd:
        wd = WEEKDAYS[m_wd.group(1)]
        d = _next_weekday(wd, base)
        return d.isoformat()

    # -------------------------
    # Formato numérico: DD/MM o DD/MM/YYYY
    # -------------------------
    m_num = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", raw)
    if m_num:
        d = int(m_num.group(1))
        m = int(m_num.group(2))
        y = int(m_num.group(3)) if m_num.group(3) else base.year

        candidate = _safe_date(y, m, d)
        if not candidate:
            return None

        # si no hay año explícito y la fecha ya pasó, saltamos al año siguiente
        if m_num.group(3) is None and candidate < base:
            candidate = _safe_date(y + 1, m, d)
            if not candidate:
                return None

        return candidate.isoformat()

    # -------------------------
    # Formato texto: "20 de enero" (y opcional "de 2027")
    # -------------------------
    # acepta también "20 enero" (sin 'de')
    m_txt = re.fullmatch(
        r"(\d{1,2})\s*(?:de\s+)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)(?:\s+de\s+(\d{4}))?",
        raw
    )
    if m_txt:
        d = int(m_txt.group(1))
        month_name = m_txt.group(2)
        m = MONTHS.get(month_name)
        y = int(m_txt.group(3)) if m_txt.group(3) else base.year

        candidate = _safe_date(y, m, d)
        if not candidate:
            return None

        # si no hay año explícito y ya pasó, usa el próximo año
        if m_txt.group(3) is None and candidate < base:
            candidate = _safe_date(y + 1, m, d)
            if not candidate:
                return None

        return candidate.isoformat()

    # No reconocido
    return None
