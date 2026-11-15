from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


class Settings:
    agt_enabled = True
    agt_agent_id = "tst_id"
    agt_policy_dir = str(PROJECT_ROOT / "agent_os" / "policies")


settings = Settings()
