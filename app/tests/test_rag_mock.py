import unittest
from unittest.mock import MagicMock, patch
import os
import shutil

# Set env vars before importing config
os.environ["INDEX_DIR"] = "./test_storage/index"
os.environ["UPLOAD_DIR"] = "./test_storage/uploads"

from app.rag import ingest_pdf, retrieve, initialize_rag, get_vector_store

class TestRag(unittest.TestCase):
    def setUp(self):
        # Clean up test directories
        if os.path.exists("./test_storage"):
            shutil.rmtree("./test_storage")
        os.makedirs("./test_storage/index")
        os.makedirs("./test_storage/uploads")

    def tearDown(self):
         if os.path.exists("./test_storage"):
            shutil.rmtree("./test_storage")

    @patch('app.rag.PyPDFLoader')
    @patch('app.rag.HuggingFaceEmbeddings')
    @patch('app.rag.FAISS')
    def test_ingest_and_retrieve_flow(self, mock_faiss, mock_embeddings, mock_loader):
        # Mock Loader
        mock_doc = MagicMock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test.pdf", "page": 1}
        mock_loader_instance = mock_loader.return_value
        mock_loader_instance.load.return_value = [mock_doc]

        # Mock Embeddings
        mock_embeddings_instance = mock_embeddings.return_value

        # Mock FAISS
        mock_vs = MagicMock()
        mock_faiss.from_documents.return_value = mock_vs
        mock_faiss.load_local.return_value = mock_vs

        # Test Initialize
        initialize_rag()

        # Test Ingest
        n_chunks = ingest_pdf("dummy_path.pdf")
        self.assertTrue(n_chunks > 0)
        mock_loader.assert_called()

        # Depending on if vector store was None or not (it is reset by global state potentially,
        # but in this test process it shares memory).
        # Since initialize_rag was called, embeddings are loaded.
        # But vector_store is loaded from disk. Disk is empty in setup.
        # So ingest_pdf calls FAISS.from_documents.
        mock_faiss.from_documents.assert_called()
        mock_vs.save_local.assert_called()

        # Test Retrieve
        # Retrieve uses get_vector_store which returns the global _vector_store
        # which is now populated.
        mock_doc_result = MagicMock()
        mock_doc_result.page_content = "Result content"
        mock_doc_result.metadata = {"source": "test.pdf", "page": 1}
        mock_vs.similarity_search_with_score.return_value = [(mock_doc_result, 0.9)]

        results = retrieve("query")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "Result content")

if __name__ == '__main__':
    unittest.main()
