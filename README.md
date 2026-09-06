# BlackPort

BlackPort is a network security scanner built for authorized assessment work. It combines port discovery, service fingerprinting, vulnerability correlation, active verification plugins, and report generation in one Python project.

This repository is the **MayheM-Sec fork** of the original BlackPort project by Matthew Valdez (`mkingv92`). Upstream work remains credited to the original author. Features and code introduced in this fork are marked **MayheM-Sec Added** in the source where practical and are documented separately below.

> Use BlackPort only on systems and networks you own or have explicit permission to test.

## Current capabilities

BlackPort currently includes:

- TCP connect scanning
- SYN scanning with automatic TCP fallback
- CIDR/network scanning and host discovery
- Curated port profiles and full-range scanning
- Service and banner fingerprinting
- OS detection support
- CVE correlation and local vulnerability data
- Plugin-based service checks and active verification
- Scan comparison/diff support
- JSON, CSV, HTML, and PDF reporting
- Multi-host reporting
- Local graphical interface in the MayheM-Sec fork

## MayheM-Sec additions

### Local graphical interface

**MayheM-Sec Added**

The fork includes a local browser-based interface for starting and monitoring BlackPort scans without hosting anything on a VPS.

Start it with:

```bash
python gui.py
```

or directly:

```bash
python gui_server.py
```

BlackPort opens the interface locally at:

```text
http://127.0.0.1:8787
```

The GUI binds to `127.0.0.1` only. It is not exposed to the local network or Internet by default.

The current interface provides:

- target entry for an IP address, hostname, or CIDR range
- Top 100, Top 500, Top 1000, and full scan profiles
- TCP connect and SYN scan modes
- live BlackPort console output
- scan start/stop controls
- automatic report output to the local `reports/` directory
- explicit BlackPort shutdown control
- automatic cleanup of an active child scan when the GUI exits

To use another local port:

```bash
python gui.py --port 9000
```

To start the server without opening a browser automatically:

```bash
python gui.py --no-browser
```

When BlackPort is shut down, the local HTTP listener is closed and the port is released. If a scan is still active, the GUI attempts to stop that child process before exiting.

### Attribution convention

Changes made specifically for this fork use comments such as:

```python
# MayheM-Sec Added: description of the change
```

Larger MayheM-Sec files and features use a short header identifying the addition. Original upstream code is not relabeled as MayheM-Sec work.

## Installation

### Requirements

- Python 3.8 or newer
- elevated privileges for raw SYN scanning
- supported on Linux, Windows, and macOS, subject to platform-specific networking restrictions

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

For best isolation, use a virtual environment:

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

## Command-line usage

### Quick scan

```bash
python main.py 192.168.1.10 --top-100
```

### Broader curated scan

```bash
python main.py 192.168.1.10 --top-500
```

### Ports 1-1000

```bash
python main.py 192.168.1.10 --top-1000
```

### Full TCP port range

```bash
python main.py 192.168.1.10 --full
```

### Custom range

```bash
python main.py 192.168.1.10 1 1024
```

### SYN scan

SYN scanning requires raw packet privileges on most systems.

```bash
sudo python main.py 192.168.1.10 --top-100 --syn
```

If SYN scanning cannot be used, BlackPort can fall back to TCP connect scanning.

### Network scan

```bash
python main.py 192.168.1.0/24 --top-100
```

### Reports

Choose an output directory:

```bash
python main.py 192.168.1.10 --top-100 --output-dir ./reports
```

Generate PDF output as well:

```bash
python main.py 192.168.1.10 --top-100 --pdf
```

## Scan architecture

BlackPort separates the assessment into several stages:

1. **Discovery** — identifies reachable/open ports using TCP connect or SYN scanning.
2. **Fingerprinting** — collects service and banner information from discovered services.
3. **Verification** — runs applicable service plugins and validation checks.
4. **Intelligence** — correlates service information with vulnerability data.
5. **Reporting** — produces structured and human-readable scan results.

The MayheM-Sec GUI does not contain a second scanner implementation. It launches the existing BlackPort scanner entry point so command-line and GUI scans stay aligned.

## Project layout

```text
BlackPort/
├── main.py                 Main command-line scanner entry point
├── gui.py                  MayheM-Sec local GUI launcher
├── gui_server.py           MayheM-Sec local browser interface
├── unified_scanner.py      SYN/TCP scanning support
├── syn_scanner.py          SYN scanning engine
├── blackport/              Core scanner, intelligence, logging, and reporting modules
├── plugins/                Service-specific verification plugins
├── cve_db.py               Vulnerability data support
├── html_report.py          HTML reporting
├── pdf_report.py           PDF reporting
└── requirements.txt        Python dependencies
```

## UDP support

UDP is an area targeted for expansion in the MayheM-Sec fork. It is intentionally not presented as complete in this README yet.

The planned implementation is a first-class UDP engine rather than a simple empty-datagram sweep. The design will include protocol-aware probes, UDP-specific state handling (`open`, `closed`, `open|filtered`, `filtered`), retries, adaptive timeouts, and service modules for common protocols such as DNS, NTP, SNMP, IKE/IPsec, SSDP, mDNS, TFTP, and IPMI.

When UDP support is implemented, the affected source will be identified as **MayheM-Sec Added**.

## Development direction

The MayheM-Sec fork is being developed around a few specific goals:

- stronger UDP coverage
- a dedicated local GUI
- clearer separation between detection and active verification
- improved service fingerprinting
- better vulnerability intelligence and prioritization
- scan confidence and risk scoring improvements
- cleaner scan history and comparison workflows
- professional reporting without changing upstream attribution

Features are added incrementally so the scanner remains testable and understandable as it grows.

## Contributing changes upstream

Because this repository is a fork, MayheM-Sec changes can be proposed back to the original BlackPort project through a GitHub pull request. The fork remains available independently whether or not an upstream contribution is accepted.

For larger changes, focused pull requests are preferred over one large combined patch. Examples include a GUI contribution, a UDP engine contribution, or a vulnerability-intelligence improvement as separate reviews.

## Upstream project and attribution

BlackPort was originally created by **Matthew Valdez** (`mkingv92`). This fork does not remove or replace that attribution.

MayheM-Sec maintains this fork and documents its own additions separately so users can distinguish upstream functionality from fork-specific work.

## License

The upstream project identifies itself as MIT licensed. Review the repository's license file and upstream project terms before redistributing modified builds.

## Responsible use

BlackPort is intended for legitimate security testing, lab work, administration, and authorized assessment. Network scanning and vulnerability verification can affect remote systems and may be restricted by law, policy, contracts, or provider terms.

Do not use BlackPort against systems you are not authorized to assess.
