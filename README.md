<div align="center">

<img src="https://raw.githubusercontent.com/jsquaresec/jsquaresec/main/assets/j2sec-approved-banner.webp" alt="J2SEC approved banner" width="100%" />

<br>

<img src="https://raw.githubusercontent.com/jsquaresec/jsquaresec/main/assets/j2sec-approved-profile.webp" alt="J2SEC approved profile artwork" width="480" />

</div>

# BlackPort

BlackPort is a network security scanner for authorized assessment work. It combines port discovery, service fingerprinting, vulnerability correlation, verification plugins, reporting, UDP support, and a local browser-based GUI.

> Use BlackPort only on systems and networks you own or have explicit permission to test.

## J2SEC Fork

This repository is maintained by **Joshua Jones / J2SEC** as a fork of the original BlackPort project by Matthew Valdez (`mkingv92`). Upstream attribution remains intact.

The fork extends the original scanner with:

- local browser-based GUI bound to `127.0.0.1`
- TCP connect, SYN, UDP, and mixed scan modes
- Safe, Verify, and Aggressive assessment profiles
- dedicated UDP scanner with conservative state handling
- UDP Top 25, Top 50, Top 100, and full-range profiles
- protocol-aware UDP probes for common services
- local scan history and JSON report viewing
- CISA Known Exploited Vulnerabilities correlation
- FIRST EPSS lookups with local caching
- additional confidence and risk scoring
- TLS posture interpretation
- passive web-technology hints
- enriched report sidecars that preserve upstream JSON output

## Local GUI

The GUI runs entirely on the local machine and does not require a VPS.

```bash
python gui.py
```

Default interface:

```text
http://127.0.0.1:8787
```

Use another local port:

```bash
python gui.py --port 9000
```

Start without automatically opening a browser:

```bash
python gui.py --no-browser
```

## Scan Modes

### TCP

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --tcp-profile top-100
```

### SYN

```bash
sudo python mayhem_scan.py 192.168.1.10 --mode syn --tcp-profile top-100
```

### UDP

```bash
python mayhem_scan.py 192.168.1.10 --mode udp --udp-profile top-50
```

### Mixed

```bash
python mayhem_scan.py 192.168.1.10 --mode mixed --tcp-profile top-100 --udp-profile top-25
```

> Some internal filenames still retain legacy names for compatibility. Branding and public-facing documentation now use **J2SEC**.

## Assessment Profiles

### Safe

Default profile. Keeps TCP/SYN discovery and fingerprinting while disabling active verification plugins and SMB post-sweep enumeration.

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --assessment-profile safe
```

### Verify

Enables only reviewed non-destructive verification plugins.

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --assessment-profile verify
```

### Aggressive

Preserves upstream active verification behavior. Use only where the assessment scope explicitly permits active verification.

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --assessment-profile aggressive
```

## UDP Scanning

The UDP engine supports:

- `open`, `closed`, and `open|filtered` states
- retries and configurable timeouts
- worker-count controls
- common service naming
- persistent JSON reports
- Top 25 / Top 50 / Top 100 / full-range profiles
- protocol-aware probes for DNS, NTP, SSDP/UPnP, mDNS, LLMNR, and Memcached

Examples:

```bash
python udp_scanner.py 192.168.1.10 --top-25
python udp_scanner.py 192.168.1.10 --top-50
python udp_scanner.py 192.168.1.10 --top-100
python udp_scanner.py 192.168.1.10 --full
```

A lack of response is not treated as proof that a UDP port is open; silent ports remain `open|filtered` unless stronger evidence is available.

## Threat Intelligence

Successful TCP/SYN scans can be enriched with:

- CISA KEV status
- FIRST EPSS score and percentile
- local threat-intelligence caching
- confidence scoring
- 0-10 risk scoring
- TLS posture findings
- passive web-technology hints

Disable enrichment with:

```bash
python mayhem_scan.py 192.168.1.10 --mode tcp --no-intel
```

## Installation

Requirements:

- Python 3.8+
- elevated privileges for raw SYN scanning
- Linux, Windows, or macOS subject to platform networking restrictions

Create a virtual environment:

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

## Upstream CLI

The original TCP/SYN path remains available:

```bash
python main.py 192.168.1.10 --top-100
python main.py 192.168.1.10 --top-500
python main.py 192.168.1.10 --top-1000
python main.py 192.168.1.10 --full
sudo python main.py 192.168.1.10 --top-100 --syn
```

## Development Status

This fork is under active development. Treat new functionality as development-stage until the final end-to-end validation pass is complete.

