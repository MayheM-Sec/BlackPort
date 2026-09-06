# BlackPort

BlackPort is a network security scanner for authorized assessment work. It combines port discovery, service fingerprinting, vulnerability correlation, verification plugins, and reporting in one Python project.

This repository is the **MayheM-Sec fork** of the original BlackPort project by Matthew Valdez (`mkingv92`). The original project and its author remain credited. Changes introduced by this fork are identified as **MayheM-Sec Added** where practical and are tracked separately in `CHANGELOG_MAYHEM.md`.

> Use BlackPort only on systems and networks you own or have explicit permission to test.

## What this fork adds

The upstream scanner remains the foundation for TCP and SYN assessment. The MayheM-Sec fork adds a dedicated UDP path, a local GUI, explicit assessment policies, and an additional intelligence layer without replacing the original scanner implementation.

Current MayheM-Sec work includes:

- local browser-based GUI bound to `127.0.0.1`
- TCP connect, SYN, UDP, and mixed scan modes
- Safe, Verify, and Aggressive assessment profiles
- dedicated UDP scanner with conservative state handling
- UDP Top 25, Top 50, Top 100, and full-range profiles
- protocol-aware UDP probes for common services
- local scan history and JSON report viewing in the GUI
- CISA Known Exploited Vulnerabilities correlation
- FIRST EPSS lookups with local caching
- separate MayheM-Sec confidence and risk scoring
- TLS posture interpretation from data BlackPort already collects
- passive web-technology hints from existing banners and titles
- enriched `.mayhem.json` report sidecars that leave upstream JSON unchanged

## Local GUI

The GUI runs entirely on the computer where BlackPort is started. It does not require a VPS.

Start it with:

```bash
python gui.py
```

BlackPort opens the interface at:

```text
http://127.0.0.1:8787
```

The listener is bound to localhost only. It is not exposed to the LAN or Internet by default.

The current interface includes:

- target entry for an IP address, hostname, or supported CIDR target
- assessment profile selection
- TCP, SYN, UDP, and mixed modes
- TCP and UDP port presets
- UDP retry and timeout controls
- live scanner output
- scan start and stop controls
- local scan history
- local JSON report viewer
- explicit BlackPort shutdown

Closing BlackPort stops the active scan process group, closes the local HTTP listener, and releases the GUI port. If the browser tab remains open afterward, it will simply lose its connection to the local service.

Use another local port if needed:

```bash
python gui.py --port 9000
```

Start the GUI without opening a browser automatically:

```bash
python gui.py --no-browser
```

## Assessment profiles

The MayheM-Sec scan launcher separates discovery from the level of verification a user authorizes.

### Safe

Safe is the default profile.

It keeps the TCP/SYN discovery and fingerprinting path but disables verification plugins and the SMB post-sweep enumeration phase.

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --assessment-profile safe
```

### Verify

Verify enables only plugins that have been explicitly reviewed as non-destructive in the MayheM-Sec policy layer.

The initial reviewed set is intentionally conservative. It currently includes the Apache and SSH verification plugins.

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --assessment-profile verify
```

### Aggressive

Aggressive preserves the upstream active verification plugin behavior.

Some upstream plugins perform authentication checks, file reads, service interaction, or active exploit verification. Use this profile only when the assessment scope explicitly permits that level of testing.

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --assessment-profile aggressive
```

## UDP scanning

UDP is implemented as its own scanner rather than treating it as a variation of TCP.

The UDP engine provides:

- `open`, `closed`, and `open|filtered` states
- configurable retries
- configurable timeout and worker count
- protocol-aware probes where implemented
- common UDP service naming
- persistent JSON reports
- Top 25, Top 50, Top 100, and full-range profiles

A lack of response is not treated as proof that a UDP port is open. Silent ports are reported as `open|filtered` unless stronger evidence is available.

Protocol-aware probes currently include:

- DNS
- NTP
- SSDP/UPnP
- mDNS
- LLMNR
- Memcached

Examples:

```bash
python udp_scanner.py 192.168.1.10 --top-25
python udp_scanner.py 192.168.1.10 --top-50
python udp_scanner.py 192.168.1.10 --top-100
```

A full UDP scan is explicit because it can take substantially longer:

```bash
python udp_scanner.py 192.168.1.10 --full
```

UDP reports are written to the selected report directory using filenames ending in `_udp.json`.

UDP and mixed modes currently accept a single IP address or hostname. UDP CIDR orchestration is being kept out of the release path until its host-discovery behavior is defined and tested properly.

## Unified MayheM-Sec launcher

`mayhem_scan.py` is the common entry point for fork-specific scan behavior. TCP and SYN still run through the upstream scanner; the wrapper applies the MayheM-Sec assessment policy and handles UDP/mixed orchestration.

TCP:

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --tcp-profile top-100
```

SYN:

```bash
sudo python mayhem_scan.py 192.168.1.10 --mode syn --tcp-profile top-100
```

UDP:

```bash
python mayhem_scan.py 192.168.1.10 --mode udp --udp-profile top-50
```

Mixed TCP and UDP:

```bash
python mayhem_scan.py 192.168.1.10 --mode mixed --tcp-profile top-100 --udp-profile top-25
```

