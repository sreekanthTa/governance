"""Mesh pillar 1 - Zero-Trust Identity: credentials for the agent."""
from __future__ import annotations
import sys
import threading
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import yaml

from identity import did as _agent_did

_CONFIG = _HERE / "mesh.yaml"

_manager = None
_spiffe = None
_ready = False
_lock = threading.Lock()


def _load_config() -> dict:
    """Load the mesh.yaml configuration file."""
    if not _CONFIG.exists():
        return {}
    return yaml.safe_load(_CONFIG.read_text())


def _build():
    global _manager, _spiffe, _ready

    if _ready:
        return _manager

    with _lock:
        if _ready:
            return _manager

        _ready = True

        try:

            from agentmesh.identity import CredentialManager, SPIFFEIdentity

            did = _agent_did()
            if not did:
                raise RuntimeError("No agent identity available")

            _manager = CredentialManager(
                default_ttl=900
            )

            _spiffe = SPIFFEIdentity.create(
                agent_did=did,
                agent_name="ass",
                trust_domain="tstdoamin",
                organization="org"
            )

        except Exception:
            _manager = None
            _spiffe = None
            _ready = False

    return _manager


def isse(capabilities=None, resources=None, ttl_seconds=None):
    manager = _build()

    if manager is None:
        return None

    did = _agent_did()

    if not did:
        return None

    cred = manager.issue(
        agent_did=did, capabilities=capabilities, resources=resources,
        ttl_seconds=ttl_seconds,
    )

    return cred.model_dump()


def validate(token: str) -> dict | None:
    """Return the credential behind a raw token if still valid, else None."""
    manager = _build()
    if manager is None:
        return None
    cred = manager.validate(token)
    return cred.model_dump() if cred is not None else None


def spiffe_id() -> str | None:
    """This agent's SPIFFE ID (workload identity), or None."""
    _build()
    return _spiffe.spiffe_id if _spiffe is not None else None


def issue_svid(ttl_hours: int = 1) -> dict | None:
    """Issue a SPIFFE SVID (x509 workload certificate) for this agent."""
    _build()
    if _spiffe is None:
        return None
    return _spiffe.issue_svid(ttl_hours=ttl_hours).model_dump()


def main():
    print("spiffe_id:", spiffe_id())

    cred = isse(capabilities=["cap"])
    if cred is None:
        print("issue: None")
        return

    print("issued:", cred["credential_id"], "| ttl:", cred["ttl_seconds"], "| caps:", cred["capabilities"])
    print("validate (good):", validate(cred["token"]) is not None)
    print("validate (bad):", validate("not-a-token") is not None)

    svid = issue_svid()
    print("svid:", svid["spiffe_id"] if svid else None)


if __name__ == "__main__":
    main()
