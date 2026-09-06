# MayheM-Sec BlackPort Changelog

This file tracks changes introduced by the MayheM-Sec fork. It does not replace upstream BlackPort history or attribution.

## Unreleased

### Added

- **MayheM-Sec Added:** local browser-based BlackPort GUI bound to `127.0.0.1` by default.
- **MayheM-Sec Added:** GUI start, stop, and application shutdown controls.
- **MayheM-Sec Added:** process-group cleanup so closing the GUI also terminates active scan children.
- **MayheM-Sec Added:** dedicated UDP scanner with conservative UDP state handling.
- **MayheM-Sec Added:** UDP Top 25, Top 50, Top 100, and full-range profiles.
- **MayheM-Sec Added:** protocol-aware UDP probes for DNS, NTP, SSDP/UPnP, mDNS, LLMNR, and Memcached.
- **MayheM-Sec Added:** UDP JSON report persistence.
- **MayheM-Sec Added:** unified `mayhem_scan.py` launcher for TCP, SYN, UDP, and mixed modes.
- **MayheM-Sec Added:** CISA KEV and FIRST EPSS enrichment with local caching.
- **MayheM-Sec Added:** confidence and second-generation MayheM-Sec risk scoring while preserving upstream risk fields.
- **MayheM-Sec Added:** enriched `.mayhem.json` sidecar reports so upstream JSON remains unchanged.
- **MayheM-Sec Added:** TLS posture analysis for expiry, hostname mismatch, self-signed certificates, weak ciphers, and legacy protocol support.

### Changed

- **MayheM-Sec Added:** replaced the legacy `FastScan Pro` Tkinter launcher with a compatibility entry point for the local BlackPort browser interface.
- **MayheM-Sec Added:** rewrote the fork README to clearly separate upstream functionality from MayheM-Sec additions and remove overly promotional wording.

### Known limitations before release testing

- UDP and mixed modes currently target a single IP address or hostname; UDP CIDR orchestration is not enabled yet.
- UDP silence is intentionally classified as `open|filtered`, not as a confirmed open port.
- Full UDP scans are expected to take substantially longer than curated UDP profiles.
- The GUI currently focuses on scan configuration and live output; richer report/history views remain planned.

## Attribution

Original BlackPort work remains attributed to Matthew Valdez (`mkingv92`). Only fork-specific additions or modifications are labeled **MayheM-Sec Added**.
