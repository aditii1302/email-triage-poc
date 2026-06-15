import logging
import requests
from backend.app.config import settings
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage

logger = logging.getLogger(__name__)
STAGE_NAME = "stage6_enrich"


def _lookup_user(email: str) -> dict | None:
    try:
        response = requests.get(
            f"{settings.DIRECTORY_BASE_URL}/users",
            params={"email": email},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def run_enrichment(raw_email_id: int, extraction: dict) -> dict:
    db = SessionLocal()
    pipeline_run = None

    try:
        email_record = db.query(RawEmail).filter(RawEmail.id == raw_email_id).first()
        if not email_record:
            raise ValueError(f"RawEmail {raw_email_id} not found")

        input_payload = {
            "raw_email_id": raw_email_id,
            "sender": email_record.sender,
            "affected_users": extraction.get("affected_users", []),
        }

        pipeline_run = start_stage(db, STAGE_NAME, input_payload=input_payload)

        affected_users = extraction.get("affected_users", [])
        sender = email_record.sender or ""

        # Try affected users first, fall back to sender
        caller_info = None
        caller_unresolved = False

        for user_email in affected_users:
            info = _lookup_user(user_email)
            if info:
                caller_info = info
                break

        if not caller_info:
            # Try sender
            import re
            email_match = re.search(r"[\w\.-]+@[\w\.-]+", sender)
            if email_match:
                caller_info = _lookup_user(email_match.group())

        if not caller_info:
            caller_unresolved = True
            caller_info = {
                "upn": sender,
                "display_name": sender,
                "department": None,
                "manager": None,
            }

        output_payload = {
            "caller": caller_info,
            "caller_unresolved": caller_unresolved,
        }

        complete_stage(
            db,
            pipeline_run,
            raw_email_id=raw_email_id,
            output_payload=output_payload,
        )

        db.commit()

        logger.info(
            "stage6.completed",
            extra={
                "raw_email_id": raw_email_id,
                "caller_unresolved": caller_unresolved,
            },
        )

        return output_payload

    except Exception as exc:
        db.rollback()
        try:
            fail_stage(
                db,
                pipeline_run,
                stage_name=STAGE_NAME,
                correlation_id=None,
                input_payload={"raw_email_id": raw_email_id},
                output_payload={"error_type": type(exc).__name__},
                error_message=str(exc),
            )
            db.commit()
        except Exception:
            db.rollback()
        raise

    finally:
        db.close()
