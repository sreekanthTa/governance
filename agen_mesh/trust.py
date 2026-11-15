"""Mesh pillar 1 - Zero-Trust: trust score for the agent."""
from __future__ import annotations
import sys
import threading
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import yaml

import identity as _agent_identity

_CONFIG = _HERE / "mesh.yaml"

_tracker = None
_agent = None
_DEFAULT_SCORE = 500
_ready = False
_lock = threading.Lock()


def _load_config() -> dict:
    """Load the mesh.yaml configuration file."""
    if not _CONFIG.exists():
        return {}
    return yaml.safe_load(_CONFIG.read_text())


def _build():
    global _tracker, _agent, _ready

    if _ready:
        return _tracker

    with _lock:
        if _ready:
            return _tracker

        _ready = True

        try:

            from agentmesh.trust_types import TrustTracker

            did = _agent_identity.did()
            if not did:
                raise RuntimeError("No agent identity available")

            _tracker = TrustTracker()
            _agent = did

        except Exception:
            _tracker = None
            _agent = None
            _ready = False

    return _tracker


def score() -> int:
    """Current trust score on the 0-1000 scale."""

    tracker = _build()

    if tracker is None:
        return _DEFAULT_SCORE

    return round(tracker.get_score(_agent) * 1000)


def level() -> str:

    tracker = _build()

    if tracker is None:
        return "unknown"

    from agentmesh.trust.levels import trust_level_for_score

    return trust_level_for_score(score())


def record(peer_id, action, success) -> int:

    tracker = _build()

    if tracker is None:
        return _DEFAULT_SCORE

    tracker.record_interaction(_agent, peer_id, action, success)

    return score()


def did():
    return _agent_identity.did()


def has_capability(capability):
    return _agent_identity.has_capability(capability)


def is_active():
    return _agent_identity.is_active()


def main():
    print("did:", did())
    print("active:", is_active())
    print("score:", score())
    print("level:", level())
    print("record ok ->", record("peer-1", "handshake", True))
    print("record fail ->", record("peer-1", "handshake", False))


if __name__ == "__main__":
    main()
