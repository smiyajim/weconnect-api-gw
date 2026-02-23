# app/ingest/ingest_checker.py

import asyncio
from app.ingest.ingest_text import ingest_text

text = """
試用期間は入社後3ヶ月間とする。
この期間中、会社は適性を判断する。
"""

async def main():
    await ingest_text(
        tenant_id="default",
        text=text,
        source="checker_test",
        filename="checker.txt",
    )
    print("✅ ingest_text が正常に完走しました")


if __name__ == "__main__":
    asyncio.run(main())