import re
import requests
from backend.app.interfaces.directory import UserRecord


class MockDirectoryClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def lookup_by_email(self, email: str) -> UserRecord | None:
        email = email.strip()
        match = re.search(r'[\w\.\-\+]+@[\w\.\-]+', email)
        if match:
            email = match.group()
        try:
            resp = requests.get(
                f'{self.base_url}/users',
                params={'email': email},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                return UserRecord(
                    upn=data.get('upn', email),
                    display_name=data.get('display_name', email),
                    department=data.get('department'),
                    manager=data.get('manager'),
                    location=data.get('location'),
                )
        except Exception:
            pass
        return None
