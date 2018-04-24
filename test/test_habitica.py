import os
from life_tracker.habitica_api import Habitica


def test_get_todos():
    amz = os.environ['AMZ_USER_ID']
    habitica = Habitica(amz)
    habitica.get_todos()
