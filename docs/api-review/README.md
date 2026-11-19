# Barakah Buddies Uploader: how we use the YouTube Data API

GCP project: **barakah-buddies-uploader** (project number 377831788483)
OAuth client: "Barakah Buddies Uploader", used only by the channel owner
Source code: [uploader/upload.py](../../uploader/upload.py), run by [.github/workflows/upload.yml](../../.github/workflows/upload.yml)
Screencast: [screencast.mp4](screencast.mp4)

## 1. The four channels (all owned by the same person)

| Language | Channel | Channel ID link |
|---|---|---|
| English | https://www.youtube.com/@BarakahBuddiesEnglish | https://www.youtube.com/channel/UCFlIWRVBoDN4R_sZWxY_Zig |
| Urdu | https://www.youtube.com/@BarakahBuddiesUrdu | https://www.youtube.com/channel/UCJPLVD2gvrmpxNau6W7y2aQ |
| Hindi | https://www.youtube.com/@BarakahBuddiesHindi | https://www.youtube.com/channel/UC4-NYtwCgs9a9umPB2Q99fg |
| Tamil | https://www.youtube.com/@BarakahBuddiesTamil | https://www.youtube.com/channel/UCZo5q7QAfbhHt6bMNlLsTXg |

All four are Brand Accounts under one Google account. Every video is our own original
animated Short (under 60 seconds) for children aged 2 to 6, so every upload is
**Made for Kids**. Each channel posts 3 Shorts a day, at 09:30, 15:30 and 18:30 IST.
There are no other users: the tool only ever uploads to these four channels.

## 2. Step by step

**Step 1. Queue the finished Shorts.** We commit each finished Short and one line of
metadata per channel to the `queue` branch of this repository. The metadata file is
`schedule.json`. Here is a real example for one Short, going to all four channels
([schedule.example.json](schedule.example.json)):

```json
{
  "file": "t01/EN.mp4",
  "lang": "EN",
  "langCode": "en",
  "publishAt": "2026-12-01T09:30:00+05:30",
  "title": "Achoo! Say Alhamdulillah 🐱 | Islamic Manners for Kids | Barakah Buddies #shorts",
  "description": "Join Rayyan, Noor and Mishmish the kitten ... Source: Sahih al-Bukhari 6224 ...",
  "playlist": "Good Islamic Manners"
}
```

The Urdu, Hindi and Tamil entries have the same shape, with the title, description and
playlist name in that language (for example the Hindi playlist "अच्छे इस्लामी अदब").

**Step 2. Sign in as the channel.** A GitHub Actions workflow runs every 3 hours. For each
channel it uses that channel's own OAuth 2.0 refresh token. The owner created each
token once by signing in and choosing the Brand Account. Tokens are stored as encrypted
GitHub secrets (`YT_TOKEN_EN`, `YT_TOKEN_UR`, `YT_TOKEN_HI`, `YT_TOKEN_TA`).
Scope: `https://www.googleapis.com/auth/youtube`.

**Step 3. Upload and schedule the Short with `videos.insert`.** For each entry whose
publish time falls in the next 48 hours, the tool makes one resumable upload:

```python
body = {
  "snippet": {"title": item["title"], "description": item["description"],
              "categoryId": "27", "defaultLanguage": item["langCode"]},
  "status": {"privacyStatus": "private",
             "publishAt": "2026-12-01T04:00:00Z",   # 09:30 IST
             "selfDeclaredMadeForKids": True,
             "containsSyntheticMedia": False},
}
api.videos().insert(part="snippet,status", body=body, media_body=media).execute()
```

The video is created as private with a future `publishAt`. YouTube then makes it public
at the slot time. This is the standard scheduling method in the API docs.

**Step 4. Add the Short to its playlist.** The tool finds the playlist by title with
`playlists.list(mine=True)`. It then calls `playlistItems.insert` with the new video ID.

**Step 5. Record the upload.** The video ID is saved to `uploaded.json` on the queue
branch, so a Short is never uploaded twice. The video file is then removed from the queue.

## 3. API calls and daily quota

Per day: 12 Shorts (3 per channel x 4 channels).

| Call | Units each | Per day |
|---|---|---|
| videos.insert | 1,600 | 19,200 |
| playlistItems.insert | 50 | 600 |
| playlists.list | 1 | about 12 |
| **Total** | | **about 19,800** |

The default 10,000 units allow only 6 uploads a day, so we asked for a higher quota.

## 4. What the tool does not do

It does not read, collect or store any viewer data or other users' data. It does not
comment, like, subscribe or touch any channel other than our four. It does not
download videos. It does not change channel settings.
