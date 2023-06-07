import os

from dotenv import find_dotenv, load_dotenv

import requests

load_dotenv(find_dotenv())
host = os.getenv("HOST_FOR_TESTS", "http://localhost:8000")


def test_check_code_response():
    rs = requests.get(f"{host}/wrong_url/")
    assert rs.status_code == 404
    rs = requests.get(f"{host}/auth/users/")
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/users/me/")
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/token/login/")
    assert rs.status_code == 405
    rs = requests.get(f"{host}/auth/token/logout/")
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/token/logoutall/")
    assert rs.status_code == 401
