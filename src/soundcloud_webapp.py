#!/usr/bin/env python3
import json
import os
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOME = os.path.expanduser("~")
RESOURCES = os.environ.get("SOUNDCLOUD_DOWNLOADER_RESOURCES", "")
if RESOURCES and os.path.isdir(RESOURCES):
    YTDLP = os.path.join(RESOURCES, "yt-dlp_macos")
    FFMPEG_DIR = RESOURCES
else:
    YTDLP = os.path.join(HOME, "Downloads", "yt-dlp_macos")
    FFMPEG_DIR = os.path.join(HOME, "Downloads", "soundcloud")
FFMPEG = os.path.join(FFMPEG_DIR, "ffmpeg")
DEFAULT_OUTPUT = os.path.join(HOME, "Downloads")
DEFAULT_OUTPUT_DISPLAY = "~/Downloads"

state = {
    "running": False,
    "status": "Ready",
    "code": None,
    "log": "",
    "process": None,
}
lock = threading.Lock()


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SoundCloud Downloader</title>
<style>
:root {
  --orange: #ff5500;
  --orange-2: #ff7a2f;
  --bg: #101010;
  --panel: #1d1d1d;
  --panel-2: #282828;
  --line: #353535;
  --text: #f7f7f7;
  --muted: #b9b9b9;
  --green: #72d67c;
  --yellow: #ffd166;
  --red: #ff6b66;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(255,85,0,.18), transparent 28rem),
    linear-gradient(135deg, #181818, #0b0b0b);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.app { max-width: 1040px; margin: 0 auto; padding: 28px; }
.shell {
  overflow: hidden;
  border: 1px solid #333;
  background: var(--panel);
  box-shadow: 0 24px 90px rgba(0,0,0,.45);
  border-radius: 12px;
}
.hero {
  background: linear-gradient(135deg, var(--orange), #ff3300);
  padding: 24px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
h1 { margin: 0; font-size: 30px; letter-spacing: 0; }
.sub { margin-top: 5px; color: rgba(255,255,255,.86); font-size: 14px; }
.badge {
  border: 1px solid rgba(255,255,255,.4);
  color: white;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 13px;
  white-space: nowrap;
}
.content { padding: 24px; display: grid; gap: 18px; }
.card {
  border: 1px solid var(--line);
  background: rgba(20,20,20,.78);
  border-radius: 8px;
  padding: 18px;
}
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid3 { display: grid; grid-template-columns: 1.15fr 1fr 1fr; gap: 16px; }
label { display: block; color: var(--muted); font-size: 13px; margin-bottom: 8px; font-weight: 650; }
input, select {
  width: 100%;
  height: 42px;
  border: 1px solid #444;
  border-radius: 6px;
  background: var(--panel-2);
  color: var(--text);
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}
input:focus, select:focus { border-color: var(--orange); box-shadow: 0 0 0 3px rgba(255,85,0,.18); }
.hint { margin-top: 9px; color: var(--muted); font-size: 13px; line-height: 1.35; }
.detect { color: var(--green); font-weight: 700; min-height: 18px; }
.checks { display: flex; flex-wrap: wrap; gap: 14px 24px; align-items: center; }
.check { display: inline-flex; align-items: center; gap: 9px; color: var(--text); font-weight: 600; }
.check input { width: 18px; height: 18px; accent-color: var(--orange); }
.actions { display: grid; grid-template-columns: 1fr auto; gap: 14px; align-items: center; }
button {
  border: 0;
  border-radius: 7px;
  background: var(--orange);
  color: white;
  font-size: 18px;
  font-weight: 800;
  height: 50px;
  padding: 0 34px;
  cursor: pointer;
}
button:hover { background: var(--orange-2); }
button.cancel { background: #b7352b; }
button.small {
  height: 42px;
  padding: 0 16px;
  border: 1px solid #444;
  background: var(--panel-2);
  font-size: 14px;
}
button.small:hover { background: #363636; }
.path-row { display: grid; grid-template-columns: 1fr auto; gap: 10px; }
.status { color: var(--muted); font-size: 14px; }
.status.good { color: var(--green); }
.status.warn { color: var(--yellow); }
.status.bad { color: var(--red); }
pre {
  margin: 0;
  height: 210px;
  overflow: auto;
  white-space: pre-wrap;
  background: #070707;
  border: 1px solid #303030;
  border-radius: 7px;
  color: #eeeeee;
  padding: 14px;
  font: 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
@media (max-width: 820px) {
  .grid, .grid3, .actions { grid-template-columns: 1fr; }
  .hero { align-items: flex-start; flex-direction: column; }
  .app { padding: 14px; }
}
</style>
</head>
<body>
<main class="app">
  <section class="shell">
    <header class="hero">
      <div>
        <h1>SoundCloud Downloader</h1>
        <div class="sub">A local yt-dlp control panel for tracks, playlists, likes, and reposts.</div>
      </div>
      <div class="badge" id="readyBadge">Checking tools...</div>
    </header>

    <div class="content">
      <section class="card">
        <label for="url">SoundCloud URL</label>
        <input id="url" placeholder="https://soundcloud.com/artist/track">
        <div class="hint">Track: /artist/track | Playlist: /artist/sets/name | Artist: /artist | Likes: /artist/likes | Reposts: /artist/reposts</div>
        <div class="hint detect" id="detected"></div>
      </section>

      <section class="card grid">
        <div>
          <label for="quality">Audio Format & Quality</label>
          <select id="quality">
            <option>Best (keep original format)</option>
            <option>MP3 320 kbps</option>
            <option>MP3 192 kbps</option>
            <option>MP3 128 kbps</option>
            <option>FLAC (lossless)</option>
            <option>OGG Vorbis</option>
          </select>
        </div>
        <div>
          <label for="output">Save To</label>
          <div class="path-row">
            <input id="output">
            <button class="small" id="browse" type="button">Browse</button>
          </div>
        </div>
      </section>

      <section class="card grid3">
        <div>
          <label>Playlist / Collection</label>
          <div class="checks"><label class="check"><input type="checkbox" id="playlist"> Download entire playlist</label></div>
          <div class="hint">Auto-enabled for sets, artist pages, likes, and reposts.</div>
        </div>
        <div>
          <label for="range">Track Range</label>
          <input id="range" placeholder="1-10">
        </div>
        <div>
          <label>Metadata</label>
          <div class="checks">
            <label class="check"><input type="checkbox" id="metadata" checked> Metadata</label>
            <label class="check"><input type="checkbox" id="artwork"> Artwork</label>
          </div>
        </div>
      </section>

      <section class="card grid">
        <div>
          <label>Download Speed Limit</label>
          <div class="checks">
            <label class="check"><input type="checkbox" id="limitSpeed" checked> Limit speed</label>
            <select id="speed" style="max-width: 190px">
              <option>500K  (0.5 MB/s)</option>
              <option selected>1M  (1 MB/s)</option>
              <option>2M  (2 MB/s)</option>
              <option>5M  (5 MB/s)</option>
            </select>
          </div>
          <div class="hint">Useful on shared networks or to avoid SoundCloud rate limiting.</div>
        </div>
        <div>
          <label>Browser Cookies</label>
          <div class="checks">
            <label class="check"><input type="checkbox" id="useCookies"> Use cookies from</label>
            <select id="browser" style="max-width: 220px">
              <option>Chrome (Default)</option>
              <option>Chrome (Profile 1)</option>
              <option>Chrome (Profile 2)</option>
              <option>Firefox</option>
              <option>Edge</option>
              <option>Brave</option>
              <option>Opera</option>
              <option>Vivaldi</option>
            </select>
          </div>
          <div class="hint">For private/liked tracks, close the browser first and pick the profile logged into SoundCloud.</div>
        </div>
      </section>

      <section class="actions">
        <div class="status" id="status">Ready.</div>
        <button id="download">Download</button>
      </section>

      <section class="card">
        <label>Progress Log</label>
        <pre id="log"></pre>
      </section>
    </div>
  </section>
</main>
<script>
const $ = id => document.getElementById(id);
let poll = null;

async function init() {
  const res = await fetch('/api/info');
  const data = await res.json();
  $('output').value = data.default_output;
  $('readyBadge').textContent = data.ffmpeg ? 'yt-dlp + ffmpeg ready' : 'yt-dlp ready';
  detect();
  setInterval(refresh, 800);
}

function detect() {
  const raw = $('url').value.trim().toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split(/[?#]/)[0].replace(/\/$/, '');
  const out = $('detected');
  if (!raw) { out.textContent = ''; return; }
  if (!raw.startsWith('soundcloud.com/')) { out.textContent = 'Paste a SoundCloud URL'; return; }
  const seg = raw.replace('soundcloud.com/', '').split('/');
  if (seg.length === 1) { out.textContent = 'Detected: Artist page - all tracks'; $('playlist').checked = true; }
  else if (seg.length >= 3 && seg[1] === 'sets') { out.textContent = 'Detected: Playlist / Set'; $('playlist').checked = true; }
  else if (seg.length === 2 && ['likes','reposts'].includes(seg[1])) { out.textContent = `Detected: ${seg[1]} - cookies may be needed`; $('playlist').checked = true; }
  else if (seg.length === 2) { out.textContent = 'Detected: Single track'; $('playlist').checked = false; }
}

function payload() {
  return {
    url: $('url').value,
    quality: $('quality').value,
    output: $('output').value,
    playlist: $('playlist').checked,
    range: $('range').value,
    metadata: $('metadata').checked,
    artwork: $('artwork').checked,
    limitSpeed: $('limitSpeed').checked,
    speed: $('speed').value.split(/\s+/)[0],
    useCookies: $('useCookies').checked,
    browser: $('browser').value
  };
}

async function startOrCancel() {
  if ($('download').classList.contains('cancel')) {
    await fetch('/api/cancel', {method:'POST'});
    return;
  }
  const res = await fetch('/api/download', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload())});
  const data = await res.json();
  if (!data.ok) alert(data.error || 'Could not start download');
  await refresh();
}

async function browseFolder() {
  const res = await fetch('/api/choose-folder', {method:'POST'});
  const data = await res.json();
  if (data.ok && data.path) $('output').value = data.path;
}

async function refresh() {
  const res = await fetch('/api/status');
  const data = await res.json();
  $('status').textContent = data.status;
  $('status').className = 'status' + (data.running ? ' warn' : data.code === 0 ? ' good' : data.code ? ' bad' : '');
  $('log').textContent = data.log;
  $('log').scrollTop = $('log').scrollHeight;
  $('download').textContent = data.running ? 'Cancel' : 'Download';
  $('download').className = data.running ? 'cancel' : '';
}

$('url').addEventListener('input', detect);
$('download').addEventListener('click', startOrCancel);
$('browse').addEventListener('click', browseFolder);
init();
</script>
</body>
</html>
"""


def browser_arg(value):
    return {
        "Chrome (Default)": "chrome:Default",
        "Chrome (Profile 1)": "chrome:Profile 1",
        "Chrome (Profile 2)": "chrome:Profile 2",
    }.get(value, value.lower())


def quote(value):
    if re.search(r"[\s'\"$`]", value):
        return "'" + value.replace("'", "'\\''") + "'"
    return value


def append_log(text):
    with lock:
        state["log"] += text
        if len(state["log"]) > 120000:
            state["log"] = state["log"][-120000:]


def run_download(command, output_dir):
    with lock:
        state["running"] = True
        state["code"] = None
        state["status"] = "Downloading..."
        state["log"] = "$ " + " ".join(quote(x) for x in command) + "\n\n"
    try:
        proc = subprocess.Popen(command, cwd=output_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        with lock:
            state["process"] = proc
        for line in proc.stdout:
            append_log(line)
        code = proc.wait()
        with lock:
            state["running"] = False
            state["code"] = code
            state["process"] = None
            state["status"] = "Done. Saved to " + output_dir if code == 0 else f"Download failed with exit code {code}"
        if code == 0:
            subprocess.Popen(["open", output_dir])
    except Exception as exc:
        with lock:
            state["running"] = False
            state["code"] = -1
            state["process"] = None
            state["status"] = "Could not start download"
        append_log(str(exc) + "\n")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            body = HTML.encode()
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/info":
            self.send_json({"default_output": DEFAULT_OUTPUT_DISPLAY, "yt_dlp": os.path.exists(YTDLP), "ffmpeg": os.path.exists(FFMPEG)})
        elif self.path == "/api/status":
            with lock:
                self.send_json({k: state[k] for k in ("running", "status", "code", "log")})
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("content-length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        if self.path == "/api/cancel":
            with lock:
                proc = state.get("process")
            if proc and proc.poll() is None:
                proc.terminate()
                append_log("\nCancel requested.\n")
            self.send_json({"ok": True})
            return
        if self.path == "/api/choose-folder":
            script = 'POSIX path of (choose folder with prompt "Save SoundCloud downloads to:")'
            try:
                result = subprocess.run(["osascript", "-e", script], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    self.send_json({"ok": True, "path": result.stdout.strip()})
                else:
                    self.send_json({"ok": False, "error": result.stderr.strip() or "Folder selection canceled"})
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, 500)
            return
        if self.path != "/api/download":
            self.send_error(404)
            return
        try:
            data = json.loads(raw.decode())
        except Exception:
            self.send_json({"ok": False, "error": "Bad request"}, 400)
            return

        with lock:
            if state["running"]:
                self.send_json({"ok": False, "error": "A download is already running"}, 409)
                return

        url = (data.get("url") or "").strip()
        if not url:
            self.send_json({"ok": False, "error": "Paste a SoundCloud URL first"}, 400)
            return
        output = os.path.expanduser((data.get("output") or DEFAULT_OUTPUT).strip())
        os.makedirs(output, exist_ok=True)

        args = ["-f", "bestaudio/best"]
        quality = data.get("quality")
        if quality == "MP3 320 kbps":
            args += ["-x", "--audio-format", "mp3", "--audio-quality", "320K"]
        elif quality == "MP3 192 kbps":
            args += ["-x", "--audio-format", "mp3", "--audio-quality", "192K"]
        elif quality == "MP3 128 kbps":
            args += ["-x", "--audio-format", "mp3", "--audio-quality", "128K"]
        elif quality == "FLAC (lossless)":
            args += ["-x", "--audio-format", "flac"]
        elif quality == "OGG Vorbis":
            args += ["-x", "--audio-format", "vorbis"]
        if data.get("metadata"):
            args.append("--embed-metadata")
        if data.get("artwork"):
            args.append("--embed-thumbnail")
        if data.get("limitSpeed"):
            args += ["-r", data.get("speed") or "1M"]
        if data.get("useCookies"):
            args += ["--cookies-from-browser", browser_arg(data.get("browser") or "Chrome (Default)")]
        if os.path.exists(FFMPEG):
            args += ["--ffmpeg-location", FFMPEG_DIR]
        if data.get("playlist"):
            if (data.get("range") or "").strip():
                args += ["--playlist-items", data["range"].strip()]
            args += ["-o", os.path.join(output, "%(playlist_index)02d - %(uploader)s - %(title)s.%(ext)s")]
        else:
            args += ["--no-playlist", "-o", os.path.join(output, "%(uploader)s - %(title)s.%(ext)s")]
        args.append(url)

        command = [YTDLP] + args
        threading.Thread(target=run_download, args=(command, output), daemon=True).start()
        self.send_json({"ok": True})


def main():
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    except OSError:
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    threading.Timer(0.4, lambda: subprocess.Popen(["open", url])).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
