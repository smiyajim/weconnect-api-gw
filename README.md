### Sourceコード・ディレクトリ構成
データベース：PostgreSQL v17
動作環境：AlmaLinux 9.x
ソース管理：uv
プログラム言語：Python

全体ディレクトリ構成：
api-gateway/
├─ pyproject.toml
├─ .venv
├─ .gitignore
├─ .python-version
├─ README.md
├─ uv.lock
│
├─ app/                      # BE (FastAPI)
│   ├─ __init__.py		    ← 空き
│   ├─ main.py
│   ├─ agent/
│   │   ├─deps.py
│   │   ├─ simple_agent.py
│   │   └─ tool_executor.py
│   ├─ api/
│   │   ├─ chat.py
│   │   ├─ dependencies.py
│   │   └─ upload.py
│   ├─ db/
│   │   ├─ __init__.py		← 空き
│   │   ├─ async_session.py
│   │   ├─ rag_async_session.py
│   │   └─ system_async_session.py
│   ├─ embeddings/
│   │   ├─ __init__.py
│   │   └─ client.py
│   ├─ ingest/
│   │   ├─ __init__.py		← 空き
│   │   ├─ chunker.py
│   │   ├─ ingest_checker.py
│   │   ├─ ingest_text.py
│   │   ├─ normalize.py
│   │   ├─ pdf_loader.py
│   │   ├─ repository.py
│   │   └─ text_normalizer.py
│   ├─ llm/
│   │   ├─ base.py
│   │   ├─ gemini_client.py
│   │   ├─ openai_client.py
│   │   └─ types.py
│   ├─ logging/
│   │   └─ access_log.py
│   ├─ mcp/			← MCPクライアント機能
│   │   └─ client.py
│   ├─ rag_clients/              	# RAG接続（将来別サーバ）
│   │   ├─ base.py
│   │   ├─ dummy.py
│   │   ├─ external_rag.py
│   │   ├─ factory.py
│   │   └─ pgvector_rag.py
│   ├─ systemdb/
│   │   ├─ base.py
│   │   ├─ models.py
│   │   └─ session.py
│   └─ tenant/
│       └─ resolver.py
│
├─ db/                          # DBスキーマー（保守用）
│   ├─ logdb_schema.sql
│   ├─ logdb_seed.sql
│   ├─ ragdb_schema.sql
│   ├─ ragdb_seed.sql
│   ├─ systemdb_schema.sql
│   └─ systemdb_seed.sq
│
└─ mcp_server/               	←  MCP Server（別プロセス／機能毎にカプセル化《RAG／LOG》）
     ├─ registry.py
     ├─ schemas.py
     └─ server.py

### Firewall / Security Group
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --add-port=9000/tcp --permanent
sudo firewall-cmd --reload

sudo firewall-cmd --list-ports

### プロセス起動
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
uv run uvicorn mcp_server.server:app --host 0.0.0.0 --port 9000 --reload

        ※ 本番では「--reload」を抜く

### curlコマンド(ローカル試験用)

    ### PDF Upload（RAG-DB書き込み試験）
    curl -X POST http://weconnect.srv.wegrow:8000/upload/pdf \
    -H "X-User-Id: demo-user" \
    -H "X-Tenant-Id: default" \
    -H "X-Internal-Gateway-Token: ＜環境変数登録したInternal-Gateway-Token＞" \
    -F "file=@社員就業規則.pdf" | jq

    ### Query（チャット試験）
    curl -X POST http://weconnect.srv.wegrow:8000/chat \
    -H "Authorization: Bearer demo-user-token" \
    -H "X-User-Id: demo-user" \
    -H "X-Tenant-Id: default" \
    -H "X-Internal-Gateway-Token: ＜環境変数登録したInternal-Gateway-Token＞" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "社内規定から試用期間を検索して"}' | jq

### DB 未作成の場合の事前作業
	user ~ $ su - 
	パスワード： xxxxxxx
	root ~ # su - postgres
	postgres ~ $ createdb systemdb -O noah
	postgres ~ $ createdb ragdb -O noah
	postgres ~ $ createdb logdb -O noah
	postgres ~ $ exit
	root ~ # exit
	user ~ $ cd ＜編集対象repoのディレクトリ＞ 
	user ~ # psql -U noah systemdb < db/systemdb_schema.sql
	user ~ # psql -U noah systemdb < db/systemdb_seed.sql
	user ~ # psql -U noah ragdb < db/schema.sql
	user ~ # psql -U noah ragdb < db/seed.sql
	user ~ # psql -U noah logdb < db/logdb_schema.sql
	user ~ # psql -U noah logdb < db/logdb_seed.sql

