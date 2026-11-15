from __future__ import annotations

import threading
from pathlib import Path

from agent_control_plane.signals import AgentSignal, SignalDispatcher

_manager = None
_ready = False
_lock = threading.Lock()


def _build():
    global _manager, _ready
    if _ready:
        return _manager

    with _lock:
        if _ready:
            return _manager

        _ready = True

        try:
            _manager = SignalDispatcher(agent_id="tstid")
        except Exception:
            _manager = None

        return _manager


def status() -> dict:
    """Current agent state."""
    disp = _build()
    if disp is None:
        return {"running": True, "stopped": False, "terminated": False}
    return {
        "running": disp.is_running,
        "stopped": disp.is_stopped,
        "terminated": disp.is_terminated,
    }

def pause():
    disp = _build()
    if disp:
        disp.signal(AgentSignal.SIGSTOP, source="api")
    return status()

def kill(reason: str = "killed via API") -> dict:
    """Terminate the agent (SIGKILL). SIGKILL raises AgentKernelPanic by design."""
    disp = _build()
    if disp:
        try:
            disp.signal(AgentSignal.SIGKILL, source="api", reason=reason)
        except Exception:  # noqa: BLE001 - SIGKILL raises AgentKernelPanic
            pass
    return status()

def resume() -> dict:
    """Resume the agent (SIGCONT)."""
    disp = _build()
    if disp:
        disp.signal(AgentSignal.SIGCONT, source="api")
    return status()


def main():
    print("status:", status())
    print("pause:", pause())
    print("resume:", resume())
    print("kill:", kill("run once"))


if __name__ == "__main__":
    main()
