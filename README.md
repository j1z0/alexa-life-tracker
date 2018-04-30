# Life Tracker - Alexas Front End for Habitica 

Life Tracker is simplestly describe as a voice interface into Habitica.Com.  Which is the gamified task tracking platform where you get to build dungeons and drangons style character by completing everyday tasks and managing projects.  Currently its very v.0.1, but the basic interface exits. Ideally plans would be to create more group tasks / quests / rewards and specific powerups you could get only through the voice interface.  Also, Life Tracker itself will have it's own quests to be completed either by teams / individuals to unlcok Life Tracker features, such as optional voice / sound packs, new features added, user call outs, etc... 

## Suggested Phrases 

Alexa open life tracker

Alexa tell life tracker I did it

Alexa tell life tracker I made my bed

Alexa ask life tracker what tasks do I have

Alexa tell life tracker to list my [ tasks | dailies | todos | habits | rewards ] 

Alexa tell life tracker to add a new [daily | todo | habit | reward] 

## how to code it 

```
# install in a virtualenv
mkvirtualenv lifetracker
workon lifetracker
pip install -r requirements-dev.txt
pip install -r requirements.txt

# invoke is command line build tool
invoke -l
invoke test 

# deploy the main alexa lambda
invoke deploy 


# the account linking module uses chalice to deploy that
cd lambda/account-linking
chalice deploy

```

## Configure
``
to prevent storing keys in the repo the system relies a lot on
enviornment variables.  If you get an error check to make sure you have
the correct ones set... For testing you want:
HABITICA_USER
HABITICA_TOKEN
AMZN_USER_ID
AMZ_CLIENT_SECRET
AMZ_CLIENT_ID


## More Info
- Tests use pytest.  Put all your unit tests in the tests folder, name them test_somthing.py.  Each test
function should start with the name test_ .  That's it, test away and be merry. :)

- This repo is also already pre-configured to run CI tests with travis.  So anything in your tests folder will get
ran each time you push code to github.  You need to make sure your new repo is enabled in travis however for this to happen.

- Publish will publish your code to pypi / cheese shop for easy sharing with the world
