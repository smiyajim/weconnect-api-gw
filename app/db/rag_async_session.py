# app/db/rag_async_session.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

RAG_DATABASE_URL = os.environ["RAG_DATABASE_URL"]

rag_async_engine = create_async_engine(
    RAG_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

RagAsyncSessionLocal = async_sessionmaker(
    bind=rag_async_engine,
    expire_on_commit=False,
)