from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Model loaded")

embeddings = model.encode(
    ["hello world", "machine learning"],
    convert_to_numpy=True
)

print(embeddings.shape)