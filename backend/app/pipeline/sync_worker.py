"""
Bi-directional sync worker.
Polls ITSM-A and ITSM-B every 15 seconds and keeps tickets in sync.
If a ticket is updated in ITSM-A, the change is reflected in ITSM-B and vice versa.
"""
import time
import logging
import requests
from backend.app.config import settings

logger = logging.getLogger(__name__)

POLL_INTERVAL = 15  # seconds
ITSM_A_URL = settings.ITSM_A_BASE_URL
ITSM_B_URL = settings.ITSM_B_BASE_URL

# In-memory state to track last known values
# key: itsm_a_number, value: dict of last known fields
_last_known: dict = {}


def _get_itsm_a_incidents() -> list[dict]:
    try:
        resp = requests.get(
            f'{ITSM_A_URL}/api/now/table/incident',
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get('result', [])
    except Exception as e:
        logger.warning(f'sync_worker: failed to fetch ITSM-A incidents: {e}')
        return []


def _get_itsm_b_issues() -> list[dict]:
    try:
        resp = requests.post(
            f'{ITSM_B_URL}/rest/api/2/search',
            json={'jql': ''},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get('issues', [])
    except Exception as e:
        logger.warning(f'sync_worker: failed to fetch ITSM-B issues: {e}')
        return []


def _update_itsm_b(issue_key: str, fields: dict) -> None:
    try:
        requests.put(
            f'{ITSM_B_URL}/rest/api/2/issue/{issue_key}',
            json={'fields': fields},
            timeout=10,
        ).raise_for_status()
        logger.info(f'sync_worker: updated ITSM-B {issue_key} with {fields}')
    except Exception as e:
        logger.warning(f'sync_worker: failed to update ITSM-B {issue_key}: {e}')


def _update_itsm_a(sys_id: str, fields: dict) -> None:
    try:
        requests.patch(
            f'{ITSM_A_URL}/api/now/table/incident/{sys_id}',
            json=fields,
            timeout=10,
        ).raise_for_status()
        logger.info(f'sync_worker: updated ITSM-A {sys_id} with {fields}')
    except Exception as e:
        logger.warning(f'sync_worker: failed to update ITSM-A {sys_id}: {e}')


def _sync_once() -> None:
    from backend.app.db import SessionLocal
    from backend.app.models.ticket_link import TicketLink

    incidents = _get_itsm_a_incidents()
    issues = _get_itsm_b_issues()

    # Build lookup of ITSM-B issues by key (real identifier, not position)
    issues_by_key = {issue.get('key'): issue for issue in issues if issue.get('key')}

    db = SessionLocal()
    try:
        for incident in incidents:
            number = incident.get('number')
            state = incident.get('state')
            urgency = incident.get('urgency')
            sys_id = incident.get('sys_id')

            # Look up the real ITSM-B key for this incident via ticket_links
            link = db.query(TicketLink).filter(TicketLink.itsm_a_id == sys_id).first()
            if not link or not link.itsm_b_key:
                continue

            issue = issues_by_key.get(link.itsm_b_key)
            if not issue:
                continue

            last = _last_known.get(number, {})

            # Detect change in ITSM-A state -> push to ITSM-B
            if last.get('state') != state:
                itsm_b_status = 'Closed' if state == 'resolved' else 'In Progress' if state == 'in_progress' else 'Open'
                _update_itsm_b(issue['key'], {'status': itsm_b_status})

            # Detect change in ITSM-B status -> push to ITSM-A
            b_status = issue.get('status')
            if last.get('b_status') != b_status and b_status == 'Closed' and state != 'resolved':
                _update_itsm_a(sys_id, {'state': 'resolved'})

            _last_known[number] = {
                'state': state,
                'urgency': urgency,
                'b_status': b_status,
            }
    finally:
        db.close()


def run_sync_worker() -> None:
    logger.info('sync_worker: starting bi-directional sync (15s interval)')
    print('Sync worker started — polling every 15 seconds...')
    while True:
        try:
            _sync_once()
        except Exception as e:
            logger.error(f'sync_worker: unexpected error: {e}')
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_sync_worker()
