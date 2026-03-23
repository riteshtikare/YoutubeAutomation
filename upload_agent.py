"""
UploadAgent — authenticates with YouTube Data API v3 and uploads
the video + thumbnail.  OAuth2 flow on first run, token cached afterward.
"""

import logging
import json
import os
from pathlib import Path

log = logging.getLogger(__name__)


class UploadAgent:
    def __init__(self, cfg):
        self.cfg = cfg

    def upload(
        self,
        video_path: Path,
        thumbnail_path: Path,
        title: str,
        description: str,
        tags: list,
    ) -> dict:
        youtube = self._get_client()
        video_id = self._upload_video(youtube, video_path, title, description, tags)
        self._set_thumbnail(youtube, video_id, thumbnail_path)
        return {"id": video_id}

    # ── OAuth2 client ─────────────────────────────────────────────
    def _get_client(self):
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        creds = None
        creds_file = Path(self.cfg.YOUTUBE_CREDENTIALS_FILE)

        if creds_file.exists():
            creds = Credentials.from_authorized_user_file(
                str(creds_file), self.cfg.YOUTUBE_SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.cfg.YOUTUBE_CLIENT_SECRETS,
                    self.cfg.YOUTUBE_SCOPES,
                )
                creds = flow.run_local_server(port=0)
            creds_file.parent.mkdir(parents=True, exist_ok=True)
            creds_file.write_text(creds.to_json())

        return build("youtube", "v3", credentials=creds)

    # ── Upload video ──────────────────────────────────────────────
    def _upload_video(self, youtube, video_path, title, description, tags):
        from googleapiclient.http import MediaFileUpload

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": self.cfg.YOUTUBE_CATEGORY_ID,
            },
            "status": {
                "privacyStatus": self.cfg.YOUTUBE_PRIVACY,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024 * 8,  # 8 MB chunks
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                log.info(f"  Uploading … {pct}%")

        video_id = response["id"]
        log.info(f"  Upload complete. Video ID: {video_id}")
        return video_id

    # ── Set thumbnail ─────────────────────────────────────────────
    def _set_thumbnail(self, youtube, video_id, thumbnail_path):
        from googleapiclient.http import MediaFileUpload

        media = MediaFileUpload(str(thumbnail_path), mimetype="image/png")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=media,
        ).execute()
        log.info("  Thumbnail set.")
