# app/db/system_async_session.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

SYSTEM_DATABASE_URL = os.environ["SYSTEM_DATABASE_URL"]

system_async_engine = create_async_engine(
    SYSTEM_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

SystemAsyncSessionLocal = async_sessionmaker(
    bind=system_async_engine,
    expire_on_commit=False,
)