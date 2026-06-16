import pytest
from unittest.mock import MagicMock, patch


def test_chroma_store_upsert():
    with patch('backend.app.adapters.chroma_store.chromadb') as mock_chroma,          patch('backend.app.adapters.chroma_store.SentenceTransformer') as mock_st:
        mock_st.return_value.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        mock_collection = MagicMock()
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        from backend.app.adapters.chroma_store import ChromaVectorStore
        store = ChromaVectorStore()
        store.upsert('INC001', 'user cannot login to HR Portal', {'application': 'HR Portal'})
        mock_collection.upsert.assert_called_once()


def test_chroma_store_query_returns_matches():
    with patch('backend.app.adapters.chroma_store.chromadb') as mock_chroma,          patch('backend.app.adapters.chroma_store.SentenceTransformer') as mock_st:
        mock_st.return_value.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'distances': [[0.1, 0.3]],
            'metadatas': [
                [{'ticket_id': 'INC001', 'application': 'HR Portal'},
                 {'ticket_id': 'INC002', 'application': 'VPN Client'}]
            ]
        }
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        from backend.app.adapters.chroma_store import ChromaVectorStore
        store = ChromaVectorStore()
        results = store.query('cannot login', n_results=2)
        assert len(results) == 2
        assert results[0].ticket_id == 'INC001'
        assert results[0].similarity == round(1 - 0.1, 4)


def test_chroma_store_query_empty_results():
    with patch('backend.app.adapters.chroma_store.chromadb') as mock_chroma,          patch('backend.app.adapters.chroma_store.SentenceTransformer') as mock_st:
        mock_st.return_value.encode.return_value.tolist.return_value = [0.1]
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'distances': [[]], 'metadatas': [[]]}
        mock_chroma.PersistentClient.return_value.get_or_create_collection.return_value = mock_collection

        from backend.app.adapters.chroma_store import ChromaVectorStore
        store = ChromaVectorStore()
        results = store.query('nothing here', n_results=5)
        assert results == []
