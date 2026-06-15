from uuid import uuid4

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from mock_services.itsm_a.database import get_db
from mock_services.itsm_a.models import Incident
from mock_services.itsm_a.schemas import (
    IncidentCreate,
    IncidentUpdate,
    ServiceNowListResponse,
    ServiceNowResponse,
)
from mock_services.itsm_a.seed import init_db, reset_db


app = FastAPI(title="ITSM-A Mock Service", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def _next_incident_number(db: Session) -> str:
    next_id = (db.query(Incident).count() + 1)
    return f"INC00100{next_id:02d}"


def _apply_sysparm_query(query, sysparm_query: str | None):
    if not sysparm_query:
        return query

    for condition in sysparm_query.split("^"):
        if "=" not in condition:
            continue

        field, value = condition.split("=", 1)
        column = getattr(Incident, field.strip(), None)
        if column is not None:
            query = query.filter(column == value.strip())

    return query


@app.post("/api/now/table/incident", response_model=ServiceNowResponse)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(
        sys_id=str(uuid4()),
        number=_next_incident_number(db),
        short_description=payload.short_description,
        description=payload.description,
        caller_id=payload.caller_id,
        state=payload.state or "new",
        urgency=payload.urgency,
        impact=payload.impact,
        assignment_group=payload.assignment_group,
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {"result": incident}


@app.get("/api/now/table/incident/{sys_id}", response_model=ServiceNowResponse)
def get_incident(sys_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.sys_id == sys_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {"result": incident}


@app.patch("/api/now/table/incident/{sys_id}", response_model=ServiceNowResponse)
def update_incident(
    sys_id: str,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(Incident.sys_id == sys_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)

    return {"result": incident}


@app.get("/api/now/table/incident", response_model=ServiceNowListResponse)
def search_incidents(
    sysparm_query: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = _apply_sysparm_query(db.query(Incident), sysparm_query)
    return {"result": query.order_by(Incident.id.asc()).all()}


@app.get("/admin/reset")
def reset(db: Session = Depends(get_db)):
    return reset_db(db)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
