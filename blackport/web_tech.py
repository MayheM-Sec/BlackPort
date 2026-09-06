"""
MayheM-Sec Added

Passive web technology detection for BlackPort.

Uses ordinary HTTP(S) requests and response metadata only. It does not attempt
credentials, exploit endpoints, or destructive actions.
"""

from __future__ import annotations

import re
from typing import Any

import requests


BODY_PATTERNS = {
    "WordPress": [r"wp-content/", r"wp-includes/"],
    "Drupal": [r"drupal-settings-json", r"/sites/default/files/"],
    "Joomla": [r"/media/system/js/", r"option=com_"],
    "React": [r"data-reactroot", r"__REACT_DEVTOOLS_GLOBAL_HOOK__"],
    "Vue.js": [r"data-v-([a-f0-9]{6,})", r"__VUE__"],
    "Angular": [r"ng-version=", r"<app-root"],
    "Next.js": [r"/_next/", r"__NEXT_DATA__"],
    "Nuxt": [r"/_nuxt/", r"__NUXT__"],
    "Laravel": [r"laravel_session", r"csrf-token"],
    "Django": [r"csrfmiddlewaretoken", r"django"],
}

HEADER_HINTS = {
    "x-powered-by": {
        "php": "PHP",
        "express": "Express",
        "asp.net": "ASP.NET",
    },
    "server": {
        "nginx": "nginx",
        "apache": "Apache HTTP Server",
        "microsoft-iis": "Microsoft IIS",
        "cloudflare": "Cloudflare",
        "caddy": "Caddy",
        "gunicorn": "Gunicorn",
        "uvicorn": "Uvicorn",
    },
}


def _title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()[:200] or None


def detect_from_response(headers: dict[str, str], body: str) -> dict[str, Any]:
    """MayheM-Sec Added: infer technologies from one HTTP response."""
    technologies: set[str] = set()
    normalized = {str(k).lower(): str(v) for k, v in headers.items()}

    for header, hints in HEADER_HINTS.items():
        value = normalized.get(header, "").lower()
        for needle, label in hints.items():
            if needle in value:
                technologies.add(label)

    cookie = normalized.get("set-cookie", "").lower()
    if "phpsessid" in cookie:
        technologies.add("PHP")
    if "laravel_session" in cookie:
        technologies.add("Laravel")
    if "csrftoken" in cookie:
        technologies.add("Django")

    sample = body[:500_000]
    for label, patterns in BODY_PATTERNS.items():
        if any(re.search(pattern, sample, flags=re.I) for pattern in patterns):
            technologies.add(label)

    return {
        "technologies": sorted(technologies),
        "server": headers.get("Server") or headers.get("server"),
        "powered_by": headers.get("X-Powered-By") or headers.get("x-powered-by"),
        "title": _title(body),
    }


def probe_web_tech(target: str, port: int, use_tls: bool = False, timeout: float = 3.0) -> dict | None:
    """MayheM-Sec Added: perform one ordinary GET request for passive fingerprinting."""
    scheme = "https" if use_tls else "http"
    default = (scheme == "https" and port == 443) or (scheme == "http" and port == 80)
    host = target
    if ":" in target and not target.startswith("["):
        host = f"[{target}]"
    url = f"{scheme}://{host}{'' if default else ':' + str(port)}/"

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            verify=False,
            headers={"User-Agent": "BlackPort-MayheM-Sec/1.0"},
        )
        details = detect_from_response(dict(response.headers), response.text)
        details.update({
            "url": response.url,
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
        })
        return details
    except requests.RequestException:
        return None
