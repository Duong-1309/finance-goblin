from pathlib import Path
from unittest.mock import patch

import pytest

from app.db.database import init_db


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path):
    """Give every test its own fresh SQLite DB and disable device auth by default."""
    db_file = tmp_path / "test.db"
    init_db(db_file)
    with (
        patch("app.services.analyzer.settings") as mock_analyzer,
        patch("app.core.security.settings") as mock_security,
    ):
        mock_analyzer.db_path = str(db_file)
        mock_analyzer.monthly_budget = 20_000_000
        mock_security.device_api_key = ""  # auth off by default; test_security.py overrides
        yield db_file
