# app/systemdb/models.py

from sqlalchemy import Column, String, DateTime, JSON   # model 用の型をインポート
from datetime import datetime                           # デフォルト値用にインポート
from sqlalchemy.sql import func
from app.systemdb.base import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True)

class AccessLog(Base):                                  # AccessLog モデルを追加(step-4)
    __tablename__ = "access_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=True)

    prompt = Column(String, nullable=False)

    tool_used = Column(String, nullable=True)      # rag_search etc
    tool_result = Column(JSON, nullable=True)      # raw tool result

    llm_response = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(JSON, nullable=True) 