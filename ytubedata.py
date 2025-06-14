from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """Extract YouTube video ID from any youtu.be or youtube.com link"""
    parsed_url = urlparse(url.strip())
    if 'youtu.be' in parsed_url.netloc:
        return parsed_url.path.lstrip('/')
    elif 'youtube.com' in parsed_url.netloc:
        query = parse_qs(parsed_url.query)
        return query.get('v', [None])[0]
    return None

input_file = "tds_youtube_links.txt"
output_file = "tds_youtube_transcripts.txt"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        yt_url = line.strip()
        if not yt_url:
            continue

        video_id = extract_video_id(yt_url)
        if not video_id:
            print(f"Skipping invalid URL: {yt_url}")
            continue

        print(f"Fetching transcript for: {yt_url}")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = "\n".join([entry["text"] for entry in transcript])

            outfile.write(f"--- Transcript for: {yt_url} ---\n")
            outfile.write(transcript_text)
            outfile.write("\n\n")
        except Exception as e:
            print(f"No transcript available for {yt_url}: {e}")
            outfile.write(f"--- Transcript for: {yt_url} ---\n")
            outfile.write("No transcript available.\n\n")

print("Done! All transcripts saved to yt_transcripts.txt")
