from django.test import TestCase

from pprint import pprint
import base64
import json
import pytest
import requests


base_url = 'http://127.0.0.1:8000'
login_url = 'http://127.0.0.1:8000/login'
toggle_headers = {}


class Request(requests.Session):
    def prepare_request(self, request):
        csrf_token = self.cookies.get('csrftoken')

        self.headers['X-CSRFToken'] = csrf_token

        if not request.url:
            raise ValueError("No URL to request")

        if not request.url.startswith('http'):
            request.url = base_url + request.url

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
                'password': 'hochwartjesus',
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

    @pytest.fixture(scope='function')
    def create_contact(self, admin):
        first_name = 'Daniel'
        last_name = 'Abreu'
        payload = {
            'contacts': {
                'first_name': first_name,
                'last_name': last_name,
                'email': 'alo@gmail.com'
            }
        }
        r = admin.post('/api/contacts', json=payload)
        _id = r.json()['contacts']['id']
        yield _id
        admin.delete('/api/contacts/{}'.format(_id))

    def test_POST(self, admin):
        first_name = 'Daniel'
        last_name = 'Abreu'
        payload = {
            'contacts': {
                'first_name': first_name,
                'last_name': last_name,
                'email': 'alo@gmail.com'
            }
        }
        r = admin.post('/api/contacts', json=payload)
        assert r.status_code == requests.codes.created

        admin.delete('/api/contacts/{}'.format(r.json()['contacts']['id']))

    def test_GET(self, admin, create_contact):
        r = admin.get('/api/contacts')
        assert len(r.json()['contacts']) == 1
        assert r.status_code == requests.codes.ok

    def test_GET_id(self, admin, create_contact):
        r = admin.get('/api/contacts/{}'.format(create_contact))
        assert r.status_code == requests.codes.ok

    def test_DELETE_id(self, admin, create_contact):
        r = admin.delete('/api/contacts/{}'.format(create_contact))
        assert r.status_code == requests.codes.ok

    def test_POST_id(self, admin):
        r = admin.post('/api/contacts/1')
        assert r.status_code == requests.codes.not_allowed

    def test_OPTIONS_id(self, admin):
        r = admin.options('/api/contacts/1')
        assert r.status_code == requests.codes.not_allowed

    @pytest.mark.skip()
    def test_patch_id_invalid_field(self, admin, create_contact):
        first_name = 'Daniel'
        last_name = 'Abreu'
        payload = {
            'contacts': {
                'first_name': first_name,
                'last_name': last_name,
                'id': 'bah'
            }
        }
        r = admin.patch('/api/contacts/{}'.format(create_contact), json=payload)
        assert r.status_code == requests.codes.bad_request

        r = admin.get('/api/contacts/{}'.format(create_contact))
        assert r.status_code == requests.codes.ok
        assert r.json()['contacts']['first_name'] == first_name
        assert r.json()['contacts']['last_name'] == 'Hochwart'
