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
TASK_TYPES = FuzzyDict({'daily': 'dailys',
                        'todo': 'todos',
                        'reward': 'rewards',
                        'habit': 'habits'
                        })
ADD_TASK_TYPES = FuzzyDict({'daily': 'daily',
                            'todo': 'todo',
                            'reward': 'reward',
                            'habit': 'habit'
                            })


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
        tasks_detail, _ = self.get_tasks(task_type)
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

        habitica_type = None
        try:
            if task_type:
                habitica_type = TASK_TYPES[task_type]
        except KeyError:
            pass

        url = BASE_HABITICA_URL + 'tasks/user'
        if habitica_type:
            url += '?type=%s' % habitica_type

        resp = requests.get(url, headers=self.auth_headers)
        if resp.status_code == 200:
            return resp.json()['data'], habitica_type
        else:
            raise Exception("Couldn't connect to Habitica, with supplied credentials %s" %
                            str(resp.json()))
        return None, habitica_type

    def get_todos(self):
        return self.get_tasks(task_type='todos')

    def complete_task(self, task_id, direction='up'):
        # https://habitica.com/api/v3/tasks/:taskId/score/:direction
        url = BASE_HABITICA_URL + "tasks/%s/score/%s" % (task_id, direction)

        # get current stats so we can calculate bonus
        before = self.get_user_stats()['data']
        data = {'scoreNotes': 'scored by life-tracker Alexa skill'}
        resp = requests.post(url, data=data, headers=self.auth_headers)
        after = resp.json().get('data')

        ret = {}
        if after:
            print("in complete_task resp is %s" % after)
            ret['gold_earned'] = round(after['gp'] - before['stats']['gp'], 2)
            ret['xp_earned'] = after['exp'] - before['stats']['exp']
            ret['lvl_earned'] = after['lvl'] - before['stats']['lvl']
            ret['class'] = after['class']
        else:
            # let's try and determine the error
            ret['error'] = resp.json()['message']
            if resp.json()['message'].startswith('Your session is outdated'):
                ret['error'] = "You've already done that today, try again tommorrow"

        return ret

    def add_task(self, task, task_type='todo'):
        url = BASE_HABITICA_URL + 'tasks/user'
        task_type = ADD_TASK_TYPES[task_type]
        # text,type,notes
        data = {'text': task, 'type': task_type,
                'notes': '... added by Alexa Life Tracker',
                }
        if task_type == 'habit':
            data['up'] = True
            data['down'] = False
        resp = requests.post(url, data=data, headers=self.auth_headers)
        data = resp.json()
        print("in add_task(%s, %s) resp is %s" % (task, task_type, data))
        return data

    def get_user_stats(self):
        url = BASE_HABITICA_URL + 'user?userFields=stats'
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


def add_task(session, task, task_type='todo'):
    habitica_type = TASK_TYPES[task_type]
    print("picked type %s from input %s" % (habitica_type, task_type))
    habitica = get_habitica(session)
    return habitica.add_task(task, habitica_type)


def match_task_with_habitica(task, session):
    habitica = get_habitica(session)
    tasks = habitica.get_tasks_simple()
    session_attribute = {'habitica_tasks': tasks}
    matched, key, item, ratio = tasks._search(task)
    task_info = {'found': matched, 'key': key, 'id': item['id'], 'direction': item['direction']}
    return {'query': task_info, 'all': session_attribute}
