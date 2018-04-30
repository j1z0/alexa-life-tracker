def lambda_handler(event, context):
    '''
    query params sent from amazon
    state, client_id, response_type, scope, and redirect_uri
    '''
    print(event)
    print(context)

    html = open('index.html').read()

    # poor mans templating engine :P
    for key, value in event.get('queryStringParameters', {}).iteritems():
        search = '{{'+key+'}}'
        html = html.replace(search, value)
    return html
