from faker import Faker
from sqlalchemy.orm import Session

from mock_services.directory.database import Base, engine
from mock_services.directory.models import DirectoryUser


fake = Faker()
DEPARTMENTS = ["IT", "Finance", "HR", "Sales", "Operations", "Security"]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_users(db: Session, count: int = 25) -> None:
    fake.seed_instance(20260610)

    db.add(
        DirectoryUser(
            email="john@example.com",
            upn="john@example.com",
            display_name="John Example",
            department="IT",
            manager="David",
        )
    )

    seen = {"john@example.com"}
    while len(seen) < count:
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name}.{last_name}@example.com".lower()
        if email in seen:
            continue

        seen.add(email)
        db.add(
            DirectoryUser(
                email=email,
                upn=email,
                display_name=f"{first_name} {last_name}",
                department=fake.random_element(DEPARTMENTS),
                manager=fake.name(),
            )
        )

    db.commit()


def reset_db(db: Session) -> dict[str, int | str]:
    db.query(DirectoryUser).delete()
    db.commit()
    seed_users(db, count=25)
    return {"status": "reset", "service": "directory", "users": 25}


def ensure_seeded(db: Session) -> None:
    if db.query(DirectoryUser).count() == 0:
        seed_users(db, count=25)
