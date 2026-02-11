from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import re
import uuid

from app.context_store import get_context
from app.state import ChatState

from app.normalizers.date import normalize_date
from app.normalizers.time import normalize_time

from app.database import init_db

from app.database import engine, Base

from typing import List
from app.schemas.appointment import AppointmentResponse
  
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.appointments import get_all_appointments

app = FastAPI(title="JotaAI Core")

#----------startup----------
@app.on_event("startup")
def _startup():
    init_db()

# ---------- utils ----------
PHONE_RE = re.compile(r"^[69]\d{8}$")

def is_valid_phone(text: str) -> bool:
    return bool(PHONE_RE.fullmatch(text.strip()))

# ---------- input ----------
class ChatIn(BaseModel):
    message: str
    sessionId: str | None = None


# ---------- endpoint ----------
@app.post("/chat")
def chat(m: ChatIn):
    sid = m.sessionId or str(uuid.uuid4())
    ctx = get_context(sid)
    text = m.message.strip()

    # =========================
    # START
    # =========================
    if ctx.state == ChatState.START:
        ctx.state = ChatState.ASK_NAME
        return JSONResponse({
            "reply": "Hola 😊 ¿Cómo te llamas?",
            "sessionId": sid
        })

    # =========================
    # ASK_NAME
    # =========================
    if ctx.state == ChatState.ASK_NAME:
        if len(text) < 2:
            return JSONResponse({
                "reply": "Necesito tu nombre para continuar 😊",
                "sessionId": sid
            })

        ctx.name = text
        ctx.state = ChatState.ASK_PHONE

        return JSONResponse({
            "reply": f"Encantado, {ctx.name}. ¿Me indicas tu teléfono?",
            "sessionId": sid
        })

    # =========================
    # ASK_PHONE
    # =========================
    if ctx.state == ChatState.ASK_PHONE:
        if not is_valid_phone(text):
            return JSONResponse({
                "reply": "El teléfono debe tener 9 dígitos y empezar por 6 o 9 📞",
                "sessionId": sid
            })

        ctx.phone = text
        ctx.state = ChatState.ASK_REASON

        return JSONResponse({
            "reply": "Perfecto 👍 ¿Cuál es el motivo de la consulta?",
            "sessionId": sid
        })

    # =========================
    # ASK_REASON
    # =========================
    if ctx.state == ChatState.ASK_REASON:
        if len(text) < 3:
            return JSONResponse({
                "reply": "¿Podrías indicarme brevemente el motivo de la consulta?",
                "sessionId": sid
            })

        ctx.reason = text
        ctx.state = ChatState.ASK_DATE

        return JSONResponse({
            "reply": "Perfecto 😊 ¿Para qué día te gustaría la cita?",
            "sessionId": sid
        })


    # =========================
    # ASK_DATE
    # =========================
    if ctx.state == ChatState.ASK_DATE:
        iso_date = normalize_date(text)

        if not iso_date:
            return JSONResponse({
                "reply": (
                    "Indícame una fecha válida 😊\n\n"
                    "Ejemplos:\n"
                    "- mañana\n"
                    "- el viernes\n"
                    "- 20/01\n"
                    "- 20 de enero"
                ),
                "sessionId": sid
            })

        ctx.date_text = text     # lo que dijo el usuario
        ctx.date_iso = iso_date  # YYYY-MM-DD
        ctx.state = ChatState.ASK_HALF_DAY

        return JSONResponse({
            "reply": "Genial 😊 ¿Prefieres **por la mañana** o **por la tarde**?",
            "sessionId": sid
        })


    # =========================
    # ASK_HALF_DAY
    # =========================
    if ctx.state == ChatState.ASK_HALF_DAY:
        choice = text.lower()

        if choice not in ("mañana", "tarde"):
            return JSONResponse({
                "reply": (
                    "Por favor, elige una opción válida 👇\n\n"
                    "🟢 **mañana**\n"
                    "🟣 **tarde**"
                ),
                "sessionId": sid
            })

        ctx.half_day = choice
        ctx.state = ChatState.ASK_TIME

        return JSONResponse({
            "reply": (
                f"Perfecto 👍 Por la **{choice}**.\n\n"
                "⏰ ¿A qué **hora** te vendría bien?"
            ),
            "sessionId": sid
        })




    # =========================
    # ASK_TIME
    # =========================
    if ctx.state == ChatState.ASK_TIME:
        t24 = normalize_time(text)

        if not t24:
            return JSONResponse({
                "reply": (
                    "Indícame una **hora válida** ⏰\n\n"
                    "Ejemplos:\n"
                    "• 10\n"
                    "• 10:30\n"
                    "• 17:15"
                ),
                "sessionId": sid
            })

        hour = int(t24.split(":")[0])

        # Validación suave según franja
        if ctx.half_day == "mañana" and hour >= 14:
            return JSONResponse({
                "reply": "Esa hora parece de **tarde** 😊 Elige una hora de mañana.",
                "sessionId": sid
            })

        if ctx.half_day == "tarde" and hour < 14:
            return JSONResponse({
                "reply": "Esa hora parece de **mañana** 😊 Elige una hora de tarde.",
                "sessionId": sid
            })

        ctx.time_text = text   # lo que dijo el usuario
        ctx.time_24h = t24     # HH:MM
        ctx.state = ChatState.CONFIRMATION

        return JSONResponse({
            "reply": (
                "Perfecto 👍 Aquí tienes el resumen de tu cita:\n\n"
                f"👤 Nombre: {ctx.name}\n"
                f"📞 Teléfono: {ctx.phone}\n"
                f"📝 Motivo: {ctx.reason}\n"
                f"📅 Fecha: {ctx.date_text} ({ctx.date_iso})\n"
                f"🕒 Hora: {ctx.time_text} ({ctx.time_24h})\n\n"
                "¿Confirmamos la cita? (**sí / no**)"
            ),
            "sessionId": sid
        })


    
    # =========================
    # CONFIRMATION
    # =========================
    if ctx.state == ChatState.CONFIRMATION:
        answer = text.lower().strip()

        if answer in ("sí", "si", "s"):
            from app.models import save_appointment
            save_appointment(ctx, sid)   # ✅ guardar SOLO aquí
            ctx.state = ChatState.CONFIRMED

            return JSONResponse({
                "reply": (
                    "✅ **Cita confirmada**\n\n"
                    "Gracias 😊 Hemos registrado tu solicitud y en breve nos pondremos en contacto contigo "
                    "para confirmar la disponibilidad.\n\n"
                    "¡Que tengas un buen día!"
                ),
                "sessionId": sid
            })

        if answer in ("no", "n"):
            ctx.state = ChatState.CHANGE_WHAT
            return JSONResponse({
                "reply": (
                    "De acuerdo 👍 ¿Qué te gustaría cambiar?\n\n"
                    "1️⃣ Fecha\n"
                    "2️⃣ Hora\n"
                    "3️⃣ Motivo\n\n"
                    "Escribe el número de la opción."
                ),
                "sessionId": sid
            })

        return JSONResponse({
            "reply": "Respóndeme solo con **sí** o **no** 😊",
            "sessionId": sid
        })
        



    # =========================
    # CHANGE_WHAT
    # =========================
    if ctx.state == ChatState.CHANGE_WHAT:
        if text == "1":
            ctx.state = ChatState.ASK_DATE_EDIT
            return JSONResponse({
                "reply": "📅 De acuerdo. ¿Para qué fecha te vendría mejor la cita?",
                "sessionId": sid
            })

        if text == "2":
            ctx.state = ChatState.ASK_TIME_EDIT
            return JSONResponse({
                "reply": "⏰ Perfecto. ¿Qué hora prefieres?",
                "sessionId": sid
            })

        if text == "3":
            ctx.state = ChatState.ASK_REASON_EDIT
            return JSONResponse({
                "reply": "📝 Entendido. ¿Cuál sería ahora el motivo de la consulta?",
                "sessionId": sid
            })

        return JSONResponse({
            "reply": (
                "Por favor, elige una opción válida:\n\n"
                "1️⃣ Fecha\n"
                "2️⃣ Hora\n"
                "3️⃣ Motivo"
            ),
            "sessionId": sid
        })


    # =========================
    # ASK_DATE_EDIT
    # =========================
    if ctx.state == ChatState.ASK_DATE_EDIT:
        iso_date = normalize_date(text)

        if not iso_date:
            return JSONResponse({
                "reply": (
                    "Indícame una fecha válida 😊\n\n"
                    "Ejemplos:\n"
                    "- mañana\n"
                    "- el viernes\n"
                    "- 20/01\n"
                    "- 20 de enero"
                ),
                "sessionId": sid
            })

        ctx.date_text = text
        ctx.date_iso = iso_date
        ctx.state = ChatState.CONFIRMATION

        return JSONResponse({
            "reply": (
                "Perfecto 👍 He actualizado la **fecha**.\n\n"
                f"📋 **Resumen de tu cita:**\n"
                f"- Nombre: {ctx.name}\n"
                f"- Teléfono: {ctx.phone}\n"
                f"- Motivo: {ctx.reason}\n"
                f"- Fecha: {ctx.date_text} ({ctx.date_iso})\n"
                f"- Hora: {ctx.time_text} ({ctx.time_24h})\n\n"
                "¿Confirmamos la cita? (**sí / no**)"
            ),
            "sessionId": sid
        })


    # =========================
    # ASK_TIME_EDIT
    # =========================
    if ctx.state == ChatState.ASK_TIME_EDIT:
        t24 = normalize_time(text)

        if not t24:
            return JSONResponse({
                "reply": "Indícame una hora válida ⏰ (por ejemplo 10 o 10:30)",
                "sessionId": sid
            })

        ctx.time_text = text
        ctx.time_24h = t24
        ctx.state = ChatState.CONFIRMATION

        return JSONResponse({
            "reply": (
                "Genial 👍 He actualizado la **hora**.\n\n"
                f"📋 **Resumen de tu cita:**\n"
                f"- Nombre: {ctx.name}\n"
                f"- Teléfono: {ctx.phone}\n"
                f"- Motivo: {ctx.reason}\n"
                f"- Fecha: {ctx.date_text} ({ctx.date_iso})\n"
                f"- Hora: {ctx.time_text} ({ctx.time_24h})\n\n"
                "¿Confirmamos la cita? (**sí / no**)"
            ),
            "sessionId": sid
        })


    # =========================
    # ASK_REASON_EDIT
    # =========================
    if ctx.state == ChatState.ASK_REASON_EDIT:
        if len(text) < 3:
            return JSONResponse({
                "reply": "Indícame un motivo válido, por favor 😊",
                "sessionId": sid
            })

        ctx.reason = text
        ctx.state = ChatState.CONFIRMATION

        return JSONResponse({
            "reply": (
                "Perfecto 👍 He actualizado el **motivo**.\n\n"
                f"📋 **Resumen de tu cita:**\n"
                f"- Nombre: {ctx.name}\n"
                f"- Teléfono: {ctx.phone}\n"
                f"- Motivo: {ctx.reason}\n"
                f"- Fecha: {ctx.date}\n"
                f"- Hora: {ctx.time}\n\n"
                "¿Confirmamos la cita? (**sí / no**)"
            ),
            "sessionId": sid
        })


    # =========================
    # FALLBACK
    # =========================
    return JSONResponse({
        "reply": "Algo no ha ido bien, vamos a empezar de nuevo 😊",
        "sessionId": sid
    })
  

from app.routers.appointment import router as appointments_router

app.include_router(appointments_router)
