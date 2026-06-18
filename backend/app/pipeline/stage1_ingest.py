import logging
from email.utils import getaddresses
from pathlib import Path

from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.parsing.eml_parser import parse_eml
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage

logger = logging.getLogger(__name__)
STAGE_NAME = "stage1_ingest"


def _mailbox_from_path(file_path: str) -> str:
    path = Path(file_path)
    parts = path.parts

    if "mailboxes" in parts:
        mailbox_index = parts.index("mailboxes") + 1
        if mailbox_index < len(parts):
            return parts[mailbox_index]

    return path.parent.name or "unknown"


def _address_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value

    addresses = [address for _, address in getaddresses([value]) if address]
    return addresses or [value]


def process_email(file_path: str) -> RawEmail:
    input_payload = {"file_path": file_path}
    db = SessionLocal()
    pipeline_run = None
    correlation_id = None

    try:
        logger.info(
            "pipeline.stage.started",
            extra={"stage_name": STAGE_NAME, "file_path": file_path},
        )
        pipeline_run = start_stage(
            db,
            STAGE_NAME,
            input_payload=input_payload,
        )
        correlation_id = pipeline_run.correlation_id

        email_data = parse_eml(file_path)
        recipients = _address_list(email_data.get("recipients"))
        cc = _address_list(email_data.get("cc"))
        attachments = email_data.get("attachments", [])

        email_record = RawEmail(
            mailbox=_mailbox_from_path(file_path),
            message_id=email_data.get("message_id"),
            conversation_id=email_data.get("conversation_id"),
            sender=email_data.get("sender"),
            recipients=recipients,
            cc=cc,
            subject=email_data.get("subject"),
            body=email_data.get("body"),
            attachment_count=len(attachments),
            attachment_paths=attachments,
            file_path=file_path,
            status="new",
        )

        db.add(email_record)
        db.flush()

        complete_stage(
            db,
            pipeline_run,
            raw_email_id=email_record.id,
            output_payload={
                "raw_email_id": email_record.id,
                "mailbox": email_record.mailbox,
                "message_id": email_record.message_id,
                "subject": email_record.subject,
                "sender": email_record.sender,
                "recipients": email_record.recipients,
                "cc": email_record.cc,
                "conversation_id": email_record.conversation_id,
                "attachment_count": email_record.attachment_count,
                "file_path": email_record.file_path,
                "attachments": attachments,
            },
        )

        db.commit()
        db.refresh(email_record)

        logger.info(
            "pipeline.stage.completed",
            extra={
                "stage_name": STAGE_NAME,
                "correlation_id": correlation_id,
                "raw_email_id": email_record.id,
                "file_path": file_path,
            },
        )

        return email_record

    except Exception as exc:
        db.rollback()

        try:
            fail_stage(
                db,
                pipeline_run,
                stage_name=STAGE_NAME,
                correlation_id=correlation_id,
                input_payload=input_payload,
                output_payload={"error_type": type(exc).__name__},
                error_message=str(exc),
            )
            db.commit()
        except Exception:
            db.rollback()
            logger.exception(
                "pipeline.stage.failure_logging_failed",
                extra={"stage_name": STAGE_NAME, "file_path": file_path},
            )

        logger.exception(
            "pipeline.stage.failed",
            extra={
                "stage_name": STAGE_NAME,
                "correlation_id": correlation_id,
                "file_path": file_path,
            },
        )

        raise

    finally:
        db.close()
