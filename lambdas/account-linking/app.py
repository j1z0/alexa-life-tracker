import os
import sys
from chalice import Chalice, Response
from chalicelib import habitica_api

if sys.version_info[0] == 3:
    # Python 3 imports.
    from urllib.parse import urlparse, parse_qs  # noqa
else:
    # Python 2 imports.
    from urlparse import urlparse, parse_qs  # noqa

app = Chalice(app_name='account-linking')
app.debug = True

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# TODO: chalice don't deploy associated files, deal with this later
# LOGIN_FORM = os.path.join(DIR_PATH, 'login_form.html')


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/login/form', methods=['GET'])
def keys_form():
    '''
    expecting to be called by Amazon during alexa account linkin

    query params sent from amazon
    state, client_id, response_type, scope, and redirect_uri
    '''
    request = app.current_request
    # TODO: add wanted params list
    # wanted = ['
    # TODO: verify client id etc...

    qp = request.query_params if request.query_params else {}

    body = LOGIN_FORM
    if qp.get('api_token'):
        body = LOGIN_FAIL_FORM

    # poor mans templating
    for key, value in qp.iteritems():
        search = '{{'+key+'}}'
        body = body.replace(search, value)

    return Response(body=body,
                    status_code=200,
                    headers={'Content-Type': 'text/html'})


@app.route('/login/keys', methods=['POST'],
           content_types=['application/x-www-form-urlencoded'])
def keys():
    parsed = parse_qs(app.current_request.raw_body.decode())
    api_key = "%s:%s" % (parsed['uid'][0], parsed['apitoken'][0])
    stats = habitica_api.Habitica(api_user=api_key).get_user_stats()
    # verify keys work
    if not stats.get('success'):
        return Response(body='',
                        status_code=301,
                        headers={'Location': 'form?api_token=%s' % api_key})

    # ok so we need to validated posted
    redirect_qps = '#state=%s&access_token=%s&token_type=bearer' % (parsed['state'][0], api_key)
    redirect = parsed['redirect_uri'][0] + redirect_qps

    return Response(body='',
                    status_code=301,
                    headers={'Location': redirect})


LOGIN_FORM = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="provide habitica keys for use with Life Tracker">
    <meta name="author" content="j1z0">

    <title>Provide Habitica Auth Keys</title>

				<!-- Bootstrap core CSS -->
			<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">

    <!-- Custom styles for this template -->
<style>
html,
body {
  height: 100%;
}

body {
  display: -ms-flexbox;
  display: flex;
  -ms-flex-align: center;
  align-items: center;
  padding-top: 40px;
  padding-bottom: 40px;
  background-color: #f5f5f5;
}

.form-signin {
  width: 100%;
  max-width: 330px;
  padding: 15px;
  margin: auto;
}
.form-signin .checkbox {
  font-weight: 400;
}
.form-signin .form-control {
  position: relative;
  box-sizing: border-box;
  height: auto;
  padding: 10px;
  font-size: 16px;
}
.form-signin .form-control:focus {
  z-index: 2;
}
.form-signin input[type="email"] {
  margin-bottom: -1px;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}
.form-signin input[type="password"] {
  margin-bottom: 10px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>
  </head>
  <body class="text-center">
		<form class="form-signin" action="keys" method="POST" role="form">
      <img class="mb-4" src="https://j1z0.net/assets/img/lifeTracker-logo.png" alt="" width="72" height="72">
			<h1 class="h3 mb-3 font-weight-normal">Link LifeTracker and Habitica</h1>
      <label for="uid" class="sr-only">User ID</label>
      <input type="text" name="uid" class="form-control" placeholder="User ID on Habitica API Page" required autofocus>
      <label for="apitoken" class="sr-only">API Token</label>
      <input type="text" name="apitoken" class="form-control" placeholder="API Token on Habitica" required>
      <div class="checkbox mb-3">
        <label>
					<span> You can find your <a href="https://habitica.com/user/settings/api" >Habitica API Key here</a></span>
                    <span></span>
					<span> Don't have an account?</span>
		   <span><a href="https://habitica.com/static/home" >Sign up for Habitica</a></span>
        </label>
      </div>
			<input type="hidden" name="state" value="{{state}}">
			<input type="hidden" name="client_id" value="{{client_id}}">
			<input type="hidden" name="response_type" value="{{response_type}}">
			<input type="hidden" name="scope" value="{{scope}}">
			<input type="hidden" name="redirect_uri" value="{{redirect_uri}}">
      <button class="btn btn-lg btn-primary btn-block" type="submit">Link Accounts</button>
    </form>
  </body>

<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
</html>'''


LOGIN_FAIL_FORM = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="provide habitica keys for use with Life Tracker">
    <meta name="author" content="j1z0">

    <title>Provide Habitica Auth Keys</title>

				<!-- Bootstrap core CSS -->
			<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">

    <!-- Custom styles for this template -->
<style>
html,
body {
  height: 100%;
}

body {
  display: -ms-flexbox;
  display: flex;
  -ms-flex-align: center;
  align-items: center;
  padding-top: 40px;
  padding-bottom: 40px;
  background-color: #f5f5f5;
}

.form-signin {
  width: 100%;
  max-width: 330px;
  padding: 15px;
  margin: auto;
}
.form-signin .checkbox {
  font-weight: 400;
}
.form-signin .form-control {
  position: relative;
  box-sizing: border-box;
  height: auto;
  padding: 10px;
  font-size: 16px;
}
.form-signin .form-control:focus {
  z-index: 2;
}
.form-signin input[type="email"] {
  margin-bottom: -1px;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}
.form-signin input[type="password"] {
  margin-bottom: 10px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>
  </head>
  <body class="text-center">
		<form class="form-signin" action="keys" method="POST" role="form">
      <img class="mb-4" src="https://j1z0.net/assets/img/lifeTracker-logo.png" alt="" width="72" height="72">
			<h1 class="h3 mb-3 font-weight-normal text-danger">Login Failed</h1>
      <label for="uid" class="sr-only">User ID</label>
      <input type="text" name="uid" class="form-control" placeholder="User ID on Habitica API Page" required autofocus>
      <label for="apitoken" class="sr-only">API Token</label>
      <input type="text" name="apitoken" class="form-control" placeholder="API Token on Habitica" required>
      <div class="checkbox mb-3">
        <label>
					<span> You can find your <a href="https://habitica.com/user/settings/api" >Habitica API Key here</a></span>
                    <span></span>
					<span> Don't have an account?</span>
		   <span><a href="https://habitica.com/static/home" >Sign up for Habitica</a></span>
        </label>
      </div>
			<input type="hidden" name="state" value="{{state}}">
			<input type="hidden" name="client_id" value="{{client_id}}">
			<input type="hidden" name="response_type" value="{{response_type}}">
			<input type="hidden" name="scope" value="{{scope}}">
			<input type="hidden" name="redirect_uri" value="{{redirect_uri}}">
      <button class="btn btn-lg btn-primary btn-block" type="submit">Link Accounts</button>
    </form>
  </body>

<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
</html>'''