### SYSTEM DB 再作成
    # 1. DBを再作成
    psql -U noah -d systemdb
        \c postgres
        DROP DATABASE systemdb;
        CREATE DATABASE systemdb;

    # 2. 構造を流す
    psql -U noah systemdb < db/system_schema.sql

    # 3. 初期データを流す
    psql -U noah systemdb < db/system_seed.sql

### RAG DB 再作成
    # 1. DBを再作成
    psql -U noah -d ragdb
        \c postgres
        DROP DATABASE ragdb;
        CREATE DATABASE ragdb;

    # 2. 構造を流す
    psql -U noah ragdb < db/schema.sql

    # 3. 初期データを流す
    psql -U noah ragdb < db/seed.sql

### LOG DB 再作成
    # 1. DBを再作成
    psql -U noah -d logdb
        \c postgres
        DROP DATABASE logdb;
        CREATE DATABASE logdb;

    # 2. 構造を流す
    psql -U noah logdb < db/system_schema.sql

    # 3. 初期データを流す
    psql -U noah logdb < db/system_seed.sql

### 設計上の考慮すべきポイント
    ⚠️ ① MCP protocol versioning

        現コードにおける「MCP protocolバージョン」
            ⇨　"protocol_version": "0.1.0-beta.1"　とする
        Phase 1作業におけるバージョン管理
            ⇨　"protocol_version": "0.1.1-phase1.1" からステップ完了単位で末番を更新
        Phase 2作業におけるバージョン管理
            ⇨　"protocol_version": "0.2.1-phase2.1" からステップ完了単位で末番を更新
        Phase 3作業におけるバージョン管理
            ⇨　"protocol_version": "0.3.1-phase3.1" からステップ完了単位で末番を更新

        AWS上構築完了版
            ⇨　"protocol_version": "1.0.0-aws.1"　とするし、検証プロセスの各段階で末番を更新
        プロダクト総合試験段階
            ⇨　"protocol_version": "1.1.0-rc.1"　とし、ファイル更新毎に末番を更新
        プロダクトリリース
            ⇨　"protocol_version": "1.1.1"　とする

        バージョン管理
            MAJOR: MCP破壊的変更
            MINOR: tool追加・仕様拡張
            PATCH: 非互換なしの修正
            -xxx: 検証段階識別子

    ⚠️ ② tool schema の「互換性ルール」
        protocol_version更新契機は下記編集実施時とする
            引数追加
            引数名変更
            tool廃止
        設計ルール
            破壊的変更は protocol_version を上げる
            引数追加は後方互換
            tool削除は段階的 deprecate
            既存引数の意味変更は「破壊的変更」とみなす

    ⚠️ ③ tool実行ログの「責務境界」
        設計指針
            tool成功 / timeout / errorログはAI-Gatewayが記録する
            MCP Server は一切ログを持たないこととする
        将来実装検討項目
            MCP Server：stateless
            AI Gateway：audit / billing / incident 対象

    ⚠️ ④ External RAG の責務境界（将来）
        ExternalRAG は：
            認証
            SLA
            レート制限
            再試行
        を必須機能とし、VPN使用も最終的に検討する

        設計指針
            - ExternalRAG は「tool実装」ではない
            - RAG Client の一種であり、tool executor からは透過
            - ExternalRAGの構築は我々から設計マニュアルを提供しカスタマの責任において行うが、
            カスタマの要望によっては構築作業の技術支援を行うこともある
            - ExternalRAG の可用性・性能・セキュリティは 顧客責任を原則とし、
            我々は 接続仕様とリファレンス実装のみを保証する

## 運用上の注意（重要）
    以下の変更を行った場合は、必ず uvicorn を再起動すること。

    - .env / 環境変数の変更
    - DB 接続設定の変更
    - ingest / chunker / embedding 周りのコード変更

    再起動しない場合、古い設定のまま処理が行われ、
    異なる DB や設定に接続される可能性がある。

# FastAPI 再起動
    pkill -f uvicorn

## 推奨対策（補助）
    - 起動時ヘルスチェックによる DB / embedding 設定検証
    - 起動ログに接続先 DB・モデル名を出力

### 環境変数（API-GWサーバー）
    RAG_DATABASE_URL=postgresql+asyncpg://noah:noahpee@localhost:5432/ragdb
    SYSTEM_DATABASE_URL=postgresql+asyncpg://noah:noahpee@localhost:5432/systemdb
    OPENAI_API_KEY=《OpenAI APIキー情報》
    OPENAI_MODEL=gpt-4.1-mini
    LLM_PROVIDER=openai
    OPENAI_EMBEDDING_MODEL=text-embedding-3-small
    MCP_SERVER_URL=http://localhost:9000
    OLDPWD=/home/smiyajim/python-pj/uv-pj/ai-gateway-step4
    INTERNAL_GATEWAY_TOKEN=《Internal-Gateway-Token情報》

