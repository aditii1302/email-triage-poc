import logging
import yaml
import csv
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.utils.pipeline_logger import complete_stage, fail_stage, start_stage

logger = logging.getLogger(__name__)
STAGE_NAME = "stage4_classify"


def _load_sop_rules():
    with open("config/sop_rules.yaml", "r") as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])


def _load_settings():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)


def _load_app_catalogue():
    catalogue = {}
    with open("config/app_catalogue.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            canonical = row["canonical_name"]
            aliases = row["aliases"].split("|")
            for alias in aliases:
                catalogue[alias.lower().strip()] = canonical
            catalogue[canonical.lower().strip()] = canonical
    return catalogue


def _apply_sop_rules(rules, application, problem_statement, business_unit):
    text = (problem_statement or "").lower()
    app = (application or "").lower()
    unit = (business_unit or "").lower()

    for rule in rules:
        if "default" in rule and rule["default"]:
            return rule["category"]

        match = rule.get("match", {})

        if "application" in match:
            if match["application"].lower() in app:
                return rule["category"]

        if "keywords" in match:
            for keyword in match["keywords"]:
                if keyword.lower() in text:
                    return rule["category"]

        if "business_unit" in match:
            if match["business_unit"].lower() in unit:
                return rule["category"]

    return "General Request"


def run_classification(raw_email_id: int, extraction: dict) -> dict:
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

        rules = _load_sop_rules()
        settings = _load_settings()
        catalogue = _load_app_catalogue()

        stated_category = extraction.get("stated_category")
        application = extraction.get("impacted_application", "")
        problem_statement = extraction.get("problem_statement", "")
        business_unit = extraction.get("impacted_business_unit", "")

        # Match application against catalogue
        canonical_app = catalogue.get((application or "").lower().strip(), application)

        # Use stated category if present, otherwise apply SOP rules
        if stated_category:
            category = stated_category
        else:
            category = _apply_sop_rules(rules, canonical_app, problem_statement, business_unit)

        priority = settings.get("priority_default", "P3")

        output_payload = {
            "category": category,
            "priority": priority,
            "canonical_application": canonical_app,
            "stated_category_used": bool(stated_category),
        }

        complete_stage(
            db,
            pipeline_run,
            raw_email_id=raw_email_id,
            output_payload=output_payload,
        )

        db.commit()

        logger.info(
            "stage4.completed",
            extra={
                "raw_email_id": raw_email_id,
                "category": category,
                "priority": priority,
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
