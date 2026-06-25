import uuid
from app.vectorstore import add_documents
from app.config import settings
from app.utils import simple_text_splitter

def ingest_text(text: str, metadata: dict | None = None) -> int:
    chunks = simple_text_splitter(
        text, 
        chunk_size=settings.CHUNK_SIZE, 
        overlap=settings.CHUNK_OVERLAP
    )
    print("DEBUG chunks type:", type(chunks))
    print("DEBUG number of chunks:", len(chunks) if chunks else 0)

    if chunks:
        print("DEBUG first chunk:", repr(chunks[0])[:200])
        print("DEBUG first chunk type:", type(chunks[0]))
    docs = []
    for i, c in enumerate(chunks):
        docs.append({
            "id": str(uuid.uuid4()),
            "text": c,
            "metadata": metadata or {}
        })
    add_documents(docs)
    return len(docs)
