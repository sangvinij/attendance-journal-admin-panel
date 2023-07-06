import os
import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
host = os.getenv("HOST_FOR_TESTS", "http://localhost:8000")


def test_docs():
    rs = requests.get(f"{host}/api/docs/")
    assert rs.status_code == 200
    assert "Backend CRM" in rs.text
