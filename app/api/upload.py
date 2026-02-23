# app/api/upload.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.tenant.resolver import resolve_tenant
from app.ingest.pdf_loader import load_pdf_pages
from app.ingest.ingest_text import ingest_text

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    tenant_id: str = Depends(resolve_tenant),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF only")

    raw = await file.read()

    # PDF → [(page_no, text)]
    pages = load_pdf_pages(raw)

    if not pages:
        raise HTTPException(status_code=400, detail="No text found in PDF")

    # ページ単位で ingest
    for page_no, text in pages:
        await ingest_text(
            tenant_id=tenant_id,
            text=text,
            filename=file.filename, # 追加
            page_no=page_no,        # 追加
        )

    return {
        "status": "ok",
        "filename": file.filename,
        "pages": len(pages),
    }