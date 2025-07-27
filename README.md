# TDS Virtual Teaching Assistant API

This project builds an intelligent API that acts as a Virtual Teaching Assistant for the **Tools in Data Science (TDS)** course (Jan 2025, IIT Madras Online BS Data Science and Applications). It enables automated answering of student questions using both text and image inputs.

The backend performs the following:

* **Fetches official course content** from the TDS Jan 2025 course page (as of 15 April 2025).
* **Scrapes Discourse posts** between 1 Jan 2025 – 14 Apr 2025 from the TDS category.
* **Extracts YouTube links** from the course and fetches transcripts for those videos.
* **Uses a RAG (Retrieval-Augmented Generation) pipeline** with Grok (LLM) to generate accurate, context-aware answers.
* **Handles optional base64-encoded screenshots** to improve understanding and question context.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/tds-virtual-ta-api.git
cd tds-virtual-ta-api
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Extract and Prepare Data

```bash
python tds_extract.py         # Course content
python disc_extract.py        # Discourse posts
python fetch_chunks.py        # Chunking content
python build_vector_store.py  # Build vector index
```

### 5. Launch the API

```bash
uvicorn grok_app:app --host 0.0.0.0 --port 8000
```

---

## 📡 API Usage

### Endpoint

```
POST /api/
```

### JSON Payload

```json
{
  "question": "What model should I use for GA5?",
  "image": "<base64_encoded_image_optional>"
}
```

### Sample cURL

```bash
curl "http://localhost:8000/api/" \
  -H "Content-Type: application/json" \
  -d '{"question": "Should I use gpt-4o-mini or gpt-3.5 turbo?", "image": "<base64_string>"}'
```

### Response

```json
{
  "answer": "You must use `gpt-3.5-turbo-0125`...",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/...",
      "text": "Clarification on model choice"
    }
  ]
}
```

## License
This project is licensed under the MIT License. See ```LICENSE.md``` for more details.
