import sys
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.pipeline.stage1_ingest import process_email
from backend.app.pipeline.stage2_intent import run_intent_classification
from backend.app.pipeline.stage3_extract import run_extraction
from backend.app.pipeline.stage4_classify import run_classification
from backend.app.pipeline.stage5_dedup import run_dedup
from backend.app.pipeline.stage6_enrich import run_enrichment
from backend.app.pipeline.stage7_ticket import run_ticket_creation, append_duplicate_comment
from backend.app.pipeline.stage8_route import run_routing


def run_full_pipeline(file_path: str):
    print(f"\nProcessing: {file_path}")

    # Stage 1
    email_record = process_email(file_path)
    raw_email_id = email_record.id
    print(f"Stage 1 done — Email ID: {raw_email_id}")

    # Stage 2
    intent = run_intent_classification(raw_email_id)
    print(f"Stage 2 done — Actionable: {intent['is_actionable']}")

    if not intent["is_actionable"]:
        run_routing(raw_email_id, is_actionable=False, dedup_status="NONE", intent_reasoning=intent["reasoning"])
        print("Not actionable — routed to no_action")
        return

    # Stage 3
    extraction = run_extraction(raw_email_id)
    print(f"Stage 3 done — App: {extraction['impacted_application']}")

    # Stage 4
    classification = run_classification(raw_email_id, extraction)
    print(f"Stage 4 done — Category: {classification['category']}")

    # Stage 5
    dedup = run_dedup(raw_email_id, extraction)
    print(f"Stage 5 done — Dedup: {dedup['ai_duplicate_check_status']}")

    # Stage 6
    enrichment = run_enrichment(raw_email_id, extraction)
    print(f"Stage 6 done — Caller resolved: {not enrichment['caller_unresolved']}")

    # Stage 7
    if dedup["ai_duplicate_check_status"] != "LINKED-TO-EXISTING":
        tickets = run_ticket_creation(raw_email_id, extraction, classification, enrichment, dedup)
        print(f"Stage 7 done — ITSM-A: {tickets['itsm_a_number']} ITSM-B: {tickets['itsm_b_key']}")
    else:
        comment_result = append_duplicate_comment(raw_email_id, dedup)
        print(f"Stage 7 done - comment appended to existing ticket {comment_result['matched_ticket_id']}")

    # Stage 8
    route = run_routing(raw_email_id, is_actionable=True, dedup_status=dedup["ai_duplicate_check_status"])
    print(f"Stage 8 done — Routed to: {route['destination']}")


class MailboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".eml"):
            print(f"\nNEW EMAIL DETECTED: {event.src_path}")
            try:
                run_full_pipeline(event.src_path)
            except Exception as e:
                print(f"Pipeline error: {e}")


INBOXES = [
    "mailboxes/inbox_1/new",
    "mailboxes/inbox_2/new",
    "mailboxes/inbox_3/new",
    "mailboxes/inbox_4/new",
]

observer = PollingObserver()
for inbox in INBOXES:
    observer.schedule(MailboxHandler(), path=inbox, recursive=False)

observer.start()
print("Watching all 4 inboxes for new emails...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
