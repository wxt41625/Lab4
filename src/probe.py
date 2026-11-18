"""Diagnóstico read-only: prueba RESTCONF, hostname, Loopback y SNMP."""

import sys

import yaml

from restconf_client import RestconfClient


PATHS = [
    "Cisco-IOS-XE-native:native/hostname",
    "Cisco-IOS-XE-native:native/interface",
    "Cisco-IOS-XE-native:native/snmp-server",
]


def main():
    with open("config/vars.yml", encoding="utf-8") as stream:
        cfg = yaml.safe_load(stream)
    client = RestconfClient(cfg["host"], cfg.get("port", 443))
    print(f"Probando RESTCONF del Catalyst {cfg['host']}:{cfg.get('port', 443)}")
    for path in PATHS:
        result = client.get(path)
        print(f"[{'OK' if result is not None else '404'}] {path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, yaml.YAMLError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
