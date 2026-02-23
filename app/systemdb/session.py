# app/systemdb/session.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

SYSTEM_DATABASE_URL = os.environ["SYSTEM_DATABASE_URL"]

system_async_engine = create_async_engine(
    SYSTEM_DATABASE_URL,
    future=True,
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=system_async_engine,
    expire_on_commit=False,
)