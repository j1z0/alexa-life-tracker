'''
Test for first time users authentication
'''

import pytest
from life_tracker.service import lambda_handler


@pytest.fixture
def hello_request():
    return {
        "session": {
            "sessionId": "SessionId.7c77f955-ae5e-46f1-a9ca-3fb354b1ce77",
            "application": {
                "applicationId": "amzn1.echo-sdk-ams.app.fb2fc3e7-55e7-4f05-851e-7ad308a6b499"
            },
            "user": {
                "userId": "amzn1.ask.account.AFP3ZWPOS2BGJR7OWJZ3DHPKMOMNWY4AY66FUR7ILBWAN"
                "IHQN73QHMAHCTVTAHFPUV3WAFNGKBYW5LFUE2WV4CCGEISSPHBHCW5SCYJDL3DLWRRRBB4CQIP3X3PV6"
                "5V2AYMMXSNFPKHPZJFVAH5AHKHDLAER67H3AHL4XBUU76XEH5BGDZZNGV5T6HHAGN6KGZI777J3VA7WGPA"
            },
            "new": True
        },
        "request": {
            "type": "IntentRequest",
            "requestId": "EdwRequestId.b595d667-caa3-4818-8d4a-c7a31e8adddc",
            "timestamp": "2016-05-27T15:36:26Z",
            "intent": {
                "name": "SayHello",
                "slots": {}
            },
            "locale": "en-US"
        },
        "version": "1.0"
    }


def test_prompt_for_account_linking_first_time(hello_request):
    res = lambda_handler(hello_request, None)
    import pprint
    pprint.pprint(res)
    assert res['response']['card']['type'] == 'LinkAccount'
