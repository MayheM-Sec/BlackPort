"""
MayheM-Sec Added

Local-only browser interface for BlackPort.

The server binds to 127.0.0.1, launches the MayheM-Sec unified scan wrapper,
and stops the complete child scan process group when the GUI exits.
Use only on systems and networks you own or have explicit permission to test.
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
DEFAULT_PORT = 8787
ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"

# MayheM-Sec Added: GUI choices are allow-listed before any subprocess starts.
TCP_PROFILES = {"top-100", "top-500", "top-1000", "full"}
UDP_PROFILES = {"top-25", "top-50", "top-100", "full"}
MODES = {"tcp", "syn", "udp", "mixed"}
HOST_RE = re.compile(r"^[A-Za-z0-9._:-]+(?:/[0-9]{1,3})?$")


class ScanState:
    """MayheM-Sec Added: thread-safe state for one local GUI scan."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.process: subprocess.Popen[str] | None = None
        self.started_at: float | None = None
        self.return_code: int | None = None
        self.command: list[str] = []
        self.output: deque[str] = deque(maxlen=4000)

    def running(self) -> bool:
        with self.lock:
            return self.process is not None and self.process.poll() is None

    def start(self, command: list[str]) -> None:
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                raise RuntimeError("A scan is already running")

            self.output.clear()
            self.return_code = None
            self.started_at = time.time()
            self.command = command[:]

            # MayheM-Sec Added: isolate the scan in its own process group/session.
            kwargs = dict(
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["start_new_session"] = True

            self.process = subprocess.Popen(command, **kwargs)
            process = self.process

        threading.Thread(target=self._capture, args=(process,), daemon=True).start()

    def _capture(self, process: subprocess.Popen[str]) -> None:
        assert process.stdout is not None
        for line in process.stdout:
            with self.lock:
                self.output.append(line.rstrip("\n"))
        code = process.wait()
        with self.lock:
            self.return_code = code

    def stop(self) -> None:
        with self.lock:
            process = self.process

        if process is None or process.poll() is not None:
            return

        # MayheM-Sec Added: stop the complete scan tree, not only the wrapper.
        try:
            if os.name == "nt":
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=4)
        except (subprocess.TimeoutExpired, ProcessLookupError, PermissionError):
            try:
                if os.name == "nt":
                    process.kill()
                else:
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
            except Exception:
                pass

        with self.lock:
            self.return_code = process.poll()

    def snapshot(self) -> dict:
        with self.lock:
            process = self.process
            running = process is not None and process.poll() is None
            return {
                "running": running,
                "started_at": self.started_at,
                "return_code": None if running else self.return_code,
                "command": self.command,
                "output": list(self.output),
            }


