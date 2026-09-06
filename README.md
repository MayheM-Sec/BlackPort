# BlackPort

BlackPort is a network security scanner for authorized assessment work. It combines port discovery, service fingerprinting, vulnerability correlation, active verification plugins, scan comparison, and reporting in a single Python project.

This repository is the **MayheM-Sec fork** of the original BlackPort project by Matthew Valdez (`mkingv92`). Original upstream work remains credited to its author. Fork-specific code and modifications are identified as **MayheM-Sec Added** where practical and are documented separately below.

> Use BlackPort only on systems and networks you own or have explicit permission to test.

## Capabilities

The upstream project provides the core TCP/SYN assessment workflow, including:

- TCP connect scanning
- SYN scanning with TCP fallback
- CIDR/network discovery
- curated and full-range TCP profiles
- service and banner fingerprinting
- OS detection support
- CVE correlation
- plugin-based verification checks
- scan comparison/diff support
- JSON, CSV, HTML, and PDF reports
- multi-host reporting

The MayheM-Sec fork extends that base with a local browser interface, a dedicated UDP engine, mixed TCP/UDP orchestration, and additional vulnerability prioritization.

## MayheM-Sec additions

### Local graphical interface

**MayheM-Sec Added**

BlackPort can run as a local browser application without a VPS or externally hosted service.

```bash
python gui.py
```

The launcher opens:

```text
http://127.0.0.1:8787
```

The server binds only to `127.0.0.1` by default. It is not exposed to the LAN or Internet.

The current interface supports:

- IP address, hostname, or supported CIDR target entry
- TCP connect scanning
- SYN scanning
- UDP scanning
- mixed TCP + UDP scanning
- TCP Top 100, Top 500, Top 1000, and full profiles
- UDP Top 25, Top 50, Top 100, and full profiles
- live scanner output
- scan start/stop controls
- automatic report output to `reports/`
- explicit application shutdown
- child-process cleanup when BlackPort closes

When the GUI is shut down, BlackPort stops an active scan process group, closes the localhost HTTP server, and releases the listening port.

Use another local GUI port with:

```bash
python gui.py --port 9000
```

Start without automatically opening a browser with:

```bash
python gui.py --no-browser
```

### UDP scanning

**MayheM-Sec Added**

UDP is implemented as a separate scanner rather than treating UDP like TCP.

The UDP engine provides:

- conservative `open`, `closed`, and `open|filtered` state handling
- retry support
- configurable timeouts and worker counts
- protocol-aware probes where implemented
- common UDP service naming
- JSON report persistence
- Top 25, Top 50, Top 100, and full-range profiles

Protocol-aware probes currently include DNS, NTP, SSDP/UPnP, mDNS, LLMNR, and Memcached. Other UDP services use a generic discovery probe and are deliberately reported conservatively when no response is returned.

Example:

```bash
python udp_scanner.py 192.168.1.10 --top-25
```

Broader UDP scan:

```bash
python udp_scanner.py 192.168.1.10 --top-100
```

A full UDP scan is explicit because it can take substantially longer:

```bash
python udp_scanner.py 192.168.1.10 --full
```

UDP results are written to the selected report directory using a filename ending in `_udp.json`.

At this stage, UDP and mixed modes accept a single IP address or hostname. CIDR UDP orchestration will be added only after host-discovery behavior is defined and tested for that path.

### Unified MayheM-Sec scan launcher

**MayheM-Sec Added**

`mayhem_scan.py` provides one entry point for the fork-specific scan modes while leaving upstream TCP/SYN implementation in `main.py`.

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

The GUI uses this same launcher so scan behavior is not duplicated in a separate interface-specific scanner.

### Threat intelligence and risk enrichment

**MayheM-Sec Added**

The fork includes an optional post-processing layer for BlackPort JSON reports. It preserves the original upstream report and writes an additional `.mayhem.json` sidecar containing MayheM-Sec fields.

Current enrichment includes:

- CISA Known Exploited Vulnerabilities correlation
- FIRST EPSS lookups
- cached intelligence data
- confidence scoring based on collected evidence
- a separate MayheM-Sec 0-10 risk score

Network failures during intelligence lookup are treated as non-fatal and cached data is used when available.

To skip this enrichment when using the unified launcher:

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --no-intel
```

### Attribution convention

Fork-specific changes use comments such as:

```python
# MayheM-Sec Added: description of the change
```

Larger MayheM-Sec files use a short header at the beginning of the file. Original upstream code is not relabeled as MayheM-Sec work.

## Installation

### Requirements

- Python 3.8 or newer
- elevated privileges for raw SYN scanning
- Linux, Windows, or macOS subject to platform networking restrictions

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

A virtual environment is recommended:

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

## Upstream command-line usage

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

SYN scanning generally requires raw packet privileges:

```bash
sudo python main.py 192.168.1.10 --top-100 --syn
```

Network scan:

```bash
python main.py 192.168.1.0/24 --top-100
```

Choose a report directory:

```bash
python main.py 192.168.1.10 --top-100 --output-dir ./reports
```

Generate PDF output as well:

```bash
python main.py 192.168.1.10 --top-100 --pdf
```

## Architecture

BlackPort is being kept modular so the CLI and GUI use the same scanner paths.

```text
BlackPort
├── Upstream TCP/SYN path
│   ├── main.py
│   ├── unified_scanner.py
│   └── blackport/
│
└── MayheM-Sec extensions
    ├── gui.py
    ├── gui_server.py
    ├── mayhem_scan.py
    ├── udp_scanner.py
    ├── report_enricher.py
    ├── blackport/threat_intel.py
    └── blackport/risk_engine_v2.py
```

The intended scan flow is:

1. **Discovery** — TCP connect, SYN, UDP, or mixed scanning.
2. **Fingerprinting** — service and banner identification where applicable.
3. **Verification** — service-specific checks from the upstream plugin system.
4. **Intelligence** — CVE correlation plus MayheM-Sec KEV/EPSS enrichment.
5. **Prioritization** — upstream risk is preserved and MayheM-Sec risk/confidence is added separately.
6. **Reporting** — upstream reports remain intact while fork-specific sidecars and UDP reports are stored separately.

## Development direction

Planned work for the MayheM-Sec fork includes:

- additional protocol-aware UDP probes
- UDP CIDR orchestration after host discovery is defined
- stronger TLS analysis
- expanded HTTP/web technology fingerprinting
- improved service fingerprint confidence
- scan history and change tracking in the GUI
- richer GUI result views beyond console output
- plugin metadata and management
- continued separation between detection and active verification

Features are being added in focused stages so each path can be tested independently before release.

## Contributing changes upstream

MayheM-Sec changes can be proposed to the original BlackPort project through GitHub pull requests. The fork remains independent whether or not an upstream contribution is accepted.

Focused pull requests are preferred for major features such as UDP support, GUI work, or vulnerability-intelligence improvements rather than combining unrelated changes into one review.

## Upstream project and attribution

BlackPort was originally created by **Matthew Valdez** (`mkingv92`). This fork does not remove or replace that attribution.

MayheM-Sec maintains this fork and documents its additions separately so users can distinguish upstream functionality from fork-specific work.

## License

The upstream project identifies itself as MIT licensed. Review the repository license and upstream terms before redistributing modified builds.

## Responsible use

BlackPort is intended for legitimate administration, lab work, and authorized security assessment. Network scanning and vulnerability verification can affect remote systems and may be restricted by law, policy, contracts, or provider terms.

Do not use BlackPort against systems you are not authorized to assess.
