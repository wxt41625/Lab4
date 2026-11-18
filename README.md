# U4ACT04 | Ciclo DevOps con RESTCONF | Irvin Misael Mejia Hernandez

Proyecto adaptado del ZIP de la practica para **Catalyst 9300 accesible por VPN**.
Se preservan los cuatro recursos YANG y el pipeline CI/CD.

## Debian + venv

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl snmp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Edita `config/vars.yml`: `host` debe ser la IP/hostname del **switch Catalyst**
que aparece en las instrucciones de tu reserva, NO el servidor de VPN.
**No guardes credenciales en YAML ni en commits.**

```bash
read -rp 'Usuario Catalyst: ' SANDBOX_USER; export SANDBOX_USER
read -rsp 'Password Catalyst: ' SANDBOX_PASS; echo; export SANDBOX_PASS
export VERIFY_SSL=false   # solo en laboratorio con certificado autofirmado
```

Asegura la VPN y ejecuta sin modificar el equipo:

```bash
python src/probe.py
python -m pytest -q
yamllint config .github
flake8 src tests --max-line-length=100
python src/deploy.py --check
```

## GitHub Actions con VPN

El job `build-test` corre en `ubuntu-latest` con lint + pruebas unitarias,
**sin credenciales ni conectividad al Catalyst**.
Al integrar un PR en `main`, el job `deploy` necesita un runner
`self-hosted` Linux instalado en el equipo Debian CON VPN activa.

GitHub repo -> Settings -> Actions -> Runners -> New self-hosted runner -> Linux.
Ejecuta en tu Debian los comandos que GitHub genera para descargar/configurar
el runner (en directorio separado del proyecto) y finalmente `./run.sh`.
Usa un **repositorio privado** para tu runner personal, y solo ejecuta
código revisado. Evita dejar habilitados jobs de PR no confiables en él.

Repo -> Settings -> Secrets and variables -> Actions -> Repository secrets:
`SANDBOX_USER`, `SANDBOX_PASS`. No subas secretos a Git.
Crea el Environment `sandbox-devnet` si GitHub te lo solicita.

## Evidencias

1. GitHub Issue con el cambio deseado.
2. Rama `feature/loopback-snmp`, commits y arbol de archivos.
3. Checks de PR (yamllint, flake8 y pytest).
4. `python src/deploy.py --check` desde VPN o log del job.
5. PR y merge, tag `v1.0`.
6. Job `deploy`: HTTP 201/204; en repeticiones puede mostrar [OK].
7. Segunda pasada idempotente `[OK] sin cambios`.
8. `verify.py`: `[PASS]` para 4 recursos.
9. `snmpwalk -v2c -c DEVOPS-RO -On <IP_CATALYST> 1.3.6.1.2.1.1.6.0`
   (si la VPN deja pasar UDP/161 y el equipo permite consultar SNMP).
10. Captura de reglas de protección de `main` y nombres de Secrets
    **sin mostrar valores**.

### Notas

El modelo YANG SNMP puede variar con IOS-XE. Si el switch responde 400/404
al aplicar SNMP, primero inspecciona la respuesta del `probe.py` y el JSON
real del path `.../restconf/data/Cisco-IOS-XE-native:native/snmp-server`.
La autenticacion RESTCONF es sobre HTTPS (443); SNMPv2c (UDP 161) solo se
usa en esta práctica controlada y no se recomienda para producción.
No cambies IP de gestion, usuarios, ni acceso a RESTCONF del switch.
