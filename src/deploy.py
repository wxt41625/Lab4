"""GET antes de PUT para idempotencia. --check nunca modifica el equipo."""

import argparse
import sys

import yaml

from payloads import build_items, is_subset
from restconf_client import RestconfClient


def main(argv=None, client_factory=RestconfClient):
    parser = argparse.ArgumentParser(description="DevOps RESTCONF - Irvin")
    parser.add_argument("--config", default="config/vars.yml")
    parser.add_argument("--check", action="store_true", help="solo consulta y compara")
    args = parser.parse_args(argv)
    with open(args.config, encoding="utf-8") as stream:
        cfg = yaml.safe_load(stream)
    client = client_factory(cfg["host"], cfg.get("port", 443))
    changes = 0
    for path, payload in build_items(cfg):
        current = client.get(path)
        if current is not None and is_subset(payload, current):
            print(f"[OK] sin cambios -> {path}")
            continue
        changes += 1
        if args.check:
            print(f"[CAMBIO] se aplicaría -> {path}")
        else:
            status = client.put(path, payload)
            print(f"[APLICADO] HTTP {status} -> {path}")
    print(f"\nResumen: {changes} cambio(s) "
          f"{'pendiente(s)' if args.check else 'aplicado(s)'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, yaml.YAMLError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
