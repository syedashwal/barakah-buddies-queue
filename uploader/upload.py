"""Barakah Buddies uploader.

Reads schedule.json from the `queue` branch checkout and uploads every Short
whose publish time is within the look-ahead window and that is not yet in
uploaded.json. Each upload is private with a future publishAt, so YouTube
publishes it at the slot time. Made for kids is always on.

Secrets (GitHub Actions): YT_CLIENT_ID, YT_CLIENT_SECRET and one refresh
token per channel: YT_TOKEN_EN, YT_TOKEN_UR, YT_TOKEN_HI, YT_TOKEN_TA.
"""
import datetime as dt
import json
import os
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

QUEUE = os.environ.get("QUEUE_DIR", "queue")
LOOKAHEAD_H = int(os.environ.get("LOOKAHEAD_HOURS", "48"))
DRY = os.environ.get("DRY_RUN") == "1"


def yt(lang):
    tok = os.environ.get(f"YT_TOKEN_{lang}")
    if not tok:
        raise SystemExit(f"missing secret YT_TOKEN_{lang}")
    creds = Credentials(None, refresh_token=tok, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                        scopes=["https://www.googleapis.com/auth/youtube"])
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def playlist_id(api, title):
    req = api.playlists().list(part="snippet", mine=True, maxResults=50)
    while req:
        res = req.execute()
        for p in res.get("items", []):
            if p["snippet"]["title"] == title:
                return p["id"]
        req = api.playlists().list_next(req, res)
    return None


def main():
    sched = json.load(open(os.path.join(QUEUE, "schedule.json"), encoding="utf-8"))
    done_path = os.path.join(QUEUE, "uploaded.json")
    done = json.load(open(done_path, encoding="utf-8")) if os.path.exists(done_path) else {}
    now = dt.datetime.now(dt.timezone.utc)
    horizon = now + dt.timedelta(hours=LOOKAHEAD_H)
    apis, failures = {}, 0
    for item in sched:
        key = f'{item["file"]}@{item["publishAt"]}'
        if key in done:
            continue
        when = dt.datetime.fromisoformat(item["publishAt"])
        if when <= now + dt.timedelta(minutes=20) or when > horizon:
            continue  # too late to schedule safely, or not due yet
        lang = item["lang"]
        print(f"upload {item['file']} -> {lang} at {item['publishAt']}")
        if DRY:
            continue
        try:
            api = apis.setdefault(lang, yt(lang))
            body = {
                "snippet": {"title": item["title"], "description": item["description"],
                            "categoryId": "27", "defaultLanguage": item.get("langCode", "en")},
                "status": {"privacyStatus": "private", "publishAt": when.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                           "selfDeclaredMadeForKids": True, "containsSyntheticMedia": False},
            }
            media = MediaFileUpload(os.path.join(QUEUE, item["file"]), mimetype="video/mp4", resumable=True)
            vid = api.videos().insert(part="snippet,status", body=body, media_body=media).execute()["id"]
            if item.get("playlist"):
                pid = playlist_id(api, item["playlist"])
                if pid:
                    api.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": pid,
                        "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            done[key] = vid
            print(f"  ok https://youtube.com/shorts/{vid}")
        except Exception as e:  # keep going with the other channels
            failures += 1
            print(f"  FAILED: {e}", file=sys.stderr)
    json.dump(done, open(done_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
