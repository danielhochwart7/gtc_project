from django.test import TestCase

from pprint import pprint
import base64
import json
import pytest
import requests


base_url = 'http://127.0.0.1:8000'
login_url = 'http://127.0.0.1:8000/login/'
toggle_headers = {}


class Request(requests.Session):
    def prepare_request(self, request):
        csrf_token = self.cookies.get('csrftoken')

        self.headers['X-CSRFToken'] = csrf_token

        if not request.url:
            raise ValueError("No URL to request")

        if not request.url.startswith('http'):
            request.url = base_url + request.url
            print(request.url)
        return super().prepare_request(request)


class SessionManager:
    def __init__(self):
        self.sessions = {'default': self.new_session('default')}

    def new_session(self, username) -> requests.Session:
        r = Request()
        r_token = r.get(login_url)
        users = {
            'default': {
                'csrfmiddlewaretoken': r_token.cookies.get('csrftoken'),
                'username': 'hochwart',
                'password': 'hochwart',
            }
        }
        try:
            data = users[username]
        except KeyError:
            raise ValueError('User {} not found.'.format(username))
        headers = {
            'origin': base_url,
            'referer': login_url,
        }

        response = r.post(login_url, data=data, headers=headers)

        assert response.status_code == 200

        return r

    def get_session(self, username) -> requests.Session:
        session = self.sessions.get(username)
        if not session:
            session = self.new_session(username)
            self.sessions[username] = session

        return session


@pytest.fixture(scope="function")
def session_manager():
    return SessionManager()


@pytest.fixture(scope="function")
def admin(session_manager) -> requests.Session:
    return session_manager.get_session('default')


class TestContacts:

    def test_GET(self, admin):
        r = admin.get('/contacts')
        pprint(r.json())
        assert r.status_code == requests.codes.ok

    def test_GET_id(self, admin):
        r = admin.get('/contacts/10')
        assert r.status_code == requests.codes.ok

    def test_DELETE_id(self, admin):
        r = admin.delete('/contacts/1')
        assert r.status_code == requests.codes.ok

    def test_POST_id(self, admin):
        r = admin.post('/contacts/1')
        assert r.status_code == requests.codes.not_allowed

    def test_OPTIONS_id(self, admin):
        r = admin.options('/contacts/1')
        assert r.status_code == requests.codes.not_allowed

    def test_patch_id(self, admin):
        payload = {
            'contacts': {
                'first_name': 'Novo',
                'last_name': 'Nome',
            }
        }
        r = admin.patch('/contacts/11', json=payload)
        assert r.status_code == requests.codes.ok

        r = admin.get('/contacts/11')
        assert r.status_code == requests.codes.ok
        assert r.json()['contacts']['first_name'] == 'Novo'
        assert r.json()['contacts']['last_name'] == 'Nome'
