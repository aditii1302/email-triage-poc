from sqlalchemy.orm import Session

from mock_services.itsm_b.database import Base, engine
from mock_services.itsm_b.models import Issue, IssueComment


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def reset_db(db: Session) -> dict[str, str]:
    db.query(IssueComment).delete()
    db.query(Issue).delete()
    db.commit()
    return {"status": "reset", "service": "itsm_b"}
