import chromadb
import re
from app.config import settings
from app.embeddings import embed_texts

try:
    if settings.CHROMA_HOST and settings.CHROMA_HOST != "chroma":
        chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        chroma_client.heartbeat()
    else:
        # Local persistent storage
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
except Exception:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")


COLLECTION_NAME = "agentic_collection"


def get_collection():
    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def clean_text(t: str) -> str:
    if not isinstance(t, str):
        t = str(t)

    # Remove invalid UTF-8 / surrogate pairs
    t = t.encode("utf-8", "ignore").decode("utf-8")

    # Extra safety cleanup for broken unicode ranges
    t = re.sub(r"[\uD800-\uDFFF]", "", t)

    return t


def add_documents(docs: list[dict]):
    col = get_collection()

    ids = [d["id"] for d in docs]

    # ✅ CLEAN TEXT BEFORE SENDING TO CHROMA
    texts = [clean_text(d["text"]) for d in docs]

    metadatas = [d.get("metadata", {}) for d in docs]

    embeddings = embed_texts(texts)

    col.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=texts
    )


def retrieve(query: str, k: int = 5, filters: dict | None = None):
    col = get_collection()

    q_emb = embed_texts([query])[0]

    if filters:
        results = col.query(
            query_embeddings=[q_emb],
            n_results=k,
            where=filters
        )
    else:
        results = col.query(
            query_embeddings=[q_emb],
            n_results=k
        )

    docs = []

    if (
        results
        and "documents" in results
        and results["documents"]
        and results["documents"][0]
    ):
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            docs.append({
                "text": doc,
                "metadata": meta
            })

    return docs