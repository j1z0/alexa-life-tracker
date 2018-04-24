""" simple wrapper around habitica api
API details from https://habitica.com/#/options/settings/api
API docs: https://habitica.com/apidoc/
"""

import requests
from nodb import NoDB


def db():
    nodb = NoDB()
    nodb.serializer = 'json'
    nodb.bucket = 'alexa-life-tracker'
    nodb.index = 'user'
    return nodb


class NotRegisteredException(Exception):
    pass


BASE_HABITICA_URL = 'https://habitica.com/api/v3/'


class Habitica(object):

    def __init__(self, amzn_id=None, auth_headers=None):
        if amzn_id:
            self.db = db()
            user = self.db.load(amzn_id + '-keys')
            if not user:
                raise NotRegisteredException("Can't find user %s" % amzn_id)
            self.auth_headers = {'x-api-user': user['habitica_user'], 'x-api-key': user['habitica_key']}
        elif auth_headers:
            self.auth_headers = auth_headers
        else:
            raise Exception('need either amazon id or auth headers to create Habitica object')

    def get_tasks(self, task_type=None):
        url = BASE_HABITICA_URL + 'tasks/user'

        if task_type:
            url += '?type=%s' % task_type

        resp = requests.get(url, headers=self.auth_headers)
        if resp.status_code == 200:
            return resp.json()['data']
        else:
            raise Exception("Couldn't connect to Habitica, with supplied credentials")

    def get_todos(self):
        return self.get_tasks(task_type='todos')


def get_habitica(session):
    '''
    give me an alexa session, I"ll see if we have a linked account with Habitica
    '''
    # TODO implement cachine here
    userid = session['user']['userId']
    auth = session.get('habitica_auth_header')
    if auth:
        return Habitica(auth_headers=auth)
    else:
        return Habitica(userid)