Choose an assessment policy explicitly:

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --assessment-profile verify
```

The GUI uses this same launcher. There is no separate scanner implementation hidden behind the web interface.

## Threat intelligence and prioritization

Successful TCP/SYN scans can be post-processed by the MayheM-Sec enrichment layer.

The enrichment layer adds:

- CISA Known Exploited Vulnerabilities status
- FIRST EPSS score and percentile
- local threat-intelligence caching
- confidence scoring based on collected evidence
- separate MayheM-Sec 0-10 risk scoring
- TLS posture findings
- passive web-technology hints

The original BlackPort JSON report is preserved. Enrichment is written to a separate file ending in `.mayhem.json`.

If an external intelligence source is unavailable, BlackPort continues without treating the lookup failure as a scan failure. Cached data is used when available.

Disable MayheM-Sec intelligence enrichment with:

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --no-intel
```

## TLS analysis

The upstream project already collects certificate, cipher, and TLS-version data for relevant services. The MayheM-Sec layer interprets that existing data rather than repeating the network probe.

Current checks include:

- expired certificates
- certificates nearing expiration
- hostname mismatch
- self-signed certificates
- weak negotiated ciphers
- TLS 1.0 / TLS 1.1 support
- broad downgrade surface where modern and legacy protocol versions coexist

## Web technology hints

MayheM-Sec web analysis is passive. It derives technology hints from banners and HTTP information BlackPort already collected rather than making additional exploit requests.

Current patterns cover common technologies such as:

- nginx
- Apache HTTP Server
- Microsoft IIS
- OpenResty
- Caddy
- PHP
- ASP.NET
- Express
- Cloudflare
- WordPress
- Drupal
- Joomla
- Tomcat
- Jetty
- Werkzeug
- gunicorn

## Installation

### Requirements

- Python 3.8 or newer
- elevated privileges for raw SYN scanning
- Linux, Windows, or macOS subject to platform networking restrictions

A virtual environment is recommended.

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Upstream command-line path

The original TCP/SYN entry point remains available.

Quick TCP scan:

```bash
python main.py 192.168.1.10 --top-100
```

Broader curated scan:

```bash
python main.py 192.168.1.10 --top-500
```

Ports 1-1000:

```bash
python main.py 192.168.1.10 --top-1000
```

Full TCP range:

```bash
python main.py 192.168.1.10 --full
```

Custom range:

```bash
python main.py 192.168.1.10 1 1024
```

SYN scan:

```bash
sudo python main.py 192.168.1.10 --top-100 --syn
```

CIDR scan:

```bash
python main.py 192.168.1.0/24 --top-100
```

Choose a report directory:

```bash
python main.py 192.168.1.10 --top-100 --output-dir ./reports
```

Generate PDF output:

```bash
python main.py 192.168.1.10 --top-100 --pdf
```

## Project structure

The fork keeps MayheM-Sec orchestration separate from the upstream scanner where possible.

```text
BlackPort/
├── main.py                         upstream TCP/SYN entry point
├── unified_scanner.py              upstream SYN/TCP discovery
├── plugins/                        upstream verification plugins
├── blackport/                      upstream core plus fork helper modules
│   ├── threat_intel.py             MayheM-Sec Added
│   ├── risk_engine_v2.py           MayheM-Sec Added
│   ├── tls_analysis.py             MayheM-Sec Added
│   ├── web_analysis.py             MayheM-Sec Added
│   └── report_index.py             MayheM-Sec Added
├── udp_scanner.py                  MayheM-Sec Added
├── assessment_runner.py            MayheM-Sec Added
├── mayhem_scan.py                  MayheM-Sec Added
├── report_enricher.py              MayheM-Sec Added
├── gui.py                          MayheM-Sec Added launcher
├── gui_server_v4.py                MayheM-Sec Added current GUI layer
└── CHANGELOG_MAYHEM.md             fork change history
```

The scan flow is intentionally straightforward:

1. Discovery
2. Fingerprinting
3. Policy-controlled verification
4. CVE and threat-intelligence correlation
5. Risk/confidence prioritization
6. Reporting and local history

## Attribution convention

Fork-specific changes use comments such as:

```python
# MayheM-Sec Added: description of the change
```

Larger MayheM-Sec files use a short header at the beginning of the file. Original upstream code is not relabeled as MayheM-Sec work.

## Contributing changes upstream

MayheM-Sec changes can be proposed to the original BlackPort repository through normal GitHub pull requests. The fork remains independent whether or not an upstream contribution is accepted.

Focused pull requests are preferred. UDP support, GUI work, assessment policy, and intelligence improvements should be reviewable independently rather than submitted as one unrelated bundle.

## Upstream project and attribution

BlackPort was originally created by **Matthew Valdez** (`mkingv92`). This fork does not remove or replace that attribution.

MayheM-Sec maintains this fork and documents its additions separately so users can distinguish upstream work from fork-specific changes.

## License

The upstream project identifies itself as MIT licensed. Review the repository license and upstream terms before redistributing modified builds.

## Development status

The current MayheM-Sec changes are being developed on the work path and have not yet received the final end-to-end test pass. They should not be treated as a release until that validation is complete.

## Responsible use

BlackPort is intended for legitimate administration, lab work, and authorized security assessment. Network scanning and active verification can affect remote systems and may be restricted by law, policy, contracts, or provider terms.

Do not use BlackPort against systems you are not authorized to assess.
