# app/rag_clients/factory.py

from app.rag_clients.pgvector_rag import PgVectorRAG

def get_rag(tenant_id: str):
    return PgVectorRAG(tenant_id)