from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    short_description: str
    description: str | None = None
    caller_id: str | None = None
    state: str | None = "new"
    urgency: str | None = "3"
    impact: str | None = "3"
    assignment_group: str | None = None


class IncidentUpdate(BaseModel):
    short_description: str | None = None
    description: str | None = None
    caller_id: str | None = None
    state: str | None = None
    urgency: str | None = None
    impact: str | None = None
    assignment_group: str | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sys_id: str
    number: str
    short_description: str
    description: str | None
    caller_id: str | None
    state: str
    urgency: str | None
    impact: str | None
    assignment_group: str | None
    created_at: datetime
    updated_at: datetime


class ServiceNowResponse(BaseModel):
    result: IncidentResponse


class ServiceNowListResponse(BaseModel):
    result: list[IncidentResponse]
