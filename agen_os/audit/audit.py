from __future__ import annotations

import threading
from pathlib import Path

from agent_os import FlightRecorder

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
            db = Path("audit.db")
            db.parent.mkdir(parents=True, exist_ok=True)
            _manager = FlightRecorder(str(db))
        except Exception:
            _manager = None

        return _manager


def record(tool_name: str, args: dict, allowed: bool, reason: str):
    rec = _build()

    if rec is None:
        return

    try:
        trace_id = rec.start_trace(
            agent_id="tst_id",
            tool_name=tool_name,
            tool_args=args,
        )

        if allowed:
            rec.log_success(trace_id)
        else:
            rec.log_violation(trace_id, reason)
    except Exception:
        pass


def verify():
    rec = _build()

    if rec is None:
        return None

    return rec.verify_integrity()


def main():
    record("web_search", {"query": "hello"}, allowed=True, reason="")
    record("delete_employee", {"id": "E-101"}, allowed=False, reason="blocked by policy")
    print(verify())


if __name__ == "__main__":
    main()
