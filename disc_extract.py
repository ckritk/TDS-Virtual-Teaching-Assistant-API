import requests
import json
import time
from datetime import datetime
import os

# === CONFIGURATION ===
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in" 
COOKIE_TOKEN = ""  
OUTPUT_FILE = "discourse_data_stream.jsonl"
START_DATE = "2025-01-01"
END_DATE = "2025-04-14"

# === Setup Headers and Session ===
headers = {
    "cookie": f"_t={COOKIE_TOKEN}",
    "User-Agent": "Mozilla/5.0"
}
session = requests.Session()
session.headers.update(headers)

# === Convert input date strings to datetime objects ===
start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")

page = 0
topic_count = 0

with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    while True:
        page += 1
        print(f"Fetching page {page}...")
        res = session.get(f"{BASE_URL}/latest.json?page={page}")

        if res.status_code != 200:
            print(f"Error: status code {res.status_code}")
            print(res.text[:300])
            break

        data = res.json()
        topics = data.get("topic_list", {}).get("topics", [])

        if not topics:
            print("No more topics.")
            break

        for topic in topics:
            created_str = topic.get("created_at", None)
            if not created_str:
                continue

            created_dt = datetime.strptime(created_str[:10], "%Y-%m-%d")

            # Skip outside date range
            if created_dt < start_dt:
                continue
            if created_dt > end_dt:
                continue

            topic_id = topic["id"]
            slug = topic["slug"]
            topic_url = f"{BASE_URL}/t/{slug}/{topic_id}.json"
            readable_url = f"{BASE_URL}/t/{slug}/{topic_id}"

            print(f"Fetching topic: {topic['title']} ({created_str})")
            topic_res = session.get(topic_url)

            if topic_res.status_code != 200:
                print(f"Skipped topic due to error {topic_res.status_code}")
                continue

            topic_data = topic_res.json()
            topic_entry = {
                "title": topic_data["title"],
                "url": readable_url,
                "created_at": created_str,
                "posts": []
            }

            for post in topic_data["post_stream"]["posts"]:
                topic_entry["posts"].append({
                    "username": post["username"],
                    "content": post["cooked"]
                })

            f.write(json.dumps(topic_entry, ensure_ascii=False) + "\n")
            topic_count += 1

            time.sleep(0.5)  # Avoid rate limits

print(f"Finished. {topic_count} topics saved to {OUTPUT_FILE}")
