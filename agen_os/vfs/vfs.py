"""Pillar 4 - VFS: POSIX-style scratch space for the agent."""
from __future__ import annotations
import json
import sys
import threading
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agent_control_plane.vfs import AgentVFS, FileMode, MemoryBackend
from config import settings

_vfs = None
_ready = False
_lock = threading.Lock()


def _build():
    global _vfs, _ready
    if _ready:
        return _vfs
    with _lock:
        if _ready:
            return _vfs
        _ready = True
        if not settings.agt_enabled:
            return None
        try:
            vfs = AgentVFS(agent_id=settings.agt_agent_id)
            vfs.mount("/policy", _policy_backend(), mode=FileMode.RO, read_only=True)
            _vfs = vfs
        except Exception as exc:
            print(f"[agt.vfs] init failed: {exc}")
            _vfs = None
    return _vfs



def _policy_backend() -> MemoryBackend:
    """Read-only mirror of agt/policies/*.yaml."""
    backend = MemoryBackend()
    for f in Path(settings.agt_policy_dir).glob("*.yaml"):
        backend.write(f"/policy/{f.name}", f.read_bytes())
    return backend

def put_working(session_id: str, chunks: list[str]) -> None:
    vfs = _build()
    if vfs:
        vfs.write_json(f"/mem/working/{session_id}.json", {"chunks": chunks})

def get_working(session_id: str) -> dict:
    vfs = _build()
    return vfs.read_json(f"/mem/working/{session_id}.json") if vfs else {}

def put_episodic(session_id: str, question: str, answer: str) -> None:
    vfs = _build()
    if vfs:
        line = json.dumps({"q": question, "a": answer}) + "\n"
        vfs.write(f"/mem/episodic/{session_id}.jsonl", line, mode=FileMode.APPEND)


def main():
    put_working("session-1", ["hello", "world"])
    print("working:", get_working("session-1"))

    put_episodic("session-1", "What is 2+2?", "4")
    put_episodic("session-1", "What is 3+3?", "6")

    vfs = _build()
    if vfs:
        print("episodic:", vfs.read_text("/mem/episodic/session-1.jsonl"))


if __name__ == "__main__":
    main()