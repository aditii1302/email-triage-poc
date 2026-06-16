import os
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.db import SessionLocal
from backend.app.models.raw_email import RawEmail
from backend.app.models.pipeline_run import PipelineRun

app = FastAPI(title="Email Triage POC API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulateEmailRequest(BaseModel):
    mailbox: str
    from_addr: str
    to_addr: str
    subject: str
    body: str


class ReviewResolveRequest(BaseModel):
    action: str


@app.get("/api/runs")
def get_runs():
    db = SessionLocal()
    try:
        emails = db.query(RawEmail).order_by(RawEmail.id.desc()).limit(50).all()
        runs = db.query(PipelineRun).all()

        stages_by_email = {}
        for run in runs:
            eid = run.raw_email_id
            if eid not in stages_by_email:
                stages_by_email[eid] = 0
            if run.status in ("completed", "success"):
                stage_num = 0
                if "stage1" in run.stage_name: stage_num = 1
                elif "stage2" in run.stage_name: stage_num = 2
                elif "stage3" in run.stage_name: stage_num = 3
                elif "stage4" in run.stage_name: stage_num = 4
                elif "stage5" in run.stage_name: stage_num = 5
                elif "stage6" in run.stage_name: stage_num = 6
                elif "stage7" in run.stage_name: stage_num = 7
                elif "stage8" in run.stage_name: stage_num = 8
                if stage_num > stages_by_email[eid]:
                    stages_by_email[eid] = stage_num

        result = []
        for email in emails:
            stages_completed = stages_by_email.get(email.id, 0)
            outcome = None
            if email.status == "processed":
                outcome = "Ticket Created"
            elif email.status == "review":
                outcome = "Review"
            elif email.status == "no_action":
                outcome = "No Action"

            result.append({
                "id": email.id,
                "subject": email.subject,
                "mailbox": email.mailbox,
                "sender": email.sender,
                "stages_completed": stages_completed,
                "outcome": outcome,
                "created_at": str(email.created_at),
            })
        return result
    finally:
        db.close()


@app.get("/api/runs/{run_id}")
def get_run_detail(run_id: int):
    db = SessionLocal()
    try:
        email = db.query(RawEmail).filter(RawEmail.id == run_id).first()
        if not email:
            return {"error": "Not found"}

        stages = db.query(PipelineRun).filter(
            PipelineRun.raw_email_id == run_id
        ).order_by(PipelineRun.id.asc()).all()

        return {
            "id": email.id,
            "subject": email.subject,
            "sender": email.sender,
            "mailbox": email.mailbox,
            "body": email.body,
            "stages": [
                {
                    "stage_name": s.stage_name,
                    "status": s.status,
                    "input_payload": s.input_payload,
                    "output_payload": s.output_payload,
                    "created_at": str(s.started_at),
                }
                for s in stages
            ]
        }
    finally:
        db.close()


@app.post("/api/simulate/email")
def simulate_email(req: SimulateEmailRequest):
    msg = MIMEMultipart()
    msg["From"] = req.from_addr
    msg["To"] = req.to_addr
    msg["Subject"] = req.subject if req.subject and req.subject.strip() else "(no subject)"
    msg["Message-ID"] = f"<sim-{datetime.utcnow().timestamp()}@example.com>"
    msg.attach(MIMEText(req.body, "plain"))

    folder = f"mailboxes/{req.mailbox}/new"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/sim_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.eml"

    with open(filename, "w") as f:
        f.write(msg.as_string())

    return {"status": "ok", "file": filename}


@app.get("/api/tickets")
def get_tickets():
    import requests as req
    db = SessionLocal()
    try:
        a = req.get("http://localhost:8001/api/now/table/incident", timeout=5).json()
        b = req.post("http://localhost:8002/rest/api/2/search",
                     json={"jql": ""}, timeout=5).json()

        itsm_a = {t["number"]: t for t in a.get("result", [])}
        itsm_b_list = b.get("issues", [])

        # Get AI fields from pipeline runs
        stage3_runs = db.query(PipelineRun).filter(PipelineRun.stage_name == "stage3_extract").all()
        stage4_runs = db.query(PipelineRun).filter(PipelineRun.stage_name == "stage4_classify").all()
        stage5_runs = db.query(PipelineRun).filter(PipelineRun.stage_name == "stage5_dedup").all()
        stage2_runs = db.query(PipelineRun).filter(PipelineRun.stage_name == "stage2_intent").all()

        stage3_by_email = {r.raw_email_id: r.output_payload for r in stage3_runs}
        stage4_by_email = {r.raw_email_id: r.output_payload for r in stage4_runs}
        stage5_by_email = {r.raw_email_id: r.output_payload for r in stage5_runs}
        stage2_by_email = {r.raw_email_id: r.output_payload for r in stage2_runs}

        emails = db.query(RawEmail).filter(RawEmail.status == "processed").order_by(RawEmail.id.asc()).all()

        tickets = []
        for i, (number, incident) in enumerate(itsm_a.items()):
            itsm_b = itsm_b_list[i] if i < len(itsm_b_list) else {}
            email = emails[i] if i < len(emails) else None
            eid = email.id if email else None

            s3 = stage3_by_email.get(eid, {}) or {}
            s4 = stage4_by_email.get(eid, {}) or {}
            s5 = stage5_by_email.get(eid, {}) or {}
            s2 = stage2_by_email.get(eid, {}) or {}

            tickets.append({
                "itsm_a_id": incident.get("sys_id"),
                "itsm_a_number": number,
                "itsm_b_key": itsm_b.get("key"),
                "short_description": incident.get("short_description"),
                "priority": s4.get("priority", incident.get("urgency")),
                "caller": incident.get("caller_id"),
                "ai_impacted_application": s3.get("impacted_application", ""),
                "ai_impacted_business_unit": s3.get("impacted_business_unit", ""),
                "ai_duplicate_check_status": s5.get("ai_duplicate_check_status", ""),
                "ai_intent_confidence": s2.get("confidence", ""),
                "category": s4.get("category", ""),
            })
        return tickets
    except Exception as e:
        return []
    finally:
        db.close()


@app.get("/api/review")
def get_review():
    db = SessionLocal()
    try:
        emails = db.query(RawEmail).filter(RawEmail.status == "review").all()
        result = []
        for email in emails:
            stage = db.query(PipelineRun).filter(
                PipelineRun.raw_email_id == email.id,
                PipelineRun.stage_name == "stage5_dedup"
            ).first()

            output = stage.output_payload if stage else {}
            result.append({
                "run_id": email.id,
                "subject": email.subject,
                "mailbox": email.mailbox,
                "problem_statement": output.get("problem_statement", ""),
                "new_ticket": "",
                "matched_ticket": output.get("matched_ticket_id", ""),
            })
        return result
    finally:
        db.close()


@app.post("/api/review/{run_id}/resolve")
def resolve_review(run_id: int, req: ReviewResolveRequest):
    db = SessionLocal()
    try:
        email = db.query(RawEmail).filter(RawEmail.id == run_id).first()
        if email:
            email.status = "processed"
            db.commit()
        return {"status": "ok", "action": req.action}
    finally:
        db.close()


@app.get("/api/config")
def get_config():
    import yaml
    config = {}
    for fname in ["settings.yaml", "sop_rules.yaml", "dl_inventory.yaml"]:
        try:
            with open(f"config/{fname}") as f:
                config[fname] = yaml.safe_load(f)
        except Exception:
            config[fname] = "Could not load"
    try:
        with open("config/app_catalogue.csv") as f:
            config["app_catalogue.csv"] = f.read()
    except Exception:
        pass
    return config


@app.get("/api/metrics")
def get_metrics():
    db = SessionLocal()
    try:
        total = db.query(RawEmail).count()
        processed = db.query(RawEmail).filter(RawEmail.status == "processed").count()
        review = db.query(RawEmail).filter(RawEmail.status == "review").count()
        no_action = db.query(RawEmail).filter(RawEmail.status == "no_action").count()
        return {
            "total_emails": total,
            "tickets_created": processed,
            "review_queue": review,
            "no_action": no_action,
        }
    finally:
        db.close()
