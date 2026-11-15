"""Mesh pillar 1 - Zero-Trust Identity: who the agent is."""
from __future__ import annotations
import threading
from pathlib import Path

import yaml

_CONFIG = Path(__file__).resolve().parent / "mesh.yaml"

_identity = None
_ready = False
_lock = threading.Lock()


def _load_config() -> dict:
    """Load the mesh.yaml configuration file."""
    if not _CONFIG.exists():
        return {}
    return yaml.safe_load(_CONFIG.read_text())

def _build():
    global _identity, _ready

    if _ready:
        return _identity

    with _lock:
        if _ready:
            return _identity

        _ready = True

        try:

            from agentmesh.identity import AgentIdentity

            _identity = AgentIdentity.create(
                name="tst",
                sponsor="sponsor@example.com",
                capabilities=["cap"],
                organization="org",
            )

        except Exception:
            _identity = None
            _ready = False

    return _identity


def did():
    identity = _build()
    return str(identity.did) if identity else ""


def has_capability(capability):
    identity = _build()
    return bool(identity and identity.has_capability(capability))


def is_active():
    identity = _build()
    return bool(identity and identity.is_active())


def current():
    """The built AgentIdentity object, or None."""
    return _build()


def main():
    print("did:", did())
    print("has 'cap':", has_capability("cap"))
    print("has 'nope':", has_capability("nope"))
    print("active:", is_active())


if __name__ == "__main__":
    main()