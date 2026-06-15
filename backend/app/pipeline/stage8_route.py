import logging
import shutil
from pathlib import Path
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage

logger = logging.getLogger(__name__)
STAGE_NAME = "stage8_route"


def _move_email(file_path, destination):
    src = Path(file_path)
    dest_dir = src.parent.parent / destination
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src.name
    shutil.move(str(src), str(dest_path))
    return str(dest_path)


def run_routing(raw_email_id, is_actionable, dedup_status, intent_reasoning=""):
    db = SessionLocal()
    pipeline_run = None
    try:
        email_record = db.query(RawEmail).filter(RawEmail.id == raw_email_id).first()
        if not email_record:
            raise ValueError(f"RawEmail {raw_email_id} not found")
        input_payload = {"raw_email_id": raw_email_id, "is_actionable": is_actionable, "dedup_status": dedup_status}
        pipeline_run = start_stage(db, STAGE_NAME, input_payload=input_payload)
        file_path = email_record.file_path
        if not is_actionable:
            destination = "no_action"
        elif dedup_status == "POSSIBLE-DUPLICATE-REVIEW":
            destination = "review"
        else:
            destination = "processed"
        new_path = None
        if file_path and Path(file_path).exists():
            new_path = _move_email(file_path, destination)
            email_record.file_path = new_path
            email_record.status = destination
        output_payload = {"destination": destination, "new_path": new_path, "intent_reasoning": intent_reasoning}
        complete_stage(db, pipeline_run, raw_email_id=raw_email_id, output_payload=output_payload)
        db.commit()
        return output_payload
    except Exception as exc:
        db.rollback()
        try:
            fail_stage(db, pipeline_run, stage_name=STAGE_NAME, correlation_id=None, input_payload={"raw_email_id": raw_email_id}, output_payload={"error_type": type(exc).__name__}, error_message=str(exc))
            db.commit()
        except Exception:
            db.rollback()
        raise
    finally:
        db.close()
