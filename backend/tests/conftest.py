from pathlib import Path
from unittest.mock import patch

import pytest

from app.db.database import init_db


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path):
    """Give every test its own fresh SQLite DB so CI has no dependency on a real data/ file."""
    db_file = tmp_path / "test.db"
    init_db(db_file)
    with patch("app.services.analyzer.settings") as mock_settings:
        mock_settings.db_path = str(db_file)
        mock_settings.monthly_budget = 20_000_000
        yield db_file
