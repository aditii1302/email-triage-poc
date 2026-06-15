import logging
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.adapters.ollama_llm import OllamaLLMClient
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage

logger = logging.getLogger(__name__)
STAGE_NAME = "stage2_intent"

llm_client = OllamaLLMClient()


def run_intent_classification(raw_email_id: int) -> dict:
    db = SessionLocal()
    pipeline_run = None

    try:
        email_record = db.query(RawEmail).filter(RawEmail.id == raw_email_id).first()

        if not email_record:
            raise ValueError(f"RawEmail {raw_email_id} not found")

        input_payload = {
            "raw_email_id": raw_email_id,
            "subject": email_record.subject,
            "sender": email_record.sender,
        }

        pipeline_run = start_stage(db, STAGE_NAME, input_payload=input_payload)

        thread_text = f"Subject: {email_record.subject}\nFrom: {email_record.sender}\n\n{email_record.body}"
        recipients = email_record.recipients or []

        result = llm_client.classify_intent(thread_text, recipients)

        output_payload = result.model_dump()

        complete_stage(
            db,
            pipeline_run,
            raw_email_id=raw_email_id,
            output_payload=output_payload,
        )

        db.commit()

        logger.info(
            "stage2.completed",
            extra={
                "raw_email_id": raw_email_id,
                "is_actionable": result.is_actionable,
                "confidence": result.confidence,
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
