from nodb import NoDB
from datetime import datetime
import random
import habitica_api

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
    elif intent_name == "ListTasksIntent":
        return list_tasks(intent, session)
    elif intent_name == "AddTaskIntent":
        return add_task(intent, session)
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

    '''attrib = session.get('attributes', {}).get('habitica_auth_header')
    if not attrib:
        print('not cached user getting habitica connection')
        habitica = habitica_api.get_habitica(session)
        print('got haibitica auth headers')
        attrib = {'habitica_auth_header': habitica.auth_headers}
    return build_response(attrib, None)
    '''


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


def add_task(intent, session):
    '''
    User: add my my husband's birthday to my calendar
    slots - targetCollection.owner.name - my
            object.name - my husband's birthday
            targetCollection.type - calendar
    '''
    card_title = intent['name']
    session_attributes = {}
    end_session = True
    speech_type = 'PlainText'
    reprompt_text = "I didn't get that. Try saying add task name "

    if 'task' in intent['slots'] and 'task_type' in intent['slots']:
        task = intent['slots']['task'].get('value', None)
        if not task:
            print("not task, lets elicit it")
            speech_output = "I'm sorry what task did you want to add?"
            elicit = elicit_slot('task', intent, speech_output, session_attributes)
            print(elicit)
            return elicit

        task_type = intent['slots']['task_type'].get('value', None)
        print("task_type is %s" % task_type)
        try:
            res = habitica_api.add_task(session, task, task_type)
        except KeyError as e:
            print("Key error adding task %s" % str(e))
            speech_output = "Did you want to add a habit, daily, todo, or a reward?"
            elicit = elicit_slot('task_type', intent, speech_output, session_attributes)
            return elicit

        if res['success']:
            print("added task")
            print(res)
            # todo complete task
            speech_output = "Task Added."
            end_session = True
        else:
            speech_output = "I'm sorry you can't do that. " + res['message']
            end_session = True
    else:
        speech_output = "I didn't get that. Try saying add task name "
        end_session = True

    return build_response(session_attributes, build_speechlet_response(
                          card_title, speech_output, reprompt_text, end_session, speech_type))


def list_tasks(intent, session):
    card_title = intent['name']
    session_attributes = {}
    end_session = True
    speech_type = 'PlainText'

    # TODO: handle time requests...

    task_type = None
    print("im in the list_tasks")
    if 'task_type' in intent['slots']:
        task_type = intent['slots']['task_type'].get('value', None)
    print("i got %s" % task_type)
    habitica = habitica_api.get_habitica(session)
    tasks, type_word = habitica.get_tasks(task_type)
    if not tasks:
        spacer = ''
        if task_type is None:
            type_word = 'task'
        if type_word == 'todos':
            type_word = 'todo'
            spacer = 'thing '
        speech_output = "You don't have any %s%s. Try saying" + \
                        " add task name to my %s." % (spacer, type_word, type_word)
        end_session = False
        reprompt_text = "Did you want to add another todo?  Say add task name."
    else:
        type_word = tasks[0]['type']
        type_word = type_word if type_word.endswith('s') else type_word + "'s"
        speech_output = "You have %s %s. " % (len(tasks), type_word)

        speech_output += combine_list_with_and(tasks, 6, start=True)

        reprompt_text = "Quest away and build thy character"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, end_session, speech_type))


def combine_list_with_and(seq, chunk_size, start=True):

    res = ", ".join(item.get('text') for item in seq[:chunk_size] if item.get('text'))

    if chunk_size > 1 and len(seq) > 1:
        temp = res.rsplit(',', 1)
        res = ' and'.join(temp)

    speech_output = ''
    if start:
        if len(seq) >= chunk_size:
            speech_output = "Here are the first " + str(chunk_size) + ". "
        else:
            speech_output = "They are. "

    return speech_output + res


def complete_task(intent, session):
    card_title = intent['name']
    session_attributes = {}
    end_session = False
    speech_type = 'PlainText'
    reprompt_text = "Thanks for using Life Tracker.  May the force be with you."

    # try to get alexa to fill in the slots first
    if 'task' in intent['slots']:
        task = intent['slots']['task'].get('value', None)
        if task:
            task_info = habitica_api.match_task_with_habitica(task, session)
            session_attributes = task_info['all']
            if not task_info['query']['found']:
                speech_output = "Can't find that, did you you mean %s?" % task_info['query']['key']
                return confirm_slot('task', task_info['query']['key'],
                                    intent, speech_output, session_attributes)
            else:
                habitica = habitica_api.get_habitica(session)
                res = habitica.complete_task(task_info['query']['id'], task_info['query']['direction'])
                if 'gold_earned' in res:
                    print("completed task")
                    print(res)
                    # todo complete task
                    speech_output = positive_response(task, res)
                    # add points output
                    speech_type = "SSML"
                    # speech_output = "Super.  You just completed your task " + task + \
                    #                ".  Great work."
                    # store to simple db
                    # update_taskdb(task, session['user']['userId'])
                    end_session = True
                else:
                    speech_output = "I'm sorry you can't do that. " + res['error']
                    end_session = True
        else:
            print("not task, lets elicit it")
            speech_output = "And what was it you did exactly?"
            elicit = elicit_slot('task', intent, speech_output, session_attributes)
            print(elicit)
            return elicit

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


def positive_response(task, task_res):
    pos_words = ['all righty', 'aooga', 'as you wish', 'bada bing bada boom', 'bam'
                 'bazinga', 'bingo', 'boom', 'booya', 'bravo', 'cha ching', 'cowabunga',
                 'dun dun dun', 'dynomite', 'eureka', 'fancy that', 'hear hear',
                 'hip hip hooray', 'hurrah', 'hurray', 'huzzah', 'kaching', 'kablam',
                 'kapow', 'kazaam', 'no way', 'oh snap', 'ohh la la', 'righto', 'wahoo',
                 'way to go', 'well done', 'whammo', 'whee', 'woo hoo', 'wowza', 'wow',
                 'yay', 'yippee', ]
    lvl_up_words = ['oh snap', 'no way', 'huzzah']
    final_word = ['great work!', 'good job!', 'amazing!', "you're awesome!", "stupendous",
                  'magnificent!', 'fasinating!', 'fantastic!']

    congrats = '<say-as interpret-as="interjection">%s</say-as>' % random.choice(pos_words)

    # calc exp / gold
    if task_res['lvl_earned']:
        lvlup = '<say-as interpret-as="interjection">%s</say-as>. You leveled up! ' % random.choice(lvl_up_words)
    else:
        lvlup = 'You gained %s gold pieces and %s experience! ' % (task_res['gold_earned'],
                                                                   task_res['xp_earned'])

    speech_output = "<speak> " + congrats + ". You just completed your task " + task + \
                    ". " + lvlup + random.choice(final_word) + "</speak>"
    return speech_output


def confirm_slot(slot, slot_value, intent, speech_output, session, should_end_session=False):
    intent['slots'][slot]['value'] = slot_value

    speech_part = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': speech_output
        },
        'shouldEndSession': should_end_session,
        "directives": [
                          {
                            "type": "Dialog.ConfirmSlot",
                            "slotToConfirm": slot,
                            "updatedIntent": intent
                           }
                       ]
        }
    return build_response(session, speech_part)


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


def build_response(session_attributes, speechlet_response=None):
    retval = {
        'version': '1.0',
        'sessionAttributes': session_attributes,
    }
    if speechlet_response:
        retval['response'] = speechlet_response
    return retval


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
        db_tasks = {'user': user,
                    'tasks': {task: [completion_time, ]}
                    }

    nodb.save(db_tasks)

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
