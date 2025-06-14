import pickle
import numpy as np
import faiss
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Load parsed chunks
with open("parsed_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

texts = [chunk["text"] for chunk in chunks]

# Load local embedding model (you can try different ones like 'all-MiniLM-L6-v2')
model = SentenceTransformer('all-MiniLM-L6-v2')

# Batch embedding function using SentenceTransformers
def embed_in_batches(texts, batch_size=100):
    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size)):
        batch = texts[i:i+batch_size]
        batch_embeddings = model.encode(batch, show_progress_bar=False, convert_to_numpy=True)
        all_embeddings.extend(batch_embeddings)
    return all_embeddings

# Generate embeddings
embeddings = embed_in_batches(texts)

# Build FAISS index
dim = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings).astype("float32"))

# Save FAISS index
faiss.write_index(index, "vector.index")

# Save metadata
for chunk in chunks:
    chunk["embedding"] = None  # Strip to save space

with open("chunk_metadata.pkl", "wb") as f:
    pickle.dump(chunks, f)

print(f"Vector store built with {len(embeddings)} chunks using Hugging Face.")
