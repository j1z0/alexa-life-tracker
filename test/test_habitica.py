import os
import pytest
from lambdas.life_tracker.habitica_api import Habitica, match_task_with_habitica
from lambdas.life_tracker.fuzzy_dict import FuzzyDict


@pytest.fixture()
def auth():
    return os.environ['HABITICA_USER'] + ':' + os.environ['HABITICA_TOKEN']


def test_get_todos(auth):
    habitica = Habitica(api_user=auth)
    habitica.get_todos()


def test_get_tasks(auth):
    habitica = Habitica(api_user=auth)
    habitica.get_tasks()
    fuzz = habitica.get_tasks_simple()
    assert isinstance(fuzz, FuzzyDict)


def test_match_task_with_habitica(auth):
    ret = match_task_with_habitica('15', {'user': {'accessToken': auth}})
    print(ret)


def test_get_user_stats(auth):
    habitica = Habitica(api_user=auth)
    stats = habitica.get_user_stats()
    assert(stats)


def test_get_user_description(auth):
    habitica = Habitica(api_user=auth)
    stats = habitica.get_user_description()
    assert(stats)


def test_complete_task(auth):
    habitica = Habitica(api_user=auth)
    new_task = habitica.add_task('make this unittest pass', 'todo')
    # now complete the one we just created
    res = habitica.complete_task(new_task['data']['_id'])
    assert(res['gold_earned'] > 0)
    assert('xp_earned' in res)
    assert('lvl_earned' in res)


def test_complete_daily(auth):
    habitica = Habitica(api_user=auth)
    # daily - farting
    id = 'd5df2968-89d9-462b-bcb9-146c2c600b01'
    # now complete the one we just created
    res = habitica.complete_task(id)
    assert(res)
