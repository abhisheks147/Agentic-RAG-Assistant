from fastapi import APIRouter, UploadFile, File, Form, Header
from app.ingestion import ingest_text
from app.agent_pipeline import agent_pipeline
from app.utils import extract_text_from_file

router = APIRouter()

@router.post("/chat")
async def chat(query: str = Form(...), x_gemini_api_key: str | None = Header(None)):
    result = agent_pipeline(query, api_key=x_gemini_api_key)
    return result

@router.post("/upload")
async def upload(file: UploadFile = File(...), source: str | None = Form(None)):
    content = await file.read()
    text = extract_text_from_file(content, file.filename)
    metadata = {"filename": file.filename, "source": source or "user_upload"}
    count = ingest_text(text, metadata=metadata)
    return {"chunks_indexed": count}
