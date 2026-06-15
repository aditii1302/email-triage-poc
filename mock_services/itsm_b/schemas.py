from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IssueFields(BaseModel):
    summary: str
    description: str | None = None
    reporter: str | None = None
    assignee: str | None = None
    priority: str | None = None
    issuetype: str | None = "Task"
    status: str | None = "Open"


class IssueCreate(BaseModel):
    fields: IssueFields


class IssueUpdateFields(BaseModel):
    summary: str | None = None
    description: str | None = None
    reporter: str | None = None
    assignee: str | None = None
    priority: str | None = None
    issuetype: str | None = None
    status: str | None = None


class IssueUpdate(BaseModel):
    fields: IssueUpdateFields


class CommentCreate(BaseModel):
    body: str
    author: str | None = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author: str | None
    body: str
    created_at: datetime


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    summary: str
    description: str | None
    reporter: str | None
    assignee: str | None
    status: str
    priority: str | None
    issue_type: str
    created_at: datetime
    updated_at: datetime


class SearchRequest(BaseModel):
    jql: str | None = None
    maxResults: int = 50


class SearchResponse(BaseModel):
    total: int
    issues: list[IssueResponse]
