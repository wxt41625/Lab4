"""MONITOR: compara el switch con las cuatro configuraciones deseadas."""

import sys

import yaml

from payloads import build_items, is_subset
from restconf_client import RestconfClient


def main():
    with open("config/vars.yml", encoding="utf-8") as stream:
        cfg = yaml.safe_load(stream)
    client = RestconfClient(cfg["host"], cfg.get("port", 443))
    failures = 0
    for path, payload in build_items(cfg):
        current = client.get(path)
        ok = current is not None and is_subset(payload, current)
        print(f"[{'PASS' if ok else 'FAIL'}] {path}")
        failures += not ok
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, yaml.YAMLError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
