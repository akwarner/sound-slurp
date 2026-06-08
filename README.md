# SoundCloud Downloader

A small macOS app wrapper around [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading SoundCloud tracks, playlists, artist pages, likes, and reposts.

It runs a local control panel in your browser at `http://127.0.0.1:8765/`, with a SoundCloud-inspired interface and live download logs.

> This is an alpha made for friends. It is not affiliated with SoundCloud. Use it responsibly and only download media you have rights or permission to save.

![SoundCloud Downloader screenshot](assets/screenshots/soundcloud-downloader.png)

## Features

- SoundCloud URL detection for tracks, sets, artist pages, likes, and reposts
- Best original audio by default
- Optional MP3, FLAC, and OGG conversion through ffmpeg
- Playlist range support, such as `1-10` or `5-5`
- Metadata and artwork embedding
- Download speed limiting
- Browser cookie support for private, liked, or age-restricted tracks
- Local-only web UI with live yt-dlp output

## Quick Install

Clone or download this repo, then run:

```bash
./install.sh
```

The installer downloads `yt-dlp_macos` and `ffmpeg`, builds the app wrapper, and installs:

```text
/Applications/SoundCloud Downloader.app
```

Open the app from Applications. If a browser tab does not appear, open:

```text
http://127.0.0.1:8765/
```

## Cookies

For private tracks, liked tracks, or age-restricted content:

1. Log into SoundCloud in your browser.
2. Close that browser.
3. Enable **Use cookies from** in the app.
4. Pick the profile where you are logged in, usually **Chrome (Default)**.

The app does not store or upload cookies. It passes the selected browser profile to yt-dlp locally.

## Quality Notes

The default **Best (keep original format)** option is usually the safest choice. If SoundCloud only serves a compressed AAC stream, converting it to MP3 320 will not improve the source quality.

## Development

Run the web app locally:

```bash
./scripts/run_dev.sh
```

Rebuild the macOS app:

```bash
./scripts/build_app.sh --download --open
```

Install somewhere other than `/Applications`:

```bash
APP_PATH="$HOME/Desktop/SoundCloud Downloader.app" ./scripts/build_app.sh --download
```

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md).

