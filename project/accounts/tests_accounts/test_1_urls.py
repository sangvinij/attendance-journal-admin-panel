import requests

from .api_requests import host


def test_check_code_response():
    rs = requests.get(f"{host}/wrong_url/")
    assert rs.status_code == 404
    rs = requests.get(f"{host}/auth/users/")
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/users/me/")
    assert rs.status_code == 200
    rs = requests.get(f"{host}/auth/token/login/")
    assert rs.status_code == 405
    rs = requests.get(f"{host}/auth/token/logout/")
    assert rs.status_code == 401
    rs = requests.get(f"{host}/auth/token/logoutall/")
    assert rs.status_code == 401
