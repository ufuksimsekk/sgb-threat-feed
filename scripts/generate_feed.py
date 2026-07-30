"""Build a FortiGate-compatible IPv4 threat feed from the SGB API."""

from __future__ import annotations

import ipaddress
import logging
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://siberguvenlik.gov.tr/api/address/index"
# SGB rates indicators from 1 (lowest) to 10 (highest) criticality.
CRITICALITY_LEVELS = tuple(range(1, 11))
PER_PAGE = 500
MAX_PAGES_PER_LEVEL = 1_000
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "feeds" / "ip.txt"


def create_session() -> requests.Session:
    """Create a session that retries transient service and network failures."""
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def normalize_ipv4(value: object) -> str | None:
    """Return a canonical IPv4 address, ignoring malformed/non-IPv4 values."""
    if not isinstance(value, str):
        return None
    try:
        address = ipaddress.ip_address(value.strip())
    except ValueError:
        return None
    return str(address) if address.version == 4 else None


def fetch_ips(session: requests.Session) -> set[str]:
    ips: set[str] = set()

    for level in CRITICALITY_LEVELS:
        for page in range(MAX_PAGES_PER_LEVEL):
            response = session.get(
                BASE_URL,
                params={
                    "type": "ip",
                    "criticality_level": level,
                    "page": page,
                    "per-page": PER_PAGE,
                },
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            models = payload.get("models", [])

            if not isinstance(models, list):
                raise ValueError("SGB API response has an invalid 'models' field")
            if not models:
                break

            for item in models:
                if isinstance(item, dict):
                    ip = normalize_ipv4(item.get("url"))
                    if ip:
                        ips.add(ip)

            if len(models) < PER_PAGE:
                break
        else:
            raise RuntimeError(f"Pagination limit exceeded for criticality level {level}")

    if not ips:
        raise RuntimeError("SGB API returned no valid IPv4 addresses; feed was not replaced")
    return ips


def write_feed(ips: set[str], output_path: Path = OUTPUT_PATH) -> None:
    """Atomically replace the published list only after a successful fetch."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ordered_ips = sorted(ips, key=lambda value: int(ipaddress.IPv4Address(value)))
    temporary_path = output_path.with_suffix(".txt.tmp")
    temporary_path.write_text("\n".join(ordered_ips) + "\n", encoding="utf-8")
    temporary_path.replace(output_path)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ips = fetch_ips(create_session())
    write_feed(ips)
    logging.info("Published %d unique IPv4 indicators to %s", len(ips), OUTPUT_PATH)


if __name__ == "__main__":
    main()
