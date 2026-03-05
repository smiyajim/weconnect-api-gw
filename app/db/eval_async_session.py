# app/db/eval_async_session.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

EVAL_DATABASE_URL = os.environ["EVAL_DATABASE_URL"]

eval_async_engine = create_async_engine(
    EVAL_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)


EvalAsyncSessionLocal = async_sessionmaker(
    bind=eval_async_engine,
    expire_on_commit=False,
)