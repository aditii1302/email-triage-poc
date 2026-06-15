from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from backend.app.models.pipeline_run import PipelineRun


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def start_stage(
    db: Session,
    stage_name: str,
    *,
    correlation_id: str | None = None,
    raw_email_id: int | None = None,
    input_payload: dict[str, Any] | None = None,
) -> PipelineRun:
    pipeline_run = PipelineRun(
        correlation_id=correlation_id or str(uuid4()),
        raw_email_id=raw_email_id,
        stage_name=stage_name,
        status="running",
        input_payload=input_payload or {},
        started_at=_utc_now(),
    )
    db.add(pipeline_run)
    db.flush()
    return pipeline_run


def complete_stage(
    db: Session,
    pipeline_run: PipelineRun,
    *,
    raw_email_id: int | None = None,
    output_payload: dict[str, Any] | None = None,
) -> PipelineRun:
    pipeline_run.raw_email_id = raw_email_id or pipeline_run.raw_email_id
    pipeline_run.status = "success"
    pipeline_run.output_payload = output_payload or {}
    pipeline_run.error_message = None
    pipeline_run.completed_at = _utc_now()
    db.flush()
    return pipeline_run


def fail_stage(
    db: Session,
    pipeline_run: PipelineRun | None = None,
    *,
    stage_name: str | None = None,
    correlation_id: str | None = None,
    raw_email_id: int | None = None,
    input_payload: dict[str, Any] | None = None,
    output_payload: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> PipelineRun:
    if pipeline_run is None or not inspect(pipeline_run).persistent:
        pipeline_run = PipelineRun(
            correlation_id=correlation_id or str(uuid4()),
            stage_name=stage_name or "unknown",
            input_payload=input_payload or {},
            started_at=_utc_now(),
        )
        db.add(pipeline_run)

    pipeline_run.raw_email_id = raw_email_id or pipeline_run.raw_email_id
    pipeline_run.status = "failed"
    pipeline_run.output_payload = output_payload or {}
    pipeline_run.error_message = error_message
    pipeline_run.completed_at = _utc_now()
    db.flush()
    return pipeline_run
