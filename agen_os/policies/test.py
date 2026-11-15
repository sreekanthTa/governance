from __future__ import annotations

import threading
from pathlib import Path

from agent_os.policies import PolicyEvaluator

_evaluator = None
_ready = False
_lock = threading.Lock()

_POLICY_DIR = Path(__file__).resolve().parent


def _build():
    global _evaluator, _ready
    if _ready:
        return _evaluator

    with _lock:
        if _ready:
            return _evaluator

        _ready = True

        try:
            ev = PolicyEvaluator()
            ev.load_policies(str(_POLICY_DIR))
            _evaluator = ev if ev.policies else None
        except Exception:
            _evaluator = None

        return _evaluator


def evaluate(tool_name: str, args: dict):
    ev = _build()

    if ev is None:
        return False, "No policy engine available"

    ctx = {
        "tool_name": tool_name,
        "agent_id": "test",
        "session_id": "test",
    }
    # ctx.update({k: v for k, v in args.items() if v is not None})

    try:
        d = ev.evaluate(ctx)
    except Exception as exc:
        return False, f"Policy evaluation failed: {exc}"

    allowed = bool(d.allowed)
    return allowed, "" if allowed else (d.reason or "denied by policy")


if __name__ == "__main__":
    for tool_name in ("web_search", "read_file", "delete_employee","test"):
        allowed, reason = evaluate(tool_name, {})
        print(f"{tool_name:16s} allowed={allowed} reason={reason!r}")
