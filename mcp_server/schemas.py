# mcp_server/schemas.py

def rag_search_schema():
    return {
        "name": "rag_search",
        "description": "社内ドキュメントを検索します。特定のカテゴリ（規程、マニュアル等）で絞り込む場合はmetadataを指定してください。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string", 
                    "description": "検索クエリ"
                },
                "top_k": {
                    "type": "integer", 
                    "default": 5
                },
                "metadata": {
                    "type": "object",
                    "description": "フィルタリング条件 (例: {'category': '就業規則'})",
                    "additionalProperties": True
                }
            },
            "required": ["query"]
        }
    }