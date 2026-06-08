# Troubleshooting

## The app opens, but the web page does not appear

Open this address manually in your browser:

```text
http://127.0.0.1:8765/
```

The app runs a local-only server on your Mac. It does not expose a public web service.

## macOS says the app cannot be opened

This alpha build is not notarized. Try reinstalling from the repo:

```bash
./install.sh
```

If macOS still blocks it, open Terminal and run:

```bash
xattr -dr com.apple.quarantine "/Applications/SoundCloud Downloader.app"
```

## Cookies do not work

For Chrome, choose the profile where you are logged into SoundCloud. Most people should start with:

```text
Chrome (Default)
```

Close Chrome before downloading private, liked, or age-restricted tracks. Chromium browsers can lock their cookie database while running.

## Downloads are lower quality than expected

The app asks yt-dlp for the best audio SoundCloud provides. Some SoundCloud streams are still AAC around 96-256 kbps. Converting a 96 kbps AAC stream to MP3 320 does not improve quality; it only makes a larger transcode.

## ffmpeg errors

Run the installer again so ffmpeg is downloaded into the app bundle:

```bash
./install.sh
```

## Where logs live

The app writes startup logs here:

```text
/tmp/soundcloud-downloader.log
```

