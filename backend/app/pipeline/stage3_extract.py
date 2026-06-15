import logging
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.adapters.ollama_llm import OllamaLLMClient
from backend.app.interfaces.llm_client import AttachmentContent
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage

logger = logging.getLogger(__name__)
STAGE_NAME = "stage3_extract"

llm_client = OllamaLLMClient()


def run_extraction(raw_email_id: int) -> dict:
    db = SessionLocal()
    pipeline_run = None

    try:
        email_record = db.query(RawEmail).filter(RawEmail.id == raw_email_id).first()

        if not email_record:
            raise ValueError(f"RawEmail {raw_email_id} not found")

        input_payload = {
            "raw_email_id": raw_email_id,
            "subject": email_record.subject,
        }

        pipeline_run = start_stage(db, STAGE_NAME, input_payload=input_payload)

        thread_text = f"Subject: {email_record.subject}\nFrom: {email_record.sender}\n\n{email_record.body}"

        # Load attachment contents if any
        attachments = []
        if email_record.attachment_count and email_record.attachment_count > 0:
            from backend.app.parsing.pdf_parser import parse_pdf
            from backend.app.parsing.docx_parser import parse_docx
            from backend.app.parsing.image_parser import parse_image
            import os

            for path in (email_record.file_path or "").split(","):
                path = path.strip()
                if not path or not os.path.exists(path):
                    continue
                ext = os.path.splitext(path)[1].lower()
                if ext == ".pdf":
                    content = parse_pdf(path)
                elif ext == ".docx":
                    content = parse_docx(path)
                elif ext in (".png", ".jpg", ".jpeg"):
                    with open(path, "rb") as f:
                        content = llm_client.describe_image(f.read(), hint="")
                else:
                    content = ""
                attachments.append(
                    AttachmentContent(filename=os.path.basename(path), content=content)
                )

        result = llm_client.extract(thread_text, attachments)

        output_payload = result.model_dump()

        complete_stage(
            db,
            pipeline_run,
            raw_email_id=raw_email_id,
            output_payload=output_payload,
        )

        db.commit()

        logger.info(
            "stage3.completed",
            extra={
                "raw_email_id": raw_email_id,
                "impacted_application": result.impacted_application,
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
