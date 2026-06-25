from sentence_transformers import SentenceTransformer
from app.config import settings

_model = SentenceTransformer(settings.EMBEDDING_MODEL)

def embed_texts(texts: list[str]) -> list[list[float]]:
    print("DEBUG RAW INPUT TYPE:", type(texts))

    try:
        # HARD FIX: enforce pure strings only
        cleaned = []
        for i, t in enumerate(texts):
            if isinstance(t, str):
                cleaned.append(t)
            else:
                print(f"❌ BAD TYPE at index {i}: {type(t)} -> {t}")
                cleaned.append(str(t))  # force convert

        print("DEBUG FINAL CLEANED COUNT:", len(cleaned))

        return _model.encode(
            cleaned,
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()

    except Exception as e:
        print(f"DEBUG: _model.encode failed! Error: {type(e)}: {e}")
        raise