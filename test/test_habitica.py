import os
from life_tracker.habitica_api import Habitica, match_task_with_habitica
from life_tracker.fuzzy_dict import FuzzyDict


def test_get_todos():
    amz = os.environ['AMZ_USER_ID']
    habitica = Habitica(amz)
    habitica.get_todos()


def test_get_tasks():
    amz = os.environ['AMZ_USER_ID']
    habitica = Habitica(amz)
    habitica.get_tasks()
    fuzz = habitica.get_tasks_simple()
    assert isinstance(fuzz, FuzzyDict)


def test_match_task_with_habitica():
    ret = match_task_with_habitica('15', {'user': {'userId': os.environ['AMZ_USER_ID']}})
    print(ret)


def test_complete_task():
    amz = os.environ['AMZ_USER_ID']
    habitica = Habitica(amz)
    new_task = habitica.add_task('make this unittest pass', 'todo')
    # now complete the one we just created
    res = habitica.complete_task(new_task['data']['_id'])
    assert(res['gold_earned'] > 0)
    assert('xp_earned' in res)
    assert('lvl_earned' in res)


def test_complete_daily():
    amz = os.environ['AMZ_USER_ID']
    habitica = Habitica(amz)
    # daily - farting
    id = 'd5df2968-89d9-462b-bcb9-146c2c600b01'
    # now complete the one we just created
    res = habitica.complete_task(id)
    assert(res)
