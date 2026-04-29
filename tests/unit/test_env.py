from __future__ import annotations

import os
from pathlib import Path

from ibkr_monitor.common.env import load_dotenv


def test_load_dotenv_sets_variable_names_without_overwriting(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TOKEN=from_file\nEXISTING=from_file\n", encoding="utf-8")
    os.environ["EXISTING"] = "already_set"

    try:
        load_dotenv(env_file)

        assert os.environ["TOKEN"] == "from_file"
        assert os.environ["EXISTING"] == "already_set"
    finally:
        os.environ.pop("TOKEN", None)
        os.environ.pop("EXISTING", None)