STATE = ScanState()
atexit.register(STATE.stop)


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BlackPort | MayheM-Sec</title>
<style>
:root{--bg:#090b10;--panel:#11151d;--panel2:#171c26;--line:#29303d;--text:#eef2f7;--muted:#93a0b2;--good:#7ee787;--warn:#f2cc60;--bad:#ff7b72}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}header{display:flex;justify-content:space-between;align-items:center;padding:20px 28px;border-bottom:1px solid var(--line);background:#0d1016}.brand{font-weight:800;letter-spacing:.09em}.brand small{display:block;margin-top:3px;color:var(--muted);font-weight:500;letter-spacing:.01em}.local{font-size:13px;color:var(--muted)}main{max-width:1220px;margin:auto;padding:28px}.grid{display:grid;grid-template-columns:390px 1fr;gap:22px}.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px}.panel h2{margin:0 0 6px;font-size:18px}.panel p{margin:0 0 18px;color:var(--muted);font-size:14px;line-height:1.5}label{display:block;margin:14px 0 7px;color:#cbd3df;font-size:13px}input,select{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:var(--panel2);color:var(--text)}.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}.buttons{display:flex;gap:10px;margin-top:18px}.btn{border:0;border-radius:9px;padding:11px 14px;font-weight:700;cursor:pointer}.primary{background:#e5e7eb;color:#11151d;flex:1}.secondary{background:#252d39;color:var(--text)}.danger{background:#3a1d22;color:#ffb4ae}.btn:disabled{opacity:.5;cursor:not-allowed}.notice{margin-top:18px;border-left:3px solid var(--warn);padding:12px 14px;background:#181811;color:#d8d1a5;border-radius:6px;font-size:13px;line-height:1.5}.console{min-height:570px;max-height:72vh;overflow:auto;background:#07090d;border:1px solid #222936;border-radius:10px;padding:16px;white-space:pre-wrap;font:12.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#c9d1d9}.meta{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:12px}.badge{border:1px solid var(--line);padding:5px 8px;border-radius:999px;color:var(--muted);font-size:12px}.hint{font-size:12px;color:var(--muted);margin-top:6px}footer{text-align:center;padding:8px 20px 28px;color:#657184;font-size:12px}@media(max-width:880px){.grid{grid-template-columns:1fr}.console{min-height:420px}main{padding:18px}}
</style>
</head>
<body>
<header><div class="brand">BLACKPORT<small>MayheM-Sec local interface</small></div><div class="local">127.0.0.1 · local only</div></header>
<main><div class="grid">
<section class="panel"><h2>New scan</h2><p>Run BlackPort from the browser without exposing the interface to your LAN or the Internet.</p>
<label for="target">Target</label><input id="target" placeholder="192.168.1.10 or 192.168.1.0/24" autocomplete="off">
<div class="row"><div><label for="mode">Scan mode</label><select id="mode" onchange="syncProfiles()"><option value="tcp">TCP connect</option><option value="syn">SYN</option><option value="udp">UDP</option><option value="mixed">Mixed TCP + UDP</option></select></div><div><label for="profile">TCP profile</label><select id="profile"><option value="top-100">Top 100</option><option value="top-500">Top 500</option><option value="top-1000">Top 1000</option><option value="full">Full</option></select></div></div>
<div id="udpRow"><label for="udpProfile">UDP profile</label><select id="udpProfile"><option value="top-25">Top 25</option><option value="top-50">Top 50</option><option value="top-100">Top 100</option><option value="full">Full</option></select><div class="hint">UDP uses conservative state classification. No response is reported as open|filtered, not automatically open.</div></div>
<div class="buttons"><button id="scan" class="btn primary" onclick="startScan()">Start scan</button><button id="stop" class="btn danger" onclick="stopScan()" disabled>Stop</button></div>
<div class="notice">Only scan systems you own or are explicitly authorized to test. SYN mode may require elevated privileges. Full UDP scans can take significantly longer than TCP scans.</div>
<div class="buttons"><button class="btn secondary" onclick="shutdownApp()">Shut down BlackPort</button></div></section>
<section class="panel"><div class="meta"><div><h2>Live output</h2><p id="summary">No scan running.</p></div><span id="runState" class="badge">IDLE</span></div><div id="console" class="console">BlackPort is ready.</div></section>
</div></main>
<footer>Original BlackPort work remains credited upstream. Fork-specific changes are marked MayheM-Sec Added.</footer>
<script>
const el=id=>document.getElementById(id);let lastText="";
async function api(path,body){const r=await fetch(path,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined});const d=await r.json();if(!r.ok)throw new Error(d.error||"Request failed");return d}
function syncProfiles(){const m=el("mode").value;el("profile").disabled=(m==="udp");el("udpProfile").disabled=(m==="tcp"||m==="syn");}
async function startScan(){try{await api("/api/scan",{target:el("target").value.trim(),mode:el("mode").value,tcp_profile:el("profile").value,udp_profile:el("udpProfile").value});await refresh()}catch(e){alert(e.message)}}
async function stopScan(){try{await api("/api/stop",{});await refresh()}catch(e){alert(e.message)}}
async function shutdownApp(){if(!confirm("Stop any active scan and shut down the local BlackPort GUI?"))return;try{await api("/api/shutdown",{});document.body.innerHTML='<main><section class="panel"><h2>BlackPort stopped</h2><p>The localhost listener is closed. You can close this tab.</p></section></main>'}catch(e){}}
async function refresh(){try{const s=await api("/api/status");el("scan").disabled=s.running;el("stop").disabled=!s.running;el("runState").textContent=s.running?"RUNNING":(s.return_code===0?"COMPLETE":(s.return_code===null?"IDLE":"STOPPED"));el("summary").textContent=s.running?"Scan in progress…":(s.started_at?"Last scan finished.":"No scan running.");const text=(s.output||[]).join("\n")||"BlackPort is ready.";if(text!==lastText){const c=el("console");c.textContent=text;c.scrollTop=c.scrollHeight;lastText=text}}catch(e){el("runState").textContent="OFFLINE"}}
syncProfiles();setInterval(refresh,900);refresh();
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    """MayheM-Sec Added: minimal local API and dashboard handler."""

    server_version = "BlackPortGUI/2.0"

    def log_message(self, fmt: str, *args) -> None:
        return

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        size = int(self.headers.get("Content-Length", "0"))
        if size > 16_384:
            raise ValueError("Request too large")
        raw = self.rfile.read(size) if size else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/status":
            self._json(STATE.snapshot())
            return
        self._json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/scan":
                self._start_scan(payload)
            elif path == "/api/stop":
                STATE.stop()
                self._json({"ok": True})
            elif path == "/api/shutdown":
                STATE.stop()
                self._json({"ok": True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                self._json({"error": "Not found"}, 404)
        except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": f"Unable to complete request: {exc}"}, 500)

    def _start_scan(self, payload: dict) -> None:
        target = str(payload.get("target", "")).strip()
        mode = str(payload.get("mode", "tcp")).lower()
        tcp_profile = str(payload.get("tcp_profile", "top-100"))
        udp_profile = str(payload.get("udp_profile", "top-25"))

        if not target or len(target) > 253 or not HOST_RE.fullmatch(target):
            raise ValueError("Enter a valid IP address, hostname, or CIDR target")
        if mode not in MODES:
            raise ValueError("Unknown scan mode")
        if tcp_profile not in TCP_PROFILES:
            raise ValueError("Unknown TCP profile")
        if udp_profile not in UDP_PROFILES:
            raise ValueError("Unknown UDP profile")

        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(ROOT / "mayhem_scan.py"),
            target,
            "--mode", mode,
            "--tcp-profile", tcp_profile,
            "--udp-profile", udp_profile,
            "--output-dir", str(REPORT_DIR),
        ]
        STATE.start(command)
        self._json({"ok": True, "command": command})


def run_gui(port: int = DEFAULT_PORT, open_browser: bool = True) -> None:
    """MayheM-Sec Added: run BlackPort locally until explicitly closed."""
    server = ThreadingHTTPServer((HOST, port), Handler)
    server.daemon_threads = True
    url = f"http://{HOST}:{port}"

    print(f"[MayheM-Sec Added] BlackPort GUI: {url}")
    print("[MayheM-Sec Added] Localhost only. Press Ctrl+C or use Shut down BlackPort to close it.")

    if open_browser:
        threading.Timer(0.35, lambda: webbrowser.open(url, new=2)).start()

    try:
        server.serve_forever(poll_interval=0.4)
    except KeyboardInterrupt:
        pass
    finally:
        STATE.stop()
        server.server_close()
        print("[MayheM-Sec Added] BlackPort GUI stopped; localhost listener closed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="BlackPort local graphical interface")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local GUI port (default: 8787)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    args = parser.parse_args()

    if not 1024 <= args.port <= 65535:
        parser.error("--port must be between 1024 and 65535")

    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))

    run_gui(args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
