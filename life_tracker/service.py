# -*- coding: utf-8 -*-
""" Habit Tracker """
from __future__ import print_function
from nodb import NoDB
from datetime import datetime
import random

# --------------- response handlers -----------------


def on_intent(request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + request['requestId'] +
          ", sessionId=" + session['sessionId'])
    intent = request['intent']
    intent_name = request['intent']['name']
    print('intent is')
    print(intent)

    # Dispatch to your skill's intent handlers
    if intent_name == "CompleteTaskIntent":
        return complete_task(intent, session)
    elif intent_name == "ListTaskIntent":
        pass
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return end_session()
    else:
        raise ValueError("Invalid intent")


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def dialog_delegate(intent):
    return {"type": "Dialog.Delegate",
            "updatedIntent": intent}

# ---------------------Biz Logix ----------------------------------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    # TODO: resample below mp3s
    # '<audio src="' + voice_line + '"/>' + \
    # voice_line = 'https://raw.githubusercontent.com/bingur/sounds-of-overwatch/master/' + \
    #             'vo/vo_misc/announcer/achievements%20unlocked.mp3'
    # voice_line = 'https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_bear_groan_roar_01.mp3'
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "<speak>Welcome to Life Tracker. " + \
                    "Tell me what task you just finished by saying, " + \
                    "Finished, and then the name of the task</speak>"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "What task did you just finish? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, "SSML"))


def task_attrib(task_name):
    return {'task': task_name}


def complete_task(intent, session):
    card_title = intent['name']
    session_attributes = {}
    end_session = False
    speech_type = 'PlainText'

    # try to get alexa to fill in the slots first
    if 'task' in intent['slots']:
        task = intent['slots']['task'].get('value', None)
        if task:
            session_attributes = task_attrib(task)
            speech_output = positive_response(task)
            speech_type = "SSML"
            # speech_output = "Super.  You just completed your task " + task + \
            #                ".  Great work."
            # store to simple db
            reprompt_text = "Thanks for use Life Tracker.  May the force be with you."
            update_taskdb(task, session['user']['userId'])
            end_session = True
        else:
            print("not task, lets elicit it")
            speech_output = "And what was it you did exactly?"
            elicit = elicit_slot('task', intent, speech_output, session_attributes)
            print(elicit)
            return elicit
            # reprompt_text = "I'm not sure what task you just completed. " + \
            #                "You can log a task by saying, " + \
            #                "I just completed, task name."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, end_session, speech_type))


def end_session():
    card_title = "Session Ended"
    speech_output = "Fantastic.  Keep on Tracking, Keep on Building. Talk Soon."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def positive_response(task):
    pos_words = ['all righty', 'aooga', 'as you wish', 'bada bing bada boom', 'bam'
                 'bazinga', 'bingo', 'boom', 'booya', 'bravo', 'cha ching', 'cowabunga',
                 'dun dun dun', 'dynomite', 'eureka', 'fancy that', 'hear hear',
                 'hip hip hooray', 'hurrah', 'hurray', 'huzzah', 'kaching', 'kablam',
                 'kapow', 'kazaam', 'no way', 'oh snap', 'ohh la la', 'righto', 'wahoo',
                 'way to go', 'well done', 'whammo', 'whee', 'woo hoo', 'wowza', 'wow',
                 'yay', 'yippee', ]

    final_word = ['great work!', 'good job!', 'amazing!', "you're awesome!", "stupendous",
                  'magnificent!', 'fasinating!', 'fantastic!']
    congrats = '<say-as interpret-as="interjection">%s</say-as>' % random.choice(pos_words)
    speech_output = "<speak> " + congrats + ". You just completed your task " + task + \
                    ". " + random.choice(final_word) + "</speak>"
    return speech_output


def elicit_slot(slot, intent, speech_output, session, should_end_session=False):
    speech_part = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': speech_output
        },
        'shouldEndSession': should_end_session,
        "directives": [
                          {
                            "type": "Dialog.ElicitSlot",
                            "slotToElicit": slot,
                            "updatedIntent": intent
                           }
                       ]
        }
    return build_response(session, speech_part)


def build_speechlet_response(title, output, reprompt_text, should_end_session,
                             speech_type='PlainText'):
    text_keyword = 'text' if speech_type == 'PlainText' else 'ssml'
    return {
        'outputSpeech': {
            'type': speech_type,
            text_keyword: output,
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- external integrations -----------------
def update_taskdb(task, user):

    user = user + '_tasks'
    nodb = NoDB()
    nodb.serializer = "json"
    nodb.bucket = "alexa-life-tracker"
    nodb.index = "user"

    # see if user exists
    db_tasks = nodb.load(user)
    print('loaded db_user')
    print(str(db_tasks))

    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(db_tasks, 'get') and db_tasks.get('tasks'):
        user_tasks = db_tasks.get('tasks', {})
        current_task = user_tasks.get(task, [])
        current_task.insert(0, completion_time)
        user_tasks[task] = current_task
    else:
        user_tasks = {'user': user,
                      'tasks': {task: [completion_time, ]}
                      }

    nodb.save(user_tasks)


# --------------- entry point -----------------


def lambda_handler(event, context):
    """ App entry point  """

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print(str(event))

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
