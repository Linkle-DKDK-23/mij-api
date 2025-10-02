# app/services/email/send_email.py
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import boto3
from botocore.config import Config
from tenacity import retry, wait_exponential, stop_after_attempt
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings  # pydantic Settings想定

# ---------- Jinja2 ----------
jinja_env = Environment(
    loader=FileSystemLoader(searchpath="./app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

def render(template_name: str, **ctx) -> str:
    return jinja_env.get_template(template_name).render(**ctx)

# ---------- 共通: MIME組み立て（HTML + 任意でTEXT） ----------
def _build_mime(subject: str, from_addr: str, to_addr: str, html: str, text: str | None = None) -> str:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    if text:
        msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg.as_string()

# ---------- MailHog（SMTP） ----------
def _send_via_mailhog(to: str, subject: str, html: str) -> None:
    raw = _build_mime(subject, settings.MAIL_FROM, to, html)
    with smtplib.SMTP(settings.MAILHOG_HOST, settings.MAILHOG_PORT) as s:
        s.sendmail(settings.MAIL_FROM, [to], raw)

# ---------- SES v2（API） ----------
@retry(wait=wait_exponential(multiplier=0.5, min=1, max=10), stop=stop_after_attempt(3))
def _send_via_ses_simple(to: str, subject: str, html: str, text: str | None = None) -> None:
    client = boto3.client(
        "sesv2",
        region_name=settings.AWS_REGION,
        config=Config(retries={"max_attempts": 3, "mode": "standard"}),
    )
    content_body = {"Html": {"Data": html, "Charset": "UTF-8"}}
    if text:
        content_body["Text"] = {"Data": text, "Charset": "UTF-8"}

    kwargs = {
        "FromEmailAddress": settings.MAIL_FROM,
        "Destination": {"ToAddresses": [to]},
        "Content": {"Simple": {"Subject": {"Data": subject, "Charset": "UTF-8"}, "Body": content_body}},
    }
    if getattr(settings, "SES_CONFIGURATION_SET", None):
        kwargs["ConfigurationSetName"] = settings.SES_CONFIGURATION_SET
    client.send_email(**kwargs)

# ---------- パブリックAPI ----------
def send_thanks_email(to: str, name: str | None = None) -> None:
    """
    事前登録サンクスメールを送る。
    .envで EMAIL_ENABLED=false の場合は即return。
    """
    if not getattr(settings, "EMAIL_ENABLED", True):
        return

    subject = "【mijfans】事前登録が完了しました"
    html = render("prereg_thanks.html", name=name or "")

    try:
        backend = getattr(settings, "EMAIL_BACKEND", "mailhog").lower()
        if backend == "mailhog":
            _send_via_mailhog(to, subject, html)
            return
        elif backend == "ses":
            _send_via_ses_simple(to, subject, html)
            return
        else:
            # 未知のバックエンド指定時は送らずに例外
            raise RuntimeError(f"Unsupported EMAIL_BACKEND: {backend}")
    except Exception as e:
        print("Error sending email", e)
