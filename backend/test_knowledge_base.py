from app.rag.qdrant_client import QdrantManager

manager = QdrantManager()
query_vector = [0.1] * 1536  # Mock vector for testing
results = manager.search("knowledge_base", query_vector, limit=5)
