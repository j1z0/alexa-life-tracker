from lambdas.life_tracker.service import lambda_handler
import pytest
from os import environ
import re


@pytest.fixture()
def list_task_request():
    return {
      "version": "1.0",
      "session": {
        "new": True,
        "sessionId": "amzn1.echo-api.session.22f7c53c-2ae4-414e-a46a-6e223792a0c3",
        "application": {
          "applicationId": "amzn1.ask.skill.8f090917-b362-4145-a587-ec40d2f8464f"
        },
        "user": {
          "userId": "amzn1.ask.account.AES7YE",
          "accessToken": environ.get("HABITICA_USER", "") + ":" + environ.get("HABITICA_TOKEN", ""),
        }
      },
      "context": {
        "AudioPlayer": {
          "playerActivity": "IDLE"
        },
        "Display": {},
        "System": {
          "application": {
            "applicationId": "amzn1.ask.skill.8f090917-b362-4145-a587-ec40d2f8464f"
          },
          "user": {
            "userId": "amzn1.ask.account.AES7YE"
          },
          "device": {
            "deviceId": "amzn1.ask.device.AE6P56NB",
            "supportedInterfaces": {
              "AudioPlayer": {},
              "Display": {
                "templateVersion": "1.0",
                "markupVersion": "1.0"
              }
            }
          },
          "apiEndpoint": "https://api.amazonalexa.com",
          "apiAccessToken": "eyJ0eXAiOiJKV1Q"
        }
      },
      "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-api.request.eaf82234-531c-4121-8a3f-e55450917cca",
            "timestamp": "2018-05-12T13:28:41Z",
            "locale": "en-US",
            "intent": {
                "name": "ListTasksIntent",
                "confirmationStatus": "NONE",
                "slots": {
                    "list_word": {
                        "name": "list_word",
                        "value": "list my",
                        "confirmationStatus": "NONE"
                    },
                    "time": {
                        "name": "time",
                        "confirmationStatus": "NONE"
                    },
                    "task_type": {
                        "name": "task_type",
                        "value": "tasks",
                        "confirmationStatus": "NONE"
                    }
                }
            },
            "dialogState": "STARTED"
        }
    }


def test_list_tasks(list_task_request):
    res = lambda_handler(list_task_request, None)
    speech = res['response']['outputSpeech']['text']
    print(res)
    assert re.match('You have.\d+.tasks', speech)
