# Universal Video Player

A lightweight browser-based player that can play:

- Standard video files (MP4, WebM, etc.)
- HLS streams (`.m3u8`) with adaptive bitrate
- MPEG-DASH streams (`.mpd`) with adaptive bitrate

## Features

- Load by URL or local file
- Automatic adaptive quality mode
- Manual quality selection for HLS and DASH
- Clear status/error messages

## Run locally

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.
