import logging
import yaml
import chromadb
from sentence_transformers import SentenceTransformer
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage

logger = logging.getLogger(__name__)
STAGE_NAME = "stage5_dedup"

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("tickets")


def _load_settings():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def run_dedup(raw_email_id: int, extraction: dict) -> dict:
    db = SessionLocal()
    pipeline_run = None

    try:
        email_record = db.query(RawEmail).filter(RawEmail.id == raw_email_id).first()
        if not email_record:
            raise ValueError(f"RawEmail {raw_email_id} not found")

        input_payload = {
            "raw_email_id": raw_email_id,
            "extraction": extraction,
        }

        pipeline_run = start_stage(db, STAGE_NAME, input_payload=input_payload)

        settings = _load_settings()
        high_threshold = settings["dedup"]["high_threshold"]
        low_threshold = settings["dedup"]["low_threshold"]

        problem_statement = extraction.get("problem_statement", "")
        application = extraction.get("impacted_application", "") or ""
        business_unit = extraction.get("impacted_business_unit", "") or ""
        affected_users = extraction.get("affected_users", [])

        embedding = model.encode(problem_statement).tolist()

        results = collection.query(
            query_embeddings=[embedding],
            n_results=5,
            include=["metadatas", "distances"],
        )

        status = "NONE"
        matched_ticket_id = None

        if results and results["distances"] and results["distances"][0]:
            for distance, metadata in zip(
                results["distances"][0],
                results["metadatas"][0]
            ):
                similarity = 1 - distance

                meta_app = metadata.get("application", "").lower()
                meta_raw_app = metadata.get("raw_application", "").lower()
                app_lower = application.lower()
                same_app = (
                    meta_app == app_lower
                    or meta_raw_app == app_lower
                    or meta_app in app_lower
                    or app_lower in meta_app
                    or meta_raw_app in app_lower
                    or app_lower in meta_raw_app
                    or meta_app == ""
                )

                same_user = any(
                    u in metadata.get("affected_users", "")
                    for u in affected_users
                )

                same_unit = (
                    metadata.get("business_unit", "").lower()
                    == business_unit.lower()
                )

                if same_app and (same_user or same_unit):
                    if similarity >= high_threshold:
                        status = "LINKED-TO-EXISTING"
                        matched_ticket_id = metadata.get("ticket_id")
                        break
                    elif similarity >= low_threshold:
                        status = "POSSIBLE-DUPLICATE-REVIEW"
                        matched_ticket_id = metadata.get("ticket_id")

        output_payload = {
            "ai_duplicate_check_status": status,
            "matched_ticket_id": matched_ticket_id,
            "problem_statement": problem_statement,
            "application": application,
        }

        complete_stage(
            db,
            pipeline_run,
            raw_email_id=raw_email_id,
            output_payload=output_payload,
        )

        db.commit()

        logger.info(
            "stage5.completed",
            extra={
                "raw_email_id": raw_email_id,
                "dedup_status": status,
                "matched_ticket_id": matched_ticket_id,
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


def index_ticket(ticket_id: str, problem_statement: str, application: str, business_unit: str, affected_users: list, raw_application: str = ""):
    embedding = model.encode(problem_statement).tolist()
    collection.upsert(
        ids=[ticket_id],
        embeddings=[embedding],
        metadatas=[{
            "ticket_id": ticket_id,
            "application": application,
            "raw_application": raw_application.lower(),
            "business_unit": business_unit,
            "affected_users": ",".join(affected_users),
        }],
    )
