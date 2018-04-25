""" simple wrapper around habitica api
API details from https://habitica.com/#/options/settings/api
API docs: https://habitica.com/apidoc/
"""

import requests
from nodb import NoDB
from fuzzy_dict import FuzzyDict


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

    def get_tasks_simple(self, task_type=None):
        tasks_detail = self.get_tasks(task_type)
        tasks = FuzzyDict()
        for td in tasks_detail:
            simple_task = {'id': td['id'],
                           'type': td['type'],
                           'direction': 'up'
                           }
            if td.get('down'):
                simple_task['direction'] = 'down'
            tasks[td['text'].lower()] = simple_task
        return tasks

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

    def complete_task(self, task_id, direction='up'):
        # https://habitica.com/api/v3/tasks/:taskId/score/:direction
        url = BASE_HABITICA_URL + "tasks/%s/score/%s" % (task_id, direction)

        # get current stats so we can calculate bonus
        status = self.get_user_stats()
        data = {'scoreNotes': 'scored by life-tracker Alexa skill'}
        resp = requests.post(url, data=data, headers=self.auth_headers)
        data = resp.json()
        print("in complete_task resp is %s" % data)

        import pdb
        pdb.set_trace()
        data - status
        return resp.json()

    def get_user_stats(self):
        url = BASE_HABITICA_URL + 'user?userFields=stats.gp,stats.hp,stats.mp,stats.xp'
        resp = requests.get(url, headers=self.auth_headers)
        return resp.json()

def get_habitica(session):
    '''
    give me an alexa session, I"ll see if we have a linked account with Habitica
    '''
    userid = session['user']['userId']
    auth = session.get('attributes', {}).get('habitica_auth_header')
    if auth:
        print("in get_habitica we got cached auth")
        return Habitica(auth_headers=auth)
    else:
        print("in get_habitica no cached auth")
        return Habitica(userid)


def match_task_with_habitica(task, session):
    habitica = get_habitica(session)
    tasks = habitica.get_tasks_simple()
    session_attribute = {'habitica_tasks': tasks}
    matched, key, item, ratio = tasks._search(task)
    task_info = {'found': matched, 'key': key, 'id': item['id'], 'direction': item['direction']}
    return {'query': task_info, 'all': session_attribute}
