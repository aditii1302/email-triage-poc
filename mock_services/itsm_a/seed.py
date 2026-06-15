from sqlalchemy.orm import Session

from mock_services.itsm_a.database import Base, engine
from mock_services.itsm_a.models import Incident


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def reset_db(db: Session) -> dict[str, str]:
    db.query(Incident).delete()
    db.commit()
    return {"status": "reset", "service": "itsm_a"}