## Attribution

BlackPort was originally created by **Matthew Valdez** (`mkingv92`). This fork preserves upstream attribution and separates fork-specific changes where practical.

## Links

[![GitHub](https://img.shields.io/badge/GitHub-jsquaresec-111111?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jsquaresec)
[![Certifications](https://img.shields.io/badge/Verified-Credentials-168BFF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://jsquaresec.github.io/jsquaresec/certifications/)
[![X](https://img.shields.io/badge/X-@j2__sec-111111?style=for-the-badge&logo=x&logoColor=white)](https://x.com/j2_sec?s=11)
[![OTD Studios](https://img.shields.io/badge/Discord-OTD%20Studios-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/nz5jE7PVh7)
[![Evolution Gaming](https://img.shields.io/badge/Discord-Evolution%20Gaming-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/rjf9ZYMARN)
[![Website](https://img.shields.io/badge/Web-onlythedemons.com-168BFF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://onlythedemons.com)

## Certifications & Badges

### Google Cloud

#### Build Infrastructure with Terraform on Google Cloud
**Google Cloud** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/02751b0c-9c07-4a42-91e8-6a54c3a0192b/public_url)

#### Implement DevOps Workflows in Google Cloud
**Google Cloud** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/0f9979bc-d59f-4d16-a80b-356838a44834/public_url)

#### Build a Secure Google Cloud Network
**Google Cloud** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/087862e0-45ad-40e5-acab-1af9485822d5/public_url)

#### Implement Cloud Security Fundamentals on Google Cloud
**Google Cloud** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/3a3a7799-7310-4c39-9ff6-879ae89dd610/public_url)

### Amazon Web Services (AWS)

#### AWS Application Networking Demonstrated
**Amazon Web Services (AWS)** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/46477737-7d9e-41e7-b23b-76c5a598169e/public_url)

#### AWS Incident Response Demonstrated
**Amazon Web Services (AWS)** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/fcfbca6c-7cc7-4de2-9704-a1bdf9d7ed4b/public_url)

### Cisco

#### Ethical Hacking
**Cisco** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/cc6f57d0-015b-40d1-ad02-2afb4c1a37ac/public_url)

#### Cisco Networking
**Cisco** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/5f247425-d38a-4497-bbb6-126668af27fc/public_url)

#### Python Coding 1
**Cisco** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/6b3e909b-45d8-44f4-8a31-c878bcbd7495/public_url)

#### Python Coding 2
**Cisco** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/5c1f2234-ae0a-45de-af49-677dce570e23/public_url)

### AttackIQ

#### Operationalizing MITRE ATT&CK v19
**AttackIQ** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/95934f21-c54a-4a14-9045-d325fc2e6f2f/public_url)

#### Breach & Attack Simulation
**AttackIQ** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/de4fae36-1f0a-4fad-bd2f-82c23f3fb135/public_url)

#### Foundations of Purple Teaming
**AttackIQ** • Issued September 2026  
[![Verify on Credly](https://img.shields.io/badge/Verify-Credly-168BFF?style=for-the-badge&logo=credly&logoColor=white)](https://www.credly.com/badges/7e67c167-c9f0-42a4-a97a-31d6a2de57ad/public_url)

### Hack The Box

#### That Was A SOCer
**Hack The Box** • September 2026  
[![View Achievement](https://img.shields.io/badge/View-Hack%20The%20Box%20Achievement-9FEF00?style=for-the-badge&logo=hackthebox&logoColor=111111)](https://labs.hackthebox.com/achievement/badge/3945090/243)

#### Investigator In The Making
**Hack The Box** • September 2026  
[![View Achievement](https://img.shields.io/badge/View-Hack%20The%20Box%20Achievement-9FEF00?style=for-the-badge&logo=hackthebox&logoColor=111111)](https://labs.hackthebox.com/achievement/badge/3945090/242)

### Other Credentials

#### Introduction to Cyber Security: Stay Safe Online
**The Open University / OpenLearn** • Issued September 2026  
[![Verify Credential](https://img.shields.io/badge/Verify-Credential-168BFF?style=for-the-badge&logo=openbadges&logoColor=white)](https://www.open.edu/openlearn/badges/badge.php?hash=3f3aaed522c2cc2d8d04c733dabbdee7f154f51e)

## Responsible Use

BlackPort is intended for legitimate administration, lab work, and authorized security assessment. Network scanning and active verification can affect remote systems and may be restricted by law, policy, contracts, or provider terms.

Do not use BlackPort against systems you are not authorized to assess.
