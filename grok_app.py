import base64
import io
import re
import os
import pickle
import faiss
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# Load everything
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index("vector.index")

# Google Drive File ID
file_id = "1_0FlXBndnudiMCRCIkCsJVm0jEIYRE2M"
url = f"https://drive.google.com/uc?id={file_id}"
filename = "chunk_metadata.pkl"

# Download if not present
if not os.path.exists(filename):
    print("Downloading chunk_metadata.pkl from Google Drive...")
    gdown.download(url, filename, quiet=False)

# Load the .pkl file
with open(filename, "rb") as f:
    metadata = pickle.load(f)

# FastAPI setup
app = FastAPI()

# Request & Response models
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 image

class QueryResponse(BaseModel):
    answer: str
    links: List[dict]

# OCR function
def extract_text_from_image(base64_string: str) -> str:
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return ""

# Chunk search
def search_similar_chunks(query, top_k=5):
    query_embedding = model.encode([query])[0].astype("float32")
    distances, indices = index.search(np.array([query_embedding]), top_k)
    return [metadata[i] for i in indices[0]]

# Snippet extractor
def extract_relevant_snippet(chunk_text, question):
    sentences = re.split(r'(?<=[.?!])\s+', chunk_text)
    question_keywords = set(re.findall(r'\w+', question.lower()))
    scored = [
        (sentence, len(question_keywords & set(re.findall(r'\w+', sentence.lower()))))
        for sentence in sentences
    ]
    return max(scored, key=lambda x: x[1])[0] if scored else sentences[0]

# Groq LLM client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY") or "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"
)

# Answer generation
def generate_answer(question, context_chunks):
    context_text = "\n\n".join(chunk["text"] for chunk in context_chunks)
    urls = [
        {"url": chunk.get("url", "#"), "text": extract_relevant_snippet(chunk["text"], question)}
        for chunk in context_chunks if "url" in chunk
    ]

    system_prompt = "You are a helpful teaching assistant for an online data science course. Answer concisely using the course material."

    user_prompt = f"""Answer the following question using the context below. Do not make up answers. If the answer is not present, say so.

Question: {question}

Context:
{context_text}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=512
    )

    answer = response.choices[0].message.content.strip()
    return answer, urls

# API Endpoint
@app.post("/api/", response_model=QueryResponse)
def answer_query(request: QueryRequest):
    full_question = request.question

    if request.image:
        extracted_text = extract_text_from_image(request.image)
        if extracted_text:
            full_question += "\n\n" + extracted_text

    chunks = search_similar_chunks(full_question)
    answer, links = generate_answer(full_question, chunks)
    return {"answer": answer, "links": links}
