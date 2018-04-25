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
    pass
    amz = os.environ['AMZ_USER_ID']
    habitica = Habitica(amz)
    tasks = habitica.get_tasks_simple()
    # TODO create the todo first... then complete it
    res = habitica.complete_task(tasks['laundry']['id'])
    print(res)
