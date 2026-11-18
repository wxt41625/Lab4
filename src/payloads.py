"""Payloads YANG para los cuatro recursos exigidos en U4ACT04."""

NATIVE = "Cisco-IOS-XE-native:native"


def build_items(cfg):
    """Genera ruta RESTCONF y cuerpo JSON según configuración deseada."""
    lb = cfg["loopback"]
    snmp = cfg["snmp"]
    return [
        (
            f"{NATIVE}/interface/Loopback={lb['id']}",
            {
                "Cisco-IOS-XE-native:Loopback": [{
                    "name": lb["id"],
                    "description": lb["description"],
                    "ip": {
                        "address": {
                            "primary": {"address": lb["ip"], "mask": lb["mask"]}
                        }
                    },
                }]
            },
        ),
        (
            f"{NATIVE}/snmp-server/Cisco-IOS-XE-snmp:community={snmp['community']}",
            {
                "Cisco-IOS-XE-snmp:community": [{
                    "name": snmp["community"],
                    "RO": [None],
                }]
            },
        ),
        (
            f"{NATIVE}/snmp-server/Cisco-IOS-XE-snmp:location",
            {"Cisco-IOS-XE-snmp:location": snmp["location"]},
        ),
        (
            f"{NATIVE}/snmp-server/Cisco-IOS-XE-snmp:contact",
            {"Cisco-IOS-XE-snmp:contact": snmp["contact"]},
        ),
    ]


def is_subset(desired, current):
    """Compara recursivamente los campos configurados sin exigir igualdad de extras.

    En las respuestas de IOS-XE la clave raíz puede incluir o no un prefijo YANG.
    El modelo ya conocido fija qué campos buscamos y comparamos.
    """
    if isinstance(desired, dict) and isinstance(current, list) and len(current) == 1:
        current = current[0]
    if isinstance(desired, list) and isinstance(current, dict) and len(desired) == 1:
        current = [current]
    if isinstance(desired, dict):
        if not isinstance(current, dict):
            return False
        for name, value in desired.items():
            if name in current:
                found = current[name]
            else:
                matches = [v for k, v in current.items() if k.split(":")[-1] == name.split(":")[-1]]
                if len(matches) != 1:
                    return False
                found = matches[0]
            if not is_subset(value, found):
                return False
        return True
    if isinstance(desired, list):
        return (
            isinstance(current, list)
            and len(desired) == len(current)
            and all(is_subset(a, b) for a, b in zip(desired, current))
        )
    return desired == current
