# app/main.py

from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router

app = FastAPI(title="AI Gateway")

app.include_router(chat_router)
app.include_router(upload_router)