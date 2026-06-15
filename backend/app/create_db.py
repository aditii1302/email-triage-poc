import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db import engine
from backend.app.models.base import Base
from backend.app.models.pipeline_run import PipelineRun
from backend.app.models.raw_email import RawEmail

Base.metadata.create_all(bind=engine)

print("Database created successfully")
