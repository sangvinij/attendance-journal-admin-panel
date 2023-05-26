from django.test import TestCase

from accounts.models import User


class UserApiTestCase(TestCase):
    def setUp(self):
        password_user1 = 'pbkdf2_sha256$600000$L7TyaoQe7pSJ2aThVT7lI6$7Mn7HUSnsVPdPDoluueQAEwp5D5QsKyYrR2qOU3tnw4='
        # password_user1 = hash from 'password1'
        test_user1 = User.objects.create(first_name='test',
                                         last_name='user1',
                                         username='test_username1',
                                         is_active='1',
                                         is_superuser='0',
                                         password=password_user1)

    def test_get_response(self):
        self.assertEqual(self.client.get('').status_code, 200)
        self.assertEqual(self.client.get('/auth/users/').status_code, 401)
        self.assertEqual(self.client.get('/auth/users/me/').status_code, 401)
        self.assertEqual(self.client.get('/auth/token/login/').status_code, 405)
        self.assertEqual(self.client.get('/auth/token/logout/').status_code, 401)

    def test_register_login(self):
        # wrong email
        self.assertEqual(self.client.post('/auth/token/login/',
                                          data={'username': 'test_wrong_username1',
                                                'password': 'password1', }
                                          ).status_code, 400)
        # wrong password
        self.assertEqual(self.client.post('/auth/token/login/',
                                          data={'username': 'test_username1',
                                                'password': 'wrong_password1', }
                                          ).status_code, 400)
        # successful login
        self.assertEqual(self.client.post('/auth/token/login/',
                                          data={'username': 'test_username1',
                                                'password': 'password1', }
                                          ).status_code, 200)
        # successful register
        self.assertEqual(self.client.post('/auth/users/', data={'username': 'test_username3',
                                                                'password': 'password3'}).status_code, 201)
        # successful get bearer token
        response = self.client.post('/auth/token/login/', data={'username': 'test_username3',
                                                                'password': 'password3'})
        bearer_token = (response.data['auth_token'])
        # successful get information from profile
        self.assertEqual(
            self.client.get('/auth/users/me/', headers={'Authorization': f'Token {bearer_token}'}).status_code,
            200
        )
        self.assertEqual(
            self.client.get('/auth/users/me/', headers={'Authorization': f'Token {bearer_token}'}).data['username'],
            'test_username3'
        )
