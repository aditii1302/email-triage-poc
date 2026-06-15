import logging
import requests
from backend.app.config import settings
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage
from backend.app.pipeline.stage5_dedup import index_ticket

logger = logging.getLogger(__name__)
STAGE_NAME = "stage7_ticket"


def _create_itsm_a_ticket(payload: dict) -> dict:
    response = requests.post(
        f"{settings.ITSM_A_BASE_URL}/api/now/table/incident",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["result"]


def _create_itsm_b_ticket(payload: dict) -> dict:
    response = requests.post(
        f"{settings.ITSM_B_BASE_URL}/rest/api/2/issue",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def run_ticket_creation(
    raw_email_id: int,
    extraction: dict,
    classification: dict,
    enrichment: dict,
    dedup: dict,
) -> dict:
    db = SessionLocal()
    pipeline_run = None

    try:
        email_record = db.query(RawEmail).filter(RawEmail.id == raw_email_id).first()
        if not email_record:
            raise ValueError(f"RawEmail {raw_email_id} not found")

        input_payload = {"raw_email_id": raw_email_id}
        pipeline_run = start_stage(db, STAGE_NAME, input_payload=input_payload)

        caller = enrichment.get("caller", {})
        problem_statement = extraction.get("problem_statement", "")
        application = classification.get("canonical_application", "")
        category = classification.get("category", "General Request")
        priority = classification.get("priority", "P3")
        business_unit = extraction.get("impacted_business_unit", "")
        affected_users = extraction.get("affected_users", [])
        dedup_status = dedup.get("ai_duplicate_check_status", "NONE")
        thread_id = email_record.conversation_id or ""

        description = (
            f"{problem_statement}\n\n"
            f"Impacted Application: {application}\n"
            f"Business Unit: {business_unit}\n"
            f"Error Details: {extraction.get('error_details', 'N/A')}\n"
            f"Affected Users: {', '.join(affected_users)}\n"
            f"Source Email Thread ID: {thread_id}\n"
            f"AI Duplicate Check: {dedup_status}"
        )

        # Create ITSM-A incident
        itsm_a_payload = {
            "short_description": problem_statement[:200],
            "description": description,
            "caller_id": caller.get("upn", ""),
            "state": "new",
            "urgency": "3",
            "impact": "3",
        }
        itsm_a_result = _create_itsm_a_ticket(itsm_a_payload)
        itsm_a_id = itsm_a_result.get("sys_id")
        itsm_a_number = itsm_a_result.get("number")

        # Create ITSM-B issue
        itsm_b_payload = {
            "fields": {
                "summary": problem_statement[:200],
                "description": description,
                "reporter": caller.get("upn", ""),
                "status": "Open",
                "priority": priority,
                "issuetype": "Incident",
            }
        }
        itsm_b_result = _create_itsm_b_ticket(itsm_b_payload)
        itsm_b_key = itsm_b_result.get("key")

        # Index in ChromaDB for future dedup
        index_ticket(
            ticket_id=itsm_a_number,
            problem_statement=problem_statement,
            application=application,
            business_unit=business_unit or "",
            affected_users=affected_users,
        )

        output_payload = {
            "itsm_a_id": itsm_a_id,
            "itsm_a_number": itsm_a_number,
            "itsm_b_key": itsm_b_key,
            "category": category,
            "priority": priority,
            "dedup_status": dedup_status,
        }

        complete_stage(
            db,
            pipeline_run,
            raw_email_id=raw_email_id,
            output_payload=output_payload,
        )

        db.commit()

        logger.info(
            "stage7.completed",
            extra={
                "raw_email_id": raw_email_id,
                "itsm_a_number": itsm_a_number,
                "itsm_b_key": itsm_b_key,
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
