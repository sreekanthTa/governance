from __future__ import annotations

import threading
from pathlib import Path

from agent_os.integrations.rbac import RBACManager

_manager = None
_ready = False
_lock = threading.Lock()

_ROLES_FILE = Path(__file__).resolve().parent / "roles.yml"


def _build():
    global _manager, _ready
    if _ready:
        return _manager

    with _lock:
        if _ready:
            return _manager

        _ready = True

        try:
            _manager = RBACManager.from_yaml(str(_ROLES_FILE))
        except Exception:
            _manager = None

        return _manager


def evaluate(agent_id: str, tool_name: str):
    mgr = _build()

    if mgr is None:
        return False, "No RBAC manager available"

    try:
        allowed = bool(mgr.has_permission(agent_id, tool_name))
    except Exception as exc:
        return False, f"RBAC evaluation failed: {exc}"

    if allowed:
        return True, ""

    role = mgr.get_role(agent_id)
    return False, f"role '{role.value}' may not use '{tool_name}'"


if __name__ == "__main__":
    checks = (
        ("tst-assitant", "web_search"),
        ("tst-assitant", "read"),
        ("tst-assitant", "delete"),
        ("unknown-agent", "read"),
    )
    for agent_id, tool_name in checks:
        allowed, reason = evaluate(agent_id, tool_name)
        print(f"{agent_id:14s} {tool_name:14s} allowed={allowed} reason={reason!r}")
