from lambdas.life_tracker.service import lambda_handler, combine_list_with_and
import pytest


@pytest.fixture()
def complete_task_request():
    return {
      "version": "1.0",
      "session": {
        "new": True,
        "sessionId": "amzn1.echo-api.session.22f7c53c-2ae4-414e-a46a-6e223792a0c3",
        "application": {
          "applicationId": "amzn1.ask.skill.8f090917-b362-4145-a587-ec40d2f8464f"
        },
        "user": {
          "userId": "amzn1.ask.account.AES7YE"
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
        "requestId": "amzn1.echo-api.request.5e1ce9b8-027a-4aba-bf93-fe47f23409c9",
        "timestamp": "2018-04-22T15:54:14Z",
        "locale": "en-US",
        "intent": {
          "name": "CompleteTaskIntent",
          "confirmationStatus": "NONE",
          "slots": {
            "complete_word": {
              "name": "complete_word",
              "confirmationStatus": "NONE"
            },
            "mark_word": {
              "name": "mark_word",
              "confirmationStatus": "NONE"
            },
            "task": {
              "name": "task",
              "confirmationStatus": "NONE"
            }
          }
        },
        "dialogState": "STARTED"
      }
    }


def test_complete_task_intent_started(complete_task_request):
    res = lambda_handler(complete_task_request, None)
    print(res)


def test_combine_list_with_and():
    lisd = [{'text': 'orange'}, {'text': 'yellow'}, {'text': 'green'}]
    combine = combine_list_with_and(lisd, 2, False)
    assert combine == 'orange and yellow'
    combine = combine_list_with_and(lisd, 1, False)
    assert combine == 'orange'
    combine = combine_list_with_and(lisd, 3, True)
    assert combine == 'Here are the first 3. orange, yellow and green'
    combine = combine_list_with_and(lisd, 4, True)
    assert combine == 'They are. orange, yellow and green'
