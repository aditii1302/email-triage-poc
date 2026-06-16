import chromadb
from sentence_transformers import SentenceTransformer
from backend.app.interfaces.vector_store import VectorMatch


class ChromaVectorStore:
    def __init__(self, path: str = './chroma_db', collection: str = 'tickets'):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(collection)

    def upsert(self, doc_id: str, text: str, metadata: dict) -> None:
        embedding = self.model.encode(text).tolist()
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def query(self, text: str, n_results: int = 5) -> list[VectorMatch]:
        embedding = self.model.encode(text).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=['metadatas', 'distances'],
        )
        matches = []
        if results and results['distances'] and results['distances'][0]:
            for distance, metadata in zip(results['distances'][0], results['metadatas'][0]):
                matches.append(VectorMatch(
                    ticket_id=metadata.get('ticket_id', ''),
                    similarity=round(1 - distance, 4),
                    metadata=metadata,
                ))
        return matches
