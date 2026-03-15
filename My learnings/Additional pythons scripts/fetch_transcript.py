"""Fetch YouTube transcript for a single video."""
import sys
from youtube_transcript_api import YouTubeTranscriptApi

VIDEO_ID = "IppKbte0As4"

try:
    # Try fetching transcript
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(VIDEO_ID)
    
    # Get video title via pytube
    title = VIDEO_ID
    try:
        from pytube import YouTube
        yt = YouTube(f"https://www.youtube.com/watch?v={VIDEO_ID}")
        title = yt.title
        print(f"Video Title: {title}")
    except Exception as e:
        print(f"Could not get title: {e}")
        title = VIDEO_ID
    
    # Build clean text
    lines = []
    for snippet in transcript:
        text = snippet.text.replace('\n', ' ').strip()
        if text:
            lines.append(text)
    
    full_text = ' '.join(lines)
    
    # Also build timestamped version
    timestamped = []
    for snippet in transcript:
        start = snippet.start
        mins = int(start // 60)
        secs = int(start % 60)
        text = snippet.text.replace('\n', ' ').strip()
        if text:
            timestamped.append(f"[{mins:02d}:{secs:02d}] {text}")
    
    # Clean filename
    import re
    safe_title = re.sub(r'[^\w\s-]', '', str(title)).strip()
    safe_title = re.sub(r'\s+', '_', safe_title)
    filename = f"{safe_title}_transcript.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Video: {title}\n")
        f.write(f"URL: https://www.youtube.com/watch?v={VIDEO_ID}\n")
        f.write("=" * 80 + "\n\n")
        f.write("FULL TRANSCRIPT (Clean Text):\n")
        f.write("-" * 40 + "\n\n")
        f.write(full_text + "\n\n")
        f.write("=" * 80 + "\n\n")
        f.write("TIMESTAMPED TRANSCRIPT:\n")
        f.write("-" * 40 + "\n\n")
        for line in timestamped:
            f.write(line + "\n")
    
    print(f"\nTranscript saved to: {filename}")
    print(f"Total segments: {len(lines)}")
    print(f"\nFirst 500 chars preview:\n{full_text[:500]}...")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
