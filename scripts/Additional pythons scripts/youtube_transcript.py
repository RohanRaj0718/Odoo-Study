import argparse
import os
import re
import sys
from urllib.parse import parse_qs, urlparse

try:
    from pytube import Playlist, YouTube
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError as exc:
    missing = str(exc).split("No module named ")[-1].strip("'\"")
    print(
        "Missing dependency: {}.\n".format(missing)
        + "Install required packages with:\n"
        + "  pip install pytube youtube-transcript-api\n",
        file=sys.stderr,
    )
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download YouTube transcripts for a video or playlist.",
    )
    parser.add_argument("url", nargs="?", help="YouTube video or playlist URL")
    parser.add_argument(
        "--output-dir",
        default="transcripts",
        help="Output folder for transcript files",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="If a playlist is detected, download all videos without prompting",
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="If a playlist is detected, download only the given video",
    )
    return parser.parse_args()


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.hostname in {"youtu.be"}:
        return parsed.path.lstrip("/") or None

    if parsed.hostname and "youtube" in parsed.hostname:
        query = parse_qs(parsed.query)
        if "v" in query and query["v"]:
            return query["v"][0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/embed/")[-1]

    return None


def extract_playlist_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.hostname and "youtube" in parsed.hostname:
        query = parse_qs(parsed.query)
        if "list" in query and query["list"]:
            return query["list"][0]
    return None


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def safe_filename(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/:*?\"<>|]", "_", value)
    value = re.sub(r"\s+", " ", value)
    return value[:120] if value else "untitled"


def write_transcript(output_dir: str, title: str, video_id: str, transcript: list[dict]) -> str:
    os.makedirs(output_dir, exist_ok=True)
    safe_title = safe_filename(title)
    filename = f"{safe_title}__{video_id}.txt"
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as handle:
        for item in transcript:
            timestamp = format_timestamp(item.get("start", 0))
            text = item.get("text", "").replace("\n", " ").strip()
            handle.write(f"[{timestamp}] {text}\n")

    return path


def fetch_title(url: str, fallback: str) -> str:
    try:
        return YouTube(url).title or fallback
    except Exception:
        return fallback


def download_transcript(url: str, output_dir: str) -> None:
    video_id = extract_video_id(url)
    if not video_id:
        print(f"Could not extract video ID from: {url}", file=sys.stderr)
        return

    title = fetch_title(url, video_id)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as exc:
        print(f"Transcript unavailable for {video_id}: {exc}", file=sys.stderr)
        return

    path = write_transcript(output_dir, title, video_id, transcript)
    print(f"Saved: {path}")


def handle_playlist(playlist_id: str, output_dir: str) -> None:
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    playlist = Playlist(playlist_url)
    video_urls = list(playlist.video_urls)

    if not video_urls:
        print("No videos found in playlist.", file=sys.stderr)
        return

    for index, url in enumerate(video_urls, start=1):
        print(f"[{index}/{len(video_urls)}] Processing {url}")
        download_transcript(url, output_dir)


def prompt_yes_no(message: str) -> bool:
    answer = input(f"{message} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def main() -> int:
    args = parse_args()
    url = args.url or input("YouTube URL: ").strip()
    if not url:
        print("A YouTube URL is required.", file=sys.stderr)
        return 1

    playlist_id = extract_playlist_id(url)
    if playlist_id and not args.single:
        if args.all or prompt_yes_no("Playlist detected. Download transcripts for all videos?"):
            handle_playlist(playlist_id, args.output_dir)
            return 0

    download_transcript(url, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
