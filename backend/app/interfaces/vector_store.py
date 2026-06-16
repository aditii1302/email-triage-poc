from typing import Protocol
from dataclasses import dataclass


@dataclass
class VectorMatch:
    ticket_id: str
    similarity: float
    metadata: dict


class VectorStore(Protocol):
    def upsert(self, doc_id: str, text: str, metadata: dict) -> None: ...
    def query(self, text: str, n_results: int) -> list[VectorMatch]: ...
