#!/usr/bin/env python3
"""Derive the public template from the ignored personal configuration."""

import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HEADER = """# openlcc-template.yaml - generic build without personal/site-specific settings.
# DERIVED FILE: generated from openlcc.yaml by scripts/sync_template.py.
# Only this header, name_add_mac_suffix and wifi.use_address differ.
# Edit openlcc.yaml, then run the script; use --check before committing.
# Review the diff for any new personal settings before publishing.
#
# Per board, provide WiFi credentials and a fresh API key in secrets.yaml.
# The fallback access point also allows WiFi setup without rebuilding.

"""


def render(source: str) -> str:
    # Keep YAML comments/lambdas intact instead of reserializing with a YAML library.
    _, separator, body = source.partition("external_components:\n")
    if not separator:
        raise ValueError("Expected external_components as the first configuration section")
    body = separator + body
    body, suffix_count = re.subn(
        r"^  name_add_mac_suffix: false$", "  name_add_mac_suffix: true", body,
        flags=re.MULTILINE,
    )
    body, address_count = re.subn(r"^  use_address: [^\n]+\n", "", body, flags=re.MULTILINE)
    if suffix_count != 1 or address_count != 1:
        raise ValueError("Personal configuration changed; review the template overrides")
    # Fail closed if the existing credential references are replaced with literal values.
    for reference in ("  ssid: !secret wifi_ssid", "  password: !secret wifi_password",
                      "    key: !secret api_key"):
        if reference not in body.splitlines():
            raise ValueError("Expected WiFi/API !secret references; review before publishing")
    return HEADER + body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args()
    source = ROOT / "openlcc.yaml"
    target = ROOT / "openlcc-template.yaml"
    if not source.exists():
        parser.error("openlcc.yaml is a local, ignored file; run this in the maintainer's checkout")
    try:
        expected = render(source.read_text())
    except ValueError as error:
        parser.error(str(error))
    if args.check:
        if not target.exists() or target.read_text() != expected:
            print("Template differs. Run: python3 scripts/sync_template.py")
            return 1
        print("Template matches openlcc.yaml with the documented personal overrides.")
        return 0
    target.write_text(expected)
    print("Updated openlcc-template.yaml; review the diff before publishing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
