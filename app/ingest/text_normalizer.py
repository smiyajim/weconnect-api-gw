# app/ingest/text_normalizer.py

import re

def normalize_japanese_text(text: str) -> str:
    if not text:
        return ""

    # ① 全角空白 → 半角
    text = text.replace("\u3000", " ")

    # ② 改行＋タブ＋連続空白を1スペースに
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    # ③ 日本語文字間の不正スペースを除去
    #   例: "試 用 期 間" → "試用期間"
    text = re.sub(
        r"(?<=[ぁ-んァ-ン一-龥])\s+(?=[ぁ-んァ-ン一-龥])",
        "",
        text,
    )

    # ④ 数字＋単位の分断修正
    #   "３ か 月" → "３か月"
    text = re.sub(
        r"(?<=[0-9０-９])\s+(?=[ぁ-んァ-ン一-龥])",
        "",
        text,
    )

    # ⑤ 記号前後の不要スペース除去
    text = re.sub(r"\s*([、。・（）()])\s*", r"\1", text)

    return text.strip()