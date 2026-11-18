"""Pruebas sin conexión al switch ni uso de secretos."""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deploy import main as deploy_main  # noqa: E402
from payloads import build_items, is_subset  # noqa: E402


with open(ROOT / "config" / "vars.yml", encoding="utf-8") as stream:
    CFG = yaml.safe_load(stream)


def test_cuatro_recursos():
    assert len(build_items(CFG)) == 4


def test_loopback_ip():
    path, body = build_items(CFG)[0]
    assert f"Loopback={CFG['loopback']['id']}" in path
    loopback = body["Cisco-IOS-XE-native:Loopback"][0]
    assert loopback["description"] == CFG["loopback"]["description"]
    assert loopback["ip"]["address"]["primary"]["address"] == CFG["loopback"]["ip"]
    assert loopback["ip"]["address"]["primary"]["mask"] == CFG["loopback"]["mask"]


def test_snmp_ro():
    path, body = build_items(CFG)[1]
    assert "snmp-server" in path
    assert body["Cisco-IOS-XE-snmp:community"][0]["RO"] == [None]


def test_is_subset_extra_fields():
    assert is_subset({"a": 1}, {"a": 1, "b": 2})
    assert not is_subset({"a": 1}, {"a": 2})


def test_is_subset_single_list_item_get():
    desired = {"Cisco-IOS-XE-native:Loopback": [{"name": 201}]}
    actual = {"Cisco-IOS-XE-native:Loopback": {"name": 201, "description": "X"}}
    assert is_subset(desired, actual)


def test_is_subset_namespace():
    assert is_subset({"Cisco-IOS-XE-snmp:contact": "Irvin"}, {"contact": "Irvin"})


def test_is_subset_list_values():
    assert is_subset({"RO": [None]}, {"RO": [None]})
    assert not is_subset({"RO": [None]}, {"RO": ["X"]})


def test_check_nunca_hace_put(capsys):
    class FakeClient:
        calls = 0

        def __init__(self, host, port):
            self.host = host
            self.port = port

        def get(self, path):
            return None

        def put(self, path, payload):
            FakeClient.calls += 1
            return 204

    FakeClient.calls = 0
    assert deploy_main(["--config", str(ROOT / "config/vars.yml"), "--check"],
                       client_factory=FakeClient) == 0
    assert FakeClient.calls == 0
    assert capsys.readouterr().out.count("[CAMBIO]") == 4


def test_deploy_idempotente(capsys):
    class FakeClient:
        state = {}
        writes = 0

        def __init__(self, host, port):
            pass

        def get(self, path):
            return FakeClient.state.get(path)

        def put(self, path, payload):
            FakeClient.writes += 1
            FakeClient.state[path] = payload
            return 201

    FakeClient.state = {}
    FakeClient.writes = 0
    args = ["--config", str(ROOT / "config/vars.yml")]
    assert deploy_main(args, client_factory=FakeClient) == 0
    assert FakeClient.writes == 4
    assert deploy_main(args, client_factory=FakeClient) == 0
    assert FakeClient.writes == 4
    assert capsys.readouterr().out.count("[OK]") == 4
