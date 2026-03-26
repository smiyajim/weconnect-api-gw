# app/agent/tool_executor.py

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from app.tenant.resolver import resolve_rag_client

logger = logging.getLogger(__name__)

TOOL_TIMEOUT_SECONDS = 60  # 開発は長めに、本番は短めに（本番では10秒程度が望ましいが、開発中は色々試すため長めに設定）
# TOOL_TIMEOUT_SECONDS = 10  # 本番必須


def _env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip() in ("1", "true", "True", "yes", "on", "ON")


def _pick_filter_metadata(args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    呼び出し側の揺れ吸収:
      - schemas.py は 'metadata'
      - 以前の実装/議論で 'filter_meta' などが混ざる可能性
    """
    v = args.get("metadata")
    if v is None:
        v = args.get("filter_meta")
    if v is None:
        v = args.get("filter_metadata")
    if v is None:
        return None
    return v if isinstance(v, dict) else None


def _pick_top_k(args: Dict[str, Any], default: int = 5) -> int:
    try:
        return int(args.get("top_k", default))
    except Exception:
        return default


async def execute_tool(tool_call: dict, tenant_id: str | None):
    """
    外側：タイムアウト＆例外ハンドリング + 返却フォーマット統一
    """
    try:
        return await asyncio.wait_for(
            _execute_tool_impl(tool_call, tenant_id),
            timeout=TOOL_TIMEOUT_SECONDS,
        )

    except asyncio.TimeoutError:
        logger.error("Tool timeout: %s", tool_call)
        return {
            "tool_name": tool_call.get("name", "unknown"),
            "error": "TOOL_TIMEOUT",
            "result": [],
        }

    except Exception as e:
        logger.exception("Tool execution error")
        return {
            "tool_name": tool_call.get("name", "unknown"),
            "error": "TOOL_ERROR",
            "message": str(e),
            "result": [],
        }


async def _execute_tool_impl(tool_call: dict, tenant_id: str | None):
    tool_name = tool_call.get("name")
    args = tool_call.get("arguments", {}) or {}

    # -----------------------------
    # rag_search
    # -----------------------------
    if tool_name == "rag_search":
        if not tenant_id:
            raise ValueError("tenant_id is required for rag_search")

        rag = await resolve_rag_client(tenant_id)

        query = args.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("rag_search requires non-empty 'query' (string)")

        top_k = _pick_top_k(args, default=5)
        filter_metadata = _pick_filter_metadata(args)

        # 評価モード切り替え（arguments 優先、なければ env）
        # arguments: eval_all_models, persist_to_evaldb, primary_model_key
        eval_all_models = args.get("eval_all_models")
        if eval_all_models is None:
            eval_all_models = _env_flag("EVAL_ALL_MODELS", "0")
        else:
            eval_all_models = bool(eval_all_models)

        persist_to_evaldb = args.get("persist_to_evaldb")
        if persist_to_evaldb is None:
            persist_to_evaldb = _env_flag("EVAL_PERSIST_DB", "0")
        else:
            persist_to_evaldb = bool(persist_to_evaldb)

        primary_model_key = args.get("primary_model_key")
        if not isinstance(primary_model_key, str) or not primary_model_key:
            primary_model_key = os.getenv("EVAL_PRIMARY_MODEL", "openai")

        # ---- 評価モード（4モデル検索 + 任意でevalDB保存）----
        if eval_all_models:
            results_by_model = await rag.search_eval_all_models(
                query=query,
                top_k=top_k,
                filter_metadata=filter_metadata,
                persist_to_evaldb=persist_to_evaldb,
            )

            # LLM に返すのは “従来互換” の list だけ（基本 primary を返す）
            primary = results_by_model.get(primary_model_key)
            if primary is None:
                # 念のためフォールバック
                primary = next(iter(results_by_model.values()), [])

            return {
                "tool_name": tool_name,
                "result": primary,
                # 返しても壊れない程度の補助情報（不要なら後で消してOK）
                "eval": {
                    "enabled": True,
                    "persisted": bool(persist_to_evaldb),
                    "primary_model_key": primary_model_key,
                    "models": list(results_by_model.keys()),
                },
            }

        # ---- 通常モード（単一モデル検索）----
        model_key = args.get("model_key", "openai")
        result = await rag.search(
            query=query,
            top_k=top_k,
            filter_metadata=filter_metadata,
            model_key=model_key,
        )
        return {
            "tool_name": tool_name,
            "result": result,
        }

    # -----------------------------
    # unknown tool
    # -----------------------------
    logger.warning("Unknown tool: %s args=%s", tool_name, args)
    return {
        "tool_name": tool_name or "unknown",
        "error": "UNKNOWN_TOOL",
        "result": [],
    }