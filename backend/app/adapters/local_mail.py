import os
import shutil
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
from backend.app.interfaces.mail_source import IncomingEmail


class LocalMailSource:
    def __init__(self, inboxes: list[str]):
        self.inboxes = inboxes
        self._queue: list[IncomingEmail] = []
        self._observer = PollingObserver()

        handler = _Handler(self._queue)
        for inbox in inboxes:
            Path(inbox).mkdir(parents=True, exist_ok=True)
            self._observer.schedule(handler, path=inbox, recursive=False)

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()

    def watch(self):
        while True:
            if self._queue:
                yield self._queue.pop(0)
            else:
                time.sleep(1)

    def mark_processed(self, email: IncomingEmail, destination: str) -> None:
        src = Path(email.file_path)
        dest_dir = src.parent.parent / destination
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest_dir / src.name))


class _Handler(FileSystemEventHandler):
    def __init__(self, queue: list):
        self._queue = queue

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.eml'):
            path = event.src_path
            mailbox = Path(path).parts[-3]
            try:
                with open(path, 'rb') as f:
                    raw = f.read()
                self._queue.append(IncomingEmail(
                    file_path=path,
                    mailbox=mailbox,
                    raw_bytes=raw,
                ))
            except Exception:
                pass
