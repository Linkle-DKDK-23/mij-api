# app/routers/debug_email.py
from fastapi import APIRouter, Query
from pydantic import EmailStr
from app.services.email.send_email import send_templated_email
from app.core.config import settings
router = APIRouter()

@router.post("/send-email")
def send_email(to: EmailStr = Query(...), subject: str = "STG debug mail"):
    send_templated_email(
        to=str(to),
        subject=subject,
        template_html="prereg_thanks.html",
        ctx={"name": "STG Debug"},
        tags={"category": "debug"}
    )
    return {"ok": True}


@router.get("/email-status")
def email_status():
    env = (getattr(settings, "ENV", "local") or "local").lower()
    backend = (getattr(settings, "EMAIL_BACKEND", "") or "").lower()
    effective = "mailhog" if backend in ("", "auto") and env in ("local","dev") \
                else ("ses" if backend in ("", "auto") else backend)
    return {
        "ENV": settings.ENV,
        "EMAIL_BACKEND": settings.EMAIL_BACKEND,
        "effective_backend": effective,
        "SES_CONFIGURATION_SET": getattr(settings, "SES_CONFIGURATION_SET", None),
        "AWS_REGION": getattr(settings, "AWS_REGION", None),
    }