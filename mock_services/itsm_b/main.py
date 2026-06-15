import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from mock_services.itsm_b.database import get_db
from mock_services.itsm_b.models import Issue, IssueComment
from mock_services.itsm_b.schemas import (
    CommentCreate,
    CommentResponse,
    IssueCreate,
    IssueResponse,
    IssueUpdate,
    SearchRequest,
    SearchResponse,
)
from mock_services.itsm_b.seed import init_db, reset_db


app = FastAPI(title="ITSM-B Mock Service", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def _next_issue_key(db: Session) -> str:
    next_number = 100 + db.query(Issue).count() + 1
    return f"SUP-{next_number}"


def _apply_jql(query, jql: str | None):
    if not jql:
        return query

    conditions = [part.strip() for part in jql.split("AND")]
    for condition in conditions:
        if "=" not in condition:
            continue

        field, value = condition.split("=", 1)
        field = field.strip()
        value = value.strip().strip('"')

        if field == "key":
            query = query.filter(Issue.key == value)
        elif field == "status":
            query = query.filter(Issue.status == value)
        elif field == "reporter":
            query = query.filter(Issue.reporter == value)
        elif field == "assignee":
            query = query.filter(Issue.assignee == value)

    return query


@app.post("/rest/api/2/issue", response_model=IssueResponse)
def create_issue(payload: IssueCreate, db: Session = Depends(get_db)):
    issue = Issue(
        key=_next_issue_key(db),
        summary=payload.fields.summary,
        description=payload.fields.description,
        reporter=payload.fields.reporter,
        assignee=payload.fields.assignee,
        status=payload.fields.status or "Open",
        priority=payload.fields.priority,
        issue_type=payload.fields.issuetype or "Task",
    )

    db.add(issue)
    db.commit()
    db.refresh(issue)

    return issue


@app.get("/rest/api/2/issue/{key}", response_model=IssueResponse)
def get_issue(key: str, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.key == key).first()
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    return issue


@app.put("/rest/api/2/issue/{key}", response_model=IssueResponse)
def update_issue(key: str, payload: IssueUpdate, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.key == key).first()
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    values = payload.fields.model_dump(exclude_unset=True)
    if "issuetype" in values:
        values["issue_type"] = values.pop("issuetype")

    for field, value in values.items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)

    return issue


@app.post("/rest/api/2/issue/{key}/comment", response_model=CommentResponse)
def add_comment(key: str, payload: CommentCreate, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.key == key).first()
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    comment = IssueComment(
        issue_id=issue.id,
        author=payload.author,
        body=payload.body,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@app.post("/rest/api/2/search", response_model=SearchResponse)
def search_issues(payload: SearchRequest, db: Session = Depends(get_db)):
    query = _apply_jql(db.query(Issue), payload.jql)
    issues = query.order_by(Issue.id.asc()).limit(payload.maxResults).all()
    return {"total": len(issues), "issues": issues}


@app.get("/admin/reset")
def reset(db: Session = Depends(get_db)):
    return reset_db(db)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
