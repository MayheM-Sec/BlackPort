"""
MayheM-Sec Added

BlackPort local GUI v3.

Extends the MayheM-Sec v2 GUI with local scan history and a report viewer while
reusing the same localhost-only process controls.
"""

from __future__ import annotations

import argparse
import json
import threading
import webbrowser
from http.server import ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from blackport.report_index import list_reports, load_report
from gui_server_v2 import DEFAULT_PORT, HOST, REPORT_DIR, STATE, Handler as BaseHandler


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BlackPort | MayheM-Sec</title>
<style>
:root{--bg:#090b10;--panel:#11151d;--panel2:#171c26;--line:#262d3a;--text:#edf2f7;--muted:#8e9aab;--accent:#e5e7eb;--good:#7ee787;--warn:#f2cc60;--bad:#ff7b72;--blue:#79c0ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{display:flex;align-items:center;justify-content:space-between;padding:20px 28px;border-bottom:1px solid var(--line);background:#0c0f15;position:sticky;top:0;z-index:3}.brand{font-weight:800;letter-spacing:.08em}.brand small{display:block;font-weight:500;letter-spacing:.02em;color:var(--muted);margin-top:3px}.status{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:14px}.dot{width:9px;height:9px;border-radius:50%;background:var(--good)}main{max-width:1320px;margin:0 auto;padding:28px}.grid{display:grid;grid-template-columns:390px 1fr;gap:22px}.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:22px}.panel h2{margin:0 0 6px;font-size:18px}.panel p{color:var(--muted);font-size:14px;line-height:1.5;margin:0 0 18px}label{display:block;color:#c8d0dc;font-size:13px;margin:14px 0 7px}input,select{width:100%;background:var(--panel2);border:1px solid var(--line);border-radius:9px;color:var(--text);padding:11px 12px;outline:none}.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}.buttons{display:flex;gap:10px;margin-top:18px}.btn{border:0;border-radius:9px;padding:11px 14px;font-weight:700;cursor:pointer}.primary{background:var(--accent);color:#101318;flex:1}.secondary{background:#252c38;color:var(--text)}.danger{background:#3b1d22;color:#ffb4ae}.btn:disabled{opacity:.5;cursor:not-allowed}.notice{border-left:3px solid var(--warn);background:#181811;padding:12px 14px;border-radius:6px;color:#d8d1a5;font-size:13px;line-height:1.45;margin-top:18px}.info{border-left-color:var(--blue);background:#101722;color:#b8d8f5}.console{background:#07090d;border:1px solid #222936;border-radius:10px;min-height:430px;max-height:58vh;overflow:auto;padding:16px;font:12.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre-wrap;color:#c9d1d9}.console.empty{color:#657184}.meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}.badge{font-size:12px;border:1px solid var(--line);padding:5px 8px;border-radius:999px;color:var(--muted)}.hidden{display:none}.history{display:grid;gap:10px}.report{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;border:1px solid var(--line);background:var(--panel2);border-radius:10px;padding:12px}.report strong{display:block;font-size:13px}.report small{display:block;color:var(--muted);margin-top:4px}.report button{background:#252c38;border:0;color:var(--text);padding:8px 10px;border-radius:8px;cursor:pointer}.viewer{max-height:520px;overflow:auto;background:#07090d;border:1px solid var(--line);border-radius:10px;padding:14px;white-space:pre-wrap;font:12px/1.5 ui-monospace,monospace}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}.card{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:12px}.card b{font-size:20px;display:block}.card span{color:var(--muted);font-size:12px}footer{text-align:center;color:#657184;padding:10px 28px 30px;font-size:12px}@media(max-width:930px){.grid{grid-template-columns:1fr}.cards{grid-template-columns:repeat(2,1fr)}main{padding:18px}}
</style></head><body>
<header><div class="brand">BLACKPORT<small>MayheM-Sec local interface</small></div><div class="status"><span class="dot"></span>Local only · 127.0.0.1</div></header>
<main><div class="grid"><section>
<div class="panel"><h2>New scan</h2><p>Run TCP, SYN, UDP, or mixed scans from the local machine.</p><label>Target</label><input id="target" placeholder="192.168.1.10 or 192.168.1.0/24"><label>Scan mode</label><select id="mode" onchange="syncMode()"><option value="tcp">TCP connect</option><option value="syn">SYN</option><option value="udp">UDP</option><option value="mixed">Mixed TCP + UDP</option></select><div id="tcpBox"><label>TCP port profile</label><select id="tcpProfile"><option value="top-100">Top 100</option><option value="top-500">Top 500</option><option value="top-1000">Top 1000</option><option value="full">Full 1-65535</option></select></div><div id="udpBox" class="hidden"><label>UDP port profile</label><select id="udpProfile"><option value="top-25">Top 25</option><option value="top-50">Top 50</option><option value="top-100">Top 100</option><option value="full">Full 1-65535</option></select><div class="row"><div><label>UDP timeout</label><input id="udpTimeout" type="number" min="0.1" max="10" step="0.1" value="1.0"></div><div><label>UDP retries</label><input id="udpRetries" type="number" min="1" max="5" value="2"></div></div></div><div class="buttons"><button id="scan" class="btn primary" onclick="startScan()">Start scan</button><button id="stop" class="btn danger" onclick="stopScan()" disabled>Stop</button></div><div class="notice">Use only against systems you own or have explicit authorization to assess.</div><div class="notice info">UDP silence is treated as <b>open|filtered</b>, not as confirmed open.</div><div class="buttons"><button class="btn secondary" onclick="shutdownApp()">Shut down BlackPort</button></div></div>
<div class="panel"><h2>Recent reports</h2><p>Local JSON reports generated by BlackPort.</p><div id="history" class="history">Loading…</div></div>
</section><section>
<div class="panel"><div class="meta"><div><h2>Live output</h2><p id="summary">No scan running.</p></div><span class="badge" id="runState">IDLE</span></div><div id="console" class="console empty">BlackPort is ready.</div></div>
<div class="panel"><div class="meta"><div><h2>Report viewer</h2><p id="reportTitle">Select a report from the history list.</p></div><span class="badge">LOCAL</span></div><div id="viewer" class="viewer">No report selected.</div></div>
</section></div></main><footer>Original BlackPort work remains credited upstream. Fork-specific changes are marked MayheM-Sec Added.</footer>
<script>
const el=id=>document.getElementById(id);let lastText="";
async function api(path,body){const r=await fetch(path,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined});const d=await r.json();if(!r.ok)throw new Error(d.error||"Request failed");return d}
function syncMode(){const m=el("mode").value;el("tcpBox").classList.toggle("hidden",m==="udp");el("udpBox").classList.toggle("hidden",!(m==="udp"||m==="mixed"))}
async function startScan(){try{await api("/api/scan",{target:el("target").value.trim(),mode:el("mode").value,tcp_profile:el("tcpProfile").value,udp_profile:el("udpProfile").value,udp_timeout:Number(el("udpTimeout").value),udp_retries:Number(el("udpRetries").value)});await refresh()}catch(e){alert(e.message)}}
async function stopScan(){try{await api("/api/stop",{});await refresh()}catch(e){alert(e.message)}}
async function shutdownApp(){if(!confirm("Stop any active scan and shut down BlackPort?"))return;try{await api("/api/shutdown",{});document.body.innerHTML='<main><div class="panel"><h2>BlackPort stopped</h2><p>The local listener is closed. You can close this tab.</p></div></main>'}catch(e){}}
async function refresh(){try{const s=await api("/api/status");el("scan").disabled=s.running;el("stop").disabled=!s.running;el("runState").textContent=s.running?"RUNNING":(s.return_code===0?"COMPLETE":(s.return_code===null?"IDLE":"STOPPED"));el("summary").textContent=s.running?"Scan in progress…":(s.started_at?"Last scan finished.":"No scan running.");const text=(s.output||[]).join("\n")||"BlackPort is ready.";if(text!==lastText){const c=el("console");c.textContent=text;c.classList.toggle("empty",!(s.output||[]).length);c.scrollTop=c.scrollHeight;lastText=text}if(!s.running)loadHistory()}catch(e){el("runState").textContent="OFFLINE"}}
function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]))}
async function loadHistory(){try{const d=await api("/api/reports");const h=el("history");if(!d.reports.length){h.textContent="No reports yet.";return}h.innerHTML=d.reports.slice(0,12).map(r=>`<div class="report"><div><strong>${esc(r.target||r.name)}</strong><small>${esc(r.protocol.toUpperCase())} · ${r.findings} findings · ${new Date(r.modified*1000).toLocaleString()}</small></div><button onclick='openReport(${JSON.stringify(r.name)})'>Open</button></div>`).join("")}catch(e){el("history").textContent="Unable to load reports."}}
async function openReport(name){try{const d=await api("/api/report?name="+encodeURIComponent(name));el("reportTitle").textContent=name;el("viewer").textContent=JSON.stringify(d.report,null,2)}catch(e){alert(e.message)}}
setInterval(refresh,1000);syncMode();refresh();loadHistory();
</script></body></html>"""


class Handler(BaseHandler):
    """MayheM-Sec Added: v3 routes for scan history and local report viewing."""

    server_version = "BlackPortGUI/3.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/reports":
            self._json({"reports": list_reports(REPORT_DIR, limit=50)})
            return
        if path == "/api/report":
            name = (parse_qs(parsed.query).get("name") or [""])[0]
            try:
                self._json({"report": load_report(REPORT_DIR, name)})
            except (FileNotFoundError, json.JSONDecodeError):
                self._json({"error": "Report not found or invalid"}, 404)
            return
        super().do_GET()


def run_gui(port: int = DEFAULT_PORT, open_browser: bool = True) -> None:
    server = ThreadingHTTPServer((HOST, port), Handler)
    server.daemon_threads = True
    url = f"http://{HOST}:{port}"
    print(f"[MayheM-Sec Added] BlackPort GUI v3: {url}")
    print("[MayheM-Sec Added] Localhost only. Closing BlackPort stops the active scan tree and listener.")
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
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("--port must be between 1024 and 65535")
    run_gui(args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
