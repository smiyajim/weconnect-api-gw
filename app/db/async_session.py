# app/db/async_session.py

print("🔥 async_session.py imported")

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# RAG 専用 DB URL を使用（推奨）
DATABASE_URL = os.environ["RAG_DATABASE_URL"]  # ← ★変更点

print("ASYNC DATABASE URL =", DATABASE_URL)

async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)