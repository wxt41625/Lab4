"""Cliente RESTCONF del Catalyst IOS-XE. No imprime credenciales."""

import os

import requests
import urllib3

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


class RestconfClient:
    """Solicitudes RESTCONF sobre HTTPS con autenticación básica."""

    def __init__(self, host, port=443):
        if not host or host == "CAMBIA_HOST_CATALYST":
            raise ValueError("Cambia 'host' en config/vars.yml por el Catalyst de tu reserva")
        user = os.environ.get("SANDBOX_USER")
        password = os.environ.get("SANDBOX_PASS")
        if not user or not password:
            raise ValueError("Define SANDBOX_USER y SANDBOX_PASS en el entorno")
        self.base = f"https://{host}:{port}/restconf/data"
        self.verify_ssl = os.getenv("VERIFY_SSL", "false").lower() == "true"
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.session.headers.update(HEADERS)

    def _request(self, method, path, payload=None):
        url = f"{self.base}/{path.lstrip('/')}"
        try:
            response = self.session.request(
                method,
                url,
                json=payload,
                verify=self.verify_ssl,
                timeout=25,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Fallo de red hacia {url}: revisa VPN, host, puerto 443 y ruta"
            ) from exc
        if method == "GET" and response.status_code == 404:
            return None, 404
        if not response.ok:
            detail = response.text[:700].replace("\n", " ")
            raise RuntimeError(
                f"RESTCONF {method} {path}: HTTP {response.status_code}. "
                f"Detalle: {detail}"
            )
        if method == "GET":
            try:
                return response.json() if response.content else None, response.status_code
            except ValueError as exc:
                raise RuntimeError("Respuesta inesperada: RESTCONF no devolvió JSON") from exc
        return None, response.status_code

    def get(self, path):
        body, _ = self._request("GET", path)
        return body

    def put(self, path, payload):
        _, status = self._request("PUT", path, payload)
        return status
