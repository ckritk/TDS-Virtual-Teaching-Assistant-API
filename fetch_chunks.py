import json
from typing import List, Dict

import json
import pickle

def process_jsonl(jsonl_path):
    chunks = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            thread = json.loads(line)
            url = thread.get("url", "")
            title = thread.get("title", "")
            posts = thread.get("posts", [])

            # Combine all post contents
            full_text = ""
            for post in posts:
                username = post.get("username", "")
                content = post.get("content", "")
                full_text += f"[{username}]\n{content.strip()}\n\n"

            chunk = {
                "url": url,
                "title": title,
                "text": full_text.strip()
            }
            chunks.append(chunk)

    return chunks

def process_multi_doc_txt(txt_path: str, is_transcript=False) -> List[Dict]:
    """Split text file into separate documents using URL markers and extract chunks"""
    chunks = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Choose pattern based on type
    marker = "--- Transcript for: " if is_transcript else "--- Content from: "
    parts = content.split(marker)

    for part in parts[1:]:  # First split is before the first doc
        try:
            url, body = part.strip().split('---', 1)
        except ValueError:
            continue  
        paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
        for para in paragraphs:
            chunks.append({
                "text": para,
                "source": url.strip(),
                "title": "Transcript" if is_transcript else "Course Notes"
            })
    return chunks


discourse_chunks = process_jsonl("discourse_data_stream.jsonl")
notes_chunks = process_multi_doc_txt("tds_cleaned.txt", is_transcript=False)
transcript_chunks = process_multi_doc_txt("tds_youtube_transcripts.txt", is_transcript=True)

all_chunks = discourse_chunks + notes_chunks + transcript_chunks

print(len(discourse_chunks),len(notes_chunks),len(transcript_chunks))

import pickle

with open("parsed_chunks.pkl", "wb") as f:
    pickle.dump(all_chunks, f)

