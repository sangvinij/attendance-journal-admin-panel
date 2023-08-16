import requests

from .api_requests import host


def test_check_code_response():
    rs = requests.get(f"{host}/wrong_url/", timeout=5)
    assert rs.status_code == 404
    rs = requests.get(f"{host}/auth/users/", timeout=5)
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/users/me/", timeout=5)
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/token/login/", timeout=5)
    assert rs.status_code == 405
    rs = requests.get(f"{host}/auth/token/logout/", timeout=5)
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/token/logoutall/", timeout=5)
    assert rs.status_code == 401
