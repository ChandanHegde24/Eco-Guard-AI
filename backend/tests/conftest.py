import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from data_layer.database import init_db
from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    init_db()
    with TestClient(app) as test_client:
        yield test_client
