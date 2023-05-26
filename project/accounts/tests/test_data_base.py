import requests
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
host = os.getenv("HOST_FOR_TESTS", 'localhost:8000')



def test_get_token():
    rs = requests.post(f"http://{host}/auth/users/", {'username': 'test_username2',
                                                           'password': 'admin1',
                                                           'first_name': 'test',
                                                           'last_name': 'user2'})
    rs = requests.post(f"http://{host}/auth/token/login/", {'username': 'test_username2', 'password': 'admin1'})
    token = rs.json()['auth_token']
    rs = requests.get(f"http://{host}/auth/users/me/", headers={"Authorization": f"Token {token}"})
    assert rs.json()['username'] == 'test_username2'
    print('\r\nTEST PASS! CONGRATULATION!!!')
