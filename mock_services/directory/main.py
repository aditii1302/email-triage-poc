import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from mock_services.directory.database import get_db
from mock_services.directory.models import DirectoryUser
from mock_services.directory.schemas import UserResponse
from mock_services.directory.seed import ensure_seeded, init_db, reset_db


app = FastAPI(title="Directory Mock Service", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = next(get_db())
    try:
        ensure_seeded(db)
    finally:
        db.close()


@app.get("/users", response_model=UserResponse)
def get_user(email: str = Query(...), db: Session = Depends(get_db)):
    user = (
        db.query(DirectoryUser)
        .filter(DirectoryUser.email == email.lower())
        .first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/admin/reset")
def reset(db: Session = Depends(get_db)):
    return reset_db(db)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)
