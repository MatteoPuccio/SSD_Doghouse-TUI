import builtins
from unittest import mock
from unittest.mock import patch, Mock

import pytest
import requests
from requests import Response
from valid8 import ValidationError

import doghousetui
from doghousetui import Utils
from doghousetui.App import App


# @patch('builtins.input', side_effect=['1', 'username', 'password'])
# @patch('builtins.print')
# def test_menu_login_success():
#    app = App()
#    app.run()
@pytest.fixture
def invalid_usernames():
    return ['a', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'abcs#?', 'localhost@hi']


@pytest.fixture
def valid_usernames():
    return ['user22', '01', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', "paoloapaoloaaapoalo"]

@pytest.fixture
def valid_passwords():
    return["aaaaaaaa","123###78", "PASSWORDASAASD@@@ASDAS", "a!aaaaaaaaaasas9as89a89a89a98a"]

@pytest.fixture
def invalid_passwords():
    return["aaaaaaa","12?3###78", "PASSWORDASAASD@@@ASD'AS", "a!aaasasdasdasdas9as89a8989a98a"]

@mock.patch('builtins.print')
@mock.patch('requests.post')
def test_app_read_username_receives_invalid_username_fails_show_message_do_not_call_post(mocked_post, mocked_print, invalid_usernames ):
    for username in invalid_usernames:
        app: App = App()
        with patch('builtins.input', side_effect=['1', username, '0']):
            app.run()
            calls = []
            for call in mocked_print.call_args_list:
                args, kwargs = call
                for a in args:
                    calls.append(a)
            assert Utils.INVALID_USERNAME_ERROR in calls
            mocked_post.assert_not_called()


@mock.patch('requests.post')
def test_app_read_username_receives_valid_username_and_password_call_post_request(mocked_post, valid_usernames, valid_passwords):
    for i in range(0, len(valid_usernames)):
        app: App = App()
        with patch('builtins.input', side_effect=['1', valid_usernames[i], valid_passwords[i],'0']):
            app.run()
            mocked_post.assert_called()

@mock.patch('builtins.print')
@mock.patch('requests.post')
def test_app_read_password_receives_invalid_password_fails_show_message_do_not_call_post(mocked_post, mocked_print, invalid_passwords, valid_usernames):
    for password in invalid_passwords:
        app: App = App()
        with patch('builtins.input', side_effect=['1', valid_usernames[0], password,  '0']):
            app.run()
            calls = []
            for call in mocked_print.call_args_list:
                args, kwargs = call
                for a in args:
                    calls.append(a)
            assert Utils.INVALID_PASSWORD_ERROR in calls
            mocked_post.assert_not_called()

# @mock.patch("builtins.print")
# def test_app_valid_credentials_print_logged_in_message(mocked_print, valid_passwords, valid_usernames):
#     for i in range(0, len(valid_usernames)):
#
#         data = {"response":{'session_token': 'asd8g8asf9af89d9gas9f8gsjabhka123445ywef'}}
#         response = requests.Response()
#         response.status_code = 200
#         response.json = lambda: data
#
#         with patch('builtins.input', side_effect=['1', valid_usernames[i], valid_passwords[i], '0']):
#             with patch.object(doghousetui.App.App, 'login_request', side_effect=response) as mocked_post:
#                 app: App = App()
#                 app.run()
#                 calls = []
#                 for call in mocked_print.call_args_list:
#                     args, kwargs = call
#                     for a in args:
#                         calls.append(a)
#                 assert Utils.LOGGED_IN_MESSAGE % (valid_usernames[i]) in calls

