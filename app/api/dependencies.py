# app/api/dependencies.py

import os
from fastapi import Header, HTTPException, status

# 必須：Reverse Proxy と AI-Gateway で共有する秘密
INTERNAL_GATEWAY_TOKEN = os.getenv("INTERNAL_GATEWAY_TOKEN")

if not INTERNAL_GATEWAY_TOKEN:
    raise RuntimeError(
        "INTERNAL_GATEWAY_TOKEN is not set. "
        "This server must be run behind a reverse proxy."
    )


def require_internal_auth(
    x_internal_gateway_token: str | None = Header(
        None,
        alias="X-Internal-Gateway-Token",
    ),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
):
    """
    Reverse Proxy 経由でのみ通過可能な内部認証ガード
    """

    # 🚫 直アクセス防止（最重要）
    if x_internal_gateway_token != INTERNAL_GATEWAY_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Direct access is not allowed",
        )

    # 👤 ユーザー・テナント情報必須
    if not x_user_id or not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing identity headers",
        )

    return {
        "user_id": x_user_id,
        "tenant_id": x_tenant_id,
    }