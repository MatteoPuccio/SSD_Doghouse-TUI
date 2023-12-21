import builtins
from getpass import getpass
from typing import List
from unittest import mock
from unittest.mock import patch, Mock

import pytest
import requests
from requests import Response
from valid8 import ValidationError

import doghousetui
from doghousetui import Utils
from doghousetui.App import App, main
from doghousetui.domain import Dog, DogDescription, DogBirthInfo, Date, PictureUrl, Dogname, DogId, EstimatedAdultSize, \
    Sex, Breed


# @patch('builtins.input', side_effect=['1', 'username', 'password'])
# @patch('builtins.print')
# def test_menu_login_success():
#    app = App()
#    app.run()

@pytest.fixture
def invalid_username():
    return 'a'


@pytest.fixture
def invalid_password():
    return '12'


@pytest.fixture
def valid_username():
    return 'user22'


@pytest.fixture
def valid_password():
    return '123###78'


@pytest.fixture
def valid_token():
    return 'asd8g8asf9af89d9gas9f8gsjabhka123445ywef'

@pytest.fixture
def invalid_token():
    return 'asd8?asf9af89d9gas9f8gsabhka123445ywef'

@pytest.fixture
def invalid_usernames():
    return ['a', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'abcs#?', 'localhost@hi']

@pytest.fixture
def valid_email():
    return "email@domain.it"

@pytest.fixture
def valid_usernames():
    return ['user22', '01', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', "paoloapaoloaaapoalo"]

@pytest.fixture
def valid_emails():
    return ['aaa@aaa',"", 'email+@pip.com', 'valid@em.a', "+@1.1"]

@pytest.fixture
def invalid_emails():
    return ['aaaaaa',"", 'email+#ù@pip.com', 'valid@e.m.a', "email@b."]



@pytest.fixture
def valid_passwords():
    return ["aaaaaaaa", "123###78", "PASSWORDASAASD@@@ASDAS", "a!aaaaaaaaaasas9as89a89a89a98a"]


@pytest.fixture
def invalid_passwords():
    return ["aaaaaaa", "12?3###78", "PASSWORDASAASD@@@ASD'AS", "a!aaasasdasdasdas9as89a8989a98a"]


def mocked_return_args_partial_contains_string(mocked_print: Mock, target: str):
    for call in mocked_print.call_args_list:
        args, kwargs = call
        for a in args:
            if target in str(a):
                return True
    return False


def mocked_return_args_partial_contains_string_exactly_x_times(mocked_print: Mock, target: str, times: int):
    count: int = 0
    for call in mocked_print.call_args_list:
        args, kwargs = call
        for a in args:
            if target in str(a):
                count += 1
    return count == times


@mock.patch('builtins.print')
@mock.patch('requests.post')
def test_app_read_username_receives_invalid_username_fails_show_message_do_not_call_post(mocked_post, mocked_print,
                                                                                         invalid_usernames):
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
def test_app_read_username_receives_valid_username_and_password_call_post_request(mocked_post, valid_username,
                                                                                  valid_password):
    app: App = App()
    with patch('builtins.input', side_effect=['1', valid_username, '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            app.run()
            mocked_post.assert_called()


@mock.patch('builtins.print')
@mock.patch('requests.post')
def test_app_read_password_receives_invalid_password_fails_show_message_and_do_not_call_post(mocked_post, mocked_print,
                                                                                             invalid_password,
                                                                                             valid_username):
    app: App = App()
    with patch('builtins.input', side_effect=['1', valid_username, '0']):
        with patch('getpass.getpass', side_effect=[invalid_password]):
            app.run()
            mocked_print.assert_any_call(Utils.INVALID_PASSWORD_ERROR)
            mocked_post.assert_not_called()


@mock.patch("builtins.print")
def test_app_valid_credentials_print_logged_in_message(mocked_print, valid_passwords, valid_usernames, valid_token):
    for i in range(0, len(valid_usernames)):
        with patch('builtins.input', side_effect=['1', valid_usernames[i], '0', '0']):
            with patch('getpass.getpass', side_effect=[valid_passwords[i]]):
                with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                    with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                        app: App = App()
                        response_login = Mock(status_code=200)
                        response_login.json.return_value = {"key": valid_token}
                        mocked_post_login.return_value = response_login
                        response_role = Mock(status_code=200)
                        response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                        mocked_post_role.return_value = response_role
                        app.run()
                        mocked_print.assert_any_call(Utils.LOGGED_IN_MESSAGE % valid_usernames[i])


@mock.patch("builtins.print")
def test_continue_without_login_prints_not_logged_user_menu(mocked_print):
    with patch('builtins.input', side_effect=['2', '0', '0']):
        app: App = App()
        app.run()
        calls = []
        printed: bool = False
        for call in mocked_print.call_args_list:
            args, kwargs = call
            for a in args:
                calls.append(a)
                if Utils.GENERIC_USER_MENU_DESCRIPTION in a:
                    printed = True
                    break
        assert printed

@mock.patch("builtins.print")
def test_app_login_valid_user_credentials_show_user_menu( mocked_print, valid_password, valid_username, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '0', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response = Mock(status_code=200)
                    response.json.return_value = {"key": valid_token}
                    mocked_post.return_value = response
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.USER_MENU_DESCRIPTION)


@mock.patch("builtins.print")
def test_app_login_valid_user_credentials_show_admin_menu(mocked_print, valid_password, valid_username, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '0', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response = Mock(status_code=200)
                    response.json.return_value = {"key": valid_token}
                    mocked_post.return_value = response
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.ADMIN_MENU_DESCRIPTION)

@mock.patch("builtins.print")
def test_app_login_prints_error_on_invalid_role_received_by_backend(mocked_print, valid_username, valid_password,
                                                                valid_token):
    app: App = App()
    with patch('builtins.input', side_effect=['1', valid_username, '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with mock.patch.object(doghousetui.App.App, 'make_role_request') as mocked_get_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token,
                                                        Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: "Some useless unpredicted role"}
                    mocked_get_role.return_value = response_role
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.LOGIN_ERROR)


@mock.patch("builtins.print")
def test_app_logout_after_login_as_user_shows_login_menu_again(mocked_print, valid_username, valid_password,
                                                               valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '6', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_logout_request') as mocked_post_logout:
                        response_logout = Mock(status_code=200)
                        mocked_post_logout.return_value = response_logout
                        app.run()
                    assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,
                                                                                      Utils.LOGIN_MENU_DESCRIPTION, 2)


@mock.patch("builtins.print")
def test_app_logout_after_login_as_admin_shows_login_menu_again(mocked_print, valid_username, valid_password,
                                                                valid_token):
    app: App = App()
    with patch('builtins.input', side_effect=['1', valid_username, '8', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with mock.patch.object(doghousetui.App.App, 'make_role_request') as mocked_get_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token,
                                                        Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_get_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_logout_request') as mocked_post_logout:
                        response_logout = Mock(status_code=200)
                        mocked_post_logout.return_value = response_logout
                        app.run()
                    assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,
                                                                                      Utils.LOGIN_MENU_DESCRIPTION, 2)


@mock.patch("builtins.print")
def test_app_logout_prints_error_message_upon_response_error(mocked_print, valid_username, valid_email, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, valid_email, '6', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with mock.patch.object(doghousetui.App.App, 'make_role_request') as mocked_get_role:
                    app: App = App()
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token,
                                                        Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_get_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_logout_request') as mocked_post_logout:
                        response_logout = Mock(status_code=503)
                        mocked_post_logout.return_value = response_logout
                        app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.LOGOUT_ERROR)


@mock.patch("builtins.print")
def test_app_back_to_login_after_continue_without_login_prints_login_menu(mocked_print):
    with patch('builtins.input', side_effect=['2', '3', '0']):
        app: App = App()
        app.run()
        assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print, Utils.LOGIN_MENU_DESCRIPTION, 2)


@mock.patch("builtins.print")
def test_app_registration_prints_invalid_password_error_on_invalid_password(mocked_print, valid_username, valid_email,
                                                                            invalid_password, valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email, valid_username, valid_email, '0']):
        with patch('getpass.getpass', side_effect=[invalid_password, valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response = Mock(status_code=200)
                mocked_post.return_value = response
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,
                                                                                  Utils.INVALID_PASSWORD_ERROR, 1)
@mock.patch("builtins.print")
def test_app_registration_prints_invalid_email_error_on_invalid_email(mocked_print, valid_username, invalid_emails, valid_email,
                                                                            valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, invalid_emails, valid_email, '0']):
        with patch('getpass.getpass', side_effect=[valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response = Mock(status_code=200)
                mocked_post.return_value = response
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,
                                                                                  Utils.INVALID_EMAIL_ERROR, 1)

@mock.patch("builtins.print")
def test_app_registration_invalid_first_password_ask_again_for_first_password(mocked_print, valid_username, invalid_password, valid_email,
                                                                            valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email, '0']):
        with patch('getpass.getpass', side_effect=[invalid_password, valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response = Mock(status_code=200)
                mocked_post.return_value = response
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,
                                                                                  Utils.INVALID_PASSWORD_ERROR, 1)


@mock.patch("builtins.print")
def test_app_registration_prints_invalid_username_error_on_invalid_username(mocked_print, invalid_username,
                                                                            valid_username, valid_email, valid_password):
    with patch('builtins.input', side_effect=['3', invalid_username, valid_username,valid_email , '0']):
        with patch('getpass.getpass', side_effect=[valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response = Mock(status_code=200)
                mocked_post.return_value = response
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,
                                                                                  Utils.INVALID_USERNAME_ERROR, 1)


@mock.patch("builtins.print")
def test_app_registration_prints_error_on_second_password_different_from_first(mocked_print, valid_username, valid_email ,
                                                                               valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email, valid_username,valid_email, '0']):
        with patch('getpass.getpass',
                   side_effect=[valid_password, valid_password + 'a', valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response = Mock(status_code=200)
                mocked_post.return_value = response
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string(mocked_print,
                                                                  Utils.REGISTRATION_PASSWORDS_DO_NOT_COINCIDE)

@mock.patch("builtins.print")
def test_app_registration_prints_error_on_second_password_invalid_print_validation_error(mocked_print, valid_username, valid_email
                                                                               , invalid_password, valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email, '0']):
        with patch('getpass.getpass',
                   side_effect=[valid_password, invalid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response = Mock(status_code=200)
                mocked_post.return_value = response
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,
                                                                  Utils.REGISTRATION_PASSWORDS_DO_NOT_COINCIDE,1)


@mock.patch("builtins.print")
def test_login_prints_invalid_token_if_received_token_from_backend_is_invalid(mock_print, invalid_token, valid_username, valid_password):
    with patch('builtins.input', side_effect=['1', valid_username, '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                app: App = App()
                response_login = Mock(status_code=200)
                response_login.json.return_value = {"key": invalid_token}
                mocked_post_login.return_value = response_login
                app.run()
                assert mocked_return_args_partial_contains_string(mock_print, Utils.INVALID_TOKEN)



@mock.patch("builtins.print")
def test_login_prints_unable_to_log_in_if_profile_does_not_exist(mock_print, invalid_token, valid_username, valid_password):
    with patch('builtins.input', side_effect=['1', valid_username, '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                app: App = App()
                response_login = Mock(status_code=400)
                response_login.json.return_value = {"non_field_errors": ['Unable to log in with provided credentials.']}
                mocked_post_login.return_value = response_login
                app.run()
                assert mocked_return_args_partial_contains_string(mock_print, 'Unable to log in with provided credentials.')

@mock.patch("builtins.print")
def test_login_prints_connection_error_if_server_cannot_be_reached(mock_print, invalid_token, valid_username, valid_password):
    with patch('builtins.input', side_effect=['1', valid_username, '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                app: App = App()
                mocked_post_login.side_effect = ConnectionError("")
                app.run()
                assert mocked_return_args_partial_contains_string(mock_print, Utils.CONNECTION_ERROR)

@mock.patch("builtins.print")
def test_logout_prints_connection_error_if_server_cannot_be_reached(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '6', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_logout_request') as mocked_post_logout:
                        mocked_post_logout.side_effect = ConnectionError("")
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)


@mock.patch("builtins.print")
def test_registration_of_user_with_already_existing_username_prints_error(mocked_print,valid_username, valid_email, valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email ,'0']):
        with patch('getpass.getpass', side_effect=[valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response_registration = Mock(status_code=400)
                response_registration.json.return_value = {'username': ['A user with that username already exists.']}
                mocked_post.return_value = response_registration
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string(mocked_print,

                                                                  'A user with that username already exists.')

@mock.patch("builtins.print")
def test_failed_registration_of_user_followed_by_login_menu(mocked_print,valid_username, valid_email, valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email,'0']):
        with patch('getpass.getpass', side_effect=[valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                mocked_post.side_effect = Exception("")
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print, Utils.LOGIN_MENU_DESCRIPTION,2)



@mock.patch("builtins.print")
def test_failed_registration_of_user_failed_due_to_connection_error_prints_error_message(mocked_print,valid_username, valid_email, valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email,'0']):
        with patch('getpass.getpass', side_effect=[valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                mocked_post.side_effect = ConnectionError("")
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print, Utils.CONNECTION_ERROR,1)


@mock.patch("builtins.print")
def test_registration_of_user_error_code_followed_by_login_menu(mocked_print,valid_username, valid_email, valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email ,'0']):
        with patch('getpass.getpass', side_effect=[valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response_registration = Mock(status_code=400)
                response_registration.json.return_value = {'username': ['A user with that username already exists.']}
                mocked_post.return_value = response_registration
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print, Utils.LOGIN_MENU_DESCRIPTION,2)

@mock.patch("builtins.print")
def test_registration_of_user_successfully_followed_by_login_menu(mocked_print,valid_username, valid_email, valid_password):
    with patch('builtins.input', side_effect=['3', valid_username, valid_email ,'0']):
        with patch('getpass.getpass', side_effect=[valid_password, valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response_registration = Mock(status_code=204)
                mocked_post.return_value = response_registration
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print, Utils.LOGIN_MENU_DESCRIPTION,2)

@mock.patch("builtins.print")
def test_registration_invalid_for_server_prints_error_by_server(mocked_print, valid_email):
    with patch('builtins.input', side_effect=['3', "andrea", valid_email, '0']):
        with patch('getpass.getpass', side_effect=["andrea88", "andrea88"]):
            with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                response_registration = Mock(status_code=400)
                response_registration.json.return_value = {'non_field_errors': ['The password is too similar to the username.']}
                mocked_post.return_value = response_registration
                app: App = App()
                app.run()
                assert mocked_return_args_partial_contains_string(mocked_print,
                                                                  'The password is too similar to the username')

def test_registration_of_user_prints_registered_message_upon_registration_made( valid_usernames,valid_emails, valid_passwords):
    for i in range(0, len(valid_usernames)):
        with patch("builtins.print") as mocked_print:
            with patch('builtins.input', side_effect=['3', valid_usernames[i], valid_emails[i], '0']):
                with patch('getpass.getpass', side_effect=[valid_passwords[i], valid_passwords[i]]):
                    with mock.patch.object(doghousetui.App.App, 'make_registration_request') as mocked_post:
                        response_registration = Mock(status_code=204)
                        mocked_post.return_value = response_registration
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.REGISTRATION_SUCCEEDED_MESSAGE)


@mock.patch("builtins.print")
def test_failed_get_preferences_due_to_connection_error_prints_error_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '2', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_show_preferences_request') as mocked_get:
                        mocked_get.side_effect = ConnectionError("")
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)


@mock.patch("builtins.print")
def test_failed_add_preferences_due_to_connection_error_prints_error_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_add_preference_to_dog_request') as mocked_get:
                        mocked_get.side_effect = ConnectionError("")
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)

@mock.patch("builtins.print")
def test_failed_remove_preferences_due_to_connection_error_prints_error_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '4', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_remove_preference_to_dog_request') as mocked_get:
                        mocked_get.side_effect = ConnectionError("")
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)

@mock.patch("builtins.print")
def test_succeeded_get_preferences_called_print_dogs_after_parse_response(mocked_print, valid_username, valid_password, valid_token, single_batch_json, valid_dogBuilder):
    with patch('builtins.input', side_effect=['1', valid_username, '2', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_show_preferences_request') as mocked_get:
                        with patch.object(doghousetui.App.App, 'print_dogs') as mocked_print_dogs:
                            with patch.object(doghousetui.App.App, 'create_dog_list_from_json') as mocked_create_dogs_from_json:
                                response_preferences = Mock(status_code=200)
                                response_preferences.json.return_value = single_batch_json
                                mocked_get.return_value=response_preferences
                                dogs:list = [valid_dogBuilder.build()]
                                mocked_create_dogs_from_json.return_value = dogs
                                app: App = App()
                                app.run()
                                mocked_create_dogs_from_json.assert_called_with(single_batch_json)
                                mocked_print_dogs.assert_called_with(dogs)



@mock.patch("builtins.print")
def test_succeeded_add_preference_prints_correctly_added_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_add_preference_to_dog_request') as mocked_add_preference:
                        response_add_preference = Mock(status_code=201)
                        mocked_add_preference.return_value = response_add_preference
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.ADD_PREFERENCE_SUCCEEDED_MESSAGE)

@mock.patch("builtins.print")
def test_failed_add_preference_due_to_missing_dog_in_database_prints_error_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_add_preference_to_dog_request') as mocked_add_preference:
                        response_add_preference = Mock(status_code=404)
                        response_add_preference.json.return_value = {'dog_id': 'some error'}
                        mocked_add_preference.return_value = response_add_preference
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.ADD_PREFERENCE_FAILED_DOG_ID)

@mock.patch("builtins.print")
def test_failed_add_preference_due_to_already_present_preference_for_user_and_dog_print_error_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_add_preference_to_dog_request') as mocked_add_preference:
                        response_add_preference = Mock(status_code=404)
                        response_add_preference.json.return_value = {'non_field_errors': 'some error'}
                        mocked_add_preference.return_value = response_add_preference
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.ADD_PREFERENCE_FAILED_DUPLICATE)

@mock.patch("builtins.print")
def test_succeeded_remove_preference_prints_correctly_removed_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '4', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_remove_preference_to_dog_request') as mocked_delete:
                        response_mocked_delete = Mock(status_code=204)
                        mocked_delete.return_value = response_mocked_delete
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.REMOVE_PREFERENCE_SUCCEEDED_MESSAGE)

@mock.patch("builtins.print")
def test_failed_remove_preference_prints_error_message(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '4', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
                    mocked_post_role.return_value = response_role
                    with mock.patch.object(doghousetui.App.App, 'make_remove_preference_to_dog_request') as mocked_delete:
                        response_mocked_delete = Mock(status_code=404)
                        mocked_delete.return_value = response_mocked_delete
                        app: App = App()
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.REMOVE_PREFERENCE_FAILED_MESSAGE)


@mock.patch("builtins.print")
def test_remove_dog_prints_error_when_the_specified_dog_does_not_exist(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '2', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role
                    with patch.object(doghousetui.App.App, 'make_dog_remove_request') as mocked_delete:
                        response_delete = Mock(status_code=404)
                        mocked_delete.return_value = response_delete
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_NOT_FOUND_ERROR)

@mock.patch("builtins.print")
def test_remove_dog_prints_dog_removed_when_the_specified_dog_exist_and_is_eliminated(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '2', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role
                    with patch.object(doghousetui.App.App, 'make_dog_remove_request') as mocked_delete:
                        response_delete = Mock(status_code=204)
                        mocked_delete.return_value = response_delete
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_DELETED_MESSAGE)

@mock.patch("builtins.print")
def test_remove_dog_prints_invalid_id_error_when_the_specified_id_is_invalid(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '-2', '2', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token}
                    mocked_post_login.return_value = response_login
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role
                    with patch.object(doghousetui.App.App, 'make_dog_remove_request') as mocked_delete:
                        response_delete = Mock(status_code=200)
                        mocked_delete.return_value = response_delete
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_ID_VALIDATION_ERROR)


@pytest.fixture
def valid_DogId():
    return 1


@pytest.fixture
def valid_Dogname():
    return "Pippo"


@pytest.fixture
def valid_DogDescription():
    return "description"


@pytest.fixture
def valid_DogBirthInfo():
    return DogBirthInfo(Breed("Bolognese"), Sex("M"), Date.parse_date("2020-05-05"), EstimatedAdultSize("L"))


@pytest.fixture
def valid_entry_date():
    return "2020-05-05"


@pytest.fixture
def valid_DogPicture():
    return "https://i.imgur.com/Ada6755nsv.png"


@pytest.fixture
def valid_dogBuilder( valid_DogId, valid_DogBirthInfo, valid_entry_date):
    return Dog.Builder(DogId(valid_DogId), valid_DogBirthInfo, Date.parse_date(valid_entry_date), True)

@mock.patch("builtins.print")
@patch.object(doghousetui.App.App, 'make_add_dog_request')
@patch.object(doghousetui.App.App, 'make_role_request')
def test_add_dog_essentials_and_empty_dog_optional_fields_with_valid_input_produce_dog_to_be_added(mocked_post_role, mocked_request, mocked_print, valid_dogBuilder, valid_username, valid_password, valid_token, valid_entry_date):
    with patch('builtins.input', side_effect=['1', valid_username, '2', "Bolognese","M",valid_entry_date,"L", valid_entry_date, "Y","","","" , '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
                with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post:
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role
                    response_request = Mock(status_code=201)
                    mocked_request.return_value = response_request
                    app: App = App()
                    response = Mock(status_code=200)
                    response.json.return_value = {"key": valid_token}
                    mocked_post.return_value = response
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_ADDED_MESSAGE)

@mock.patch("builtins.print")
@patch.object(doghousetui.App.App, 'make_add_dog_request')
@patch.object(doghousetui.App.App, 'make_role_request')
def test_add_dog_with_invalid_breed_call_method_of_suggestions_of_breed_and_print_suggestions(mocked_post_role, mocked_request, mocked_print, valid_dogBuilder, valid_username, valid_password, valid_token, valid_entry_date):
    with patch('builtins.input', side_effect=['1', valid_username, '2',"INVALID_DOG_BREED", "Bolognese","M",valid_entry_date,"L", valid_entry_date, "Y","","","" , '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
                with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post:
                    with patch.object(doghousetui.domain.Breed, 'similar_breeds') as mocked_similar_breeds:
                        response_role = Mock(status_code=200)
                        response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                        mocked_post_role.return_value = response_role
                        response_request = Mock(status_code=201)
                        mocked_request.return_value = response_request
                        app: App = App()
                        response = Mock(status_code=200)
                        response.json.return_value = {"key": valid_token}
                        mocked_post.return_value = response
                        mocked_similar_breeds.return_value = ["DOG_BREED_OF_TESTING"]
                        app.run()
                        mocked_similar_breeds.assert_called()
                        mocked_similar_breeds.assert_called()
                        assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print, "DOG_BREED_OF_TESTING",1)


@mock.patch("builtins.print")
@patch.object(doghousetui.App.App, 'make_add_dog_request')
@patch.object(doghousetui.App.App, 'make_role_request')
def test_add_dog_essential_and_dog_options_fields_with_valid_input_produce_dog_to_be_added(mocked_post_role, mocked_add_dog_request, mocked_print, valid_dogBuilder, valid_Dogname, valid_DogDescription, valid_DogPicture, valid_username, valid_password, valid_token, valid_entry_date):
    with patch('builtins.input', side_effect=['1', valid_username, '2', "Bolognese","M",valid_entry_date,"L", valid_entry_date, "Y",valid_Dogname,valid_DogDescription,valid_DogPicture , '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
                with patch.object(doghousetui.App.App, 'make_login_request') as mocked_login_post:
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role

                    response_request = Mock(status_code=201)
                    mocked_add_dog_request.return_value = response_request
                    app: App = App()
                    response = Mock(status_code=200)

                    response.json.return_value = {"key": valid_token}
                    mocked_login_post.return_value = response
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_ADDED_MESSAGE)

@mock.patch("builtins.print")
@patch.object(doghousetui.App.App, 'make_role_request')
def test_add_dog_essential_and_dog_options_fields_with_invalid_dog_not_call_request_and_print_invalid_dog_message(mocked_post_role, mocked_print, valid_dogBuilder, valid_Dogname, valid_DogDescription, valid_DogPicture, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '2', "Bolognese","M","2020-05-06","L", "2020-05-05", "Y",valid_Dogname,valid_DogDescription,valid_DogPicture , '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
                with patch.object(doghousetui.App.App, 'make_login_request') as mocked_login_post:
                    with patch.object(doghousetui.App.App, 'make_add_dog_request') as mocked_add_dog_request:
                        response_role = Mock(status_code=200)
                        response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                        mocked_post_role.return_value = response_role

                        response = Mock(status_code=200)
                        response.json.return_value = {"key": valid_token}

                        mocked_login_post.return_value = response
                        app: App = App()
                        app.run()
                        mocked_add_dog_request.assert_not_called()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_BIRTH_AFTER_ENTRY)


@mock.patch("builtins.print")
@patch.object(doghousetui.App.App, 'make_add_dog_request')
@patch.object(doghousetui.App.App, 'make_role_request')
def test_add_valid_dog_but_unable_to_contact_server_print_connection_error_message(mocked_post_role, mocked_add_dog_request, mocked_print, valid_dogBuilder, valid_Dogname, valid_DogDescription, valid_entry_date ,valid_DogPicture, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '2', "Bolognese","M",valid_entry_date,"L", valid_entry_date, "Y",valid_Dogname,valid_DogDescription,valid_DogPicture , '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
                with patch.object(doghousetui.App.App, 'make_login_request') as mocked_login_post:

                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role

                    mocked_add_dog_request.side_effect = ConnectionError("test")

                    response = Mock(status_code=200)
                    response.json.return_value = {"key": valid_token}
                    mocked_login_post.return_value = response

                    app: App = App()
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)

@mock.patch("builtins.print")
@patch.object(doghousetui.App.App, 'make_add_dog_request')
@patch.object(doghousetui.App.App, 'make_role_request')
def test_add_dog_print_server_error_in_case_server_reject_operation(mocked_post_role, mocked_add_dog_request, mocked_print, valid_dogBuilder, valid_Dogname, valid_DogDescription, valid_entry_date ,valid_DogPicture, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '2', "Bolognese","M",valid_entry_date,"L", valid_entry_date, "Y",valid_Dogname,valid_DogDescription,valid_DogPicture , '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
                with patch.object(doghousetui.App.App, 'make_login_request') as mocked_login_post:
                    response_role = Mock(status_code=200)

                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role

                    response_add_dog_request = Mock(status_code=400)
                    response_add_dog_request.json.return_value = {'non_field_errors':["TEST_ERROR"]}
                    mocked_add_dog_request.return_value = response_add_dog_request

                    response = Mock(status_code=200)
                    response.json.return_value = {"key": valid_token}

                    mocked_login_post.return_value = response
                    app: App = App()
                    app.run()
                    assert mocked_return_args_partial_contains_string(mocked_print, "TEST_ERROR")


@pytest.fixture
def dogs_json():
    return [{'user': 1, 'dog': {'id': 13, 'name': 'Toby', 'breed': 'Half-breed', 'sex': 'M', 'birth_date': '2023-12-16',
             'entry_date': '2023-12-16', 'neutered': False, 'description': '', 'estimated_adult_size': 'M',
             'picture': ''}},{'user': 1, 'dog':  {'id': 14, 'name': 'Bigdog', 'breed': 'Afghan Hound', 'sex': 'M',
             'birth_date': '2023-12-04', 'entry_date': '2023-12-08', 'neutered': True,
            'description': 'some descr', 'estimated_adult_size': 'M', 'picture': ''}},
            {'user': 1, 'dog': {'id': 15, 'name': 'Somedog', 'breed': 'Affenpinscher', 'sex': 'F',
             'birth_date': '2023-12-11', 'entry_date': '2023-12-17', 'neutered': False,
             'description': 'some desc', 'estimated_adult_size': 'M', 'picture': ''}}]

@pytest.fixture
def dogs_list():
    return [Dog.Builder(DogId(13), DogBirthInfo(Breed('Half-breed'), Sex("M"), Date.parse_date('2023-12-16'), EstimatedAdultSize("S")),  Date.parse_date('2023-12-16'),False).build(),
            Dog.Builder(DogId(14), DogBirthInfo(Breed('Half-breed'), Sex("M"), Date.parse_date('2023-12-16'), EstimatedAdultSize("S")),  Date.parse_date('2023-12-16'),False).build(),
            Dog.Builder(DogId(15), DogBirthInfo(Breed('Half-breed'), Sex("M"), Date.parse_date('2023-12-16'), EstimatedAdultSize("S")),  Date.parse_date('2023-12-16'),False).build(),
            Dog.Builder(DogId(16), DogBirthInfo(Breed('Half-breed'), Sex("M"), Date.parse_date('2023-12-16'), EstimatedAdultSize("S")),  Date.parse_date('2023-12-16'),False).build(),
            ]

@pytest.fixture
def single_batch_json():
    return [{'user': 1, 'dog': {'id': 13, 'name': 'Toby', 'breed': 'Half-breed', 'sex': 'M', 'birth_date': '2023-12-16',
             'entry_date': '2023-12-16', 'neutered': False, 'description': '', 'estimated_adult_size': 'M',
             'picture': ''}},{'user': 1, 'dog': {'id': 14, 'name': 'Bigdog', 'breed': 'Afghan Hound', 'sex': 'M',
             'birth_date': '2023-12-04', 'entry_date': '2023-12-08', 'neutered': True,
            'description': 'some descr', 'estimated_adult_size': 'M', 'picture': ''}}]


def test_create_dog_from_json_creates_dog_with_specified_attributes(dogs_json):
    dog_json = dogs_json[0]['dog']
    app: App = App()
    dog: Dog = app.create_dog_from_json(dog_json)
    assert (dog.name.value == 'Toby' and dog.dog_id.value == 13 and
            dog.birth_info.breed.value == 'Half-breed' and dog.birth_info.sex.value == 'M'
            and dog.birth_info.birth_date == Date.parse_date('2023-12-16') and
            dog.entry_date == Date.parse_date('2023-12-16') and dog.neutered == False
            and dog.description.value == '' and dog.birth_info.estimated_adult_size.value == 'M'
            and dog.picture.value == '')

def test_create_dog_list_from_json_creates_dog_list_of_correct_size(dogs_json):
    app: App = App()
    all_dogs: List[Dog] = app.create_dog_list_from_json(dogs_json)
    assert 3 == len(all_dogs)

@mock.patch("builtins.print")
def test_print_dogs_prints_dogs_inside_dog_list_2_batches(mocked_print, dogs_list):
    with patch('builtins.input', side_effect=['y']):
        app: App = App()
        app.print_dogs(dogs_list)
        for dog in dogs_list:
            assert mocked_return_args_partial_contains_string(mocked_print, str(dog.dog_id.value))

@mock.patch("builtins.print")
def test_print_dogs_prints_dogs_inside_dog_list_2_batches_prints_only_first_batch_if_n_as_input(mocked_print, dogs_list):
    with patch('builtins.input', side_effect=['n']):
        app: App = App()
        app.print_dogs(dogs_list)
        for i in range(0, Utils.SHOW_DOGS_BATCH_SIZE):
            assert mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_ID_PRINT+str(dogs_list[i].dog_id.value))
        for i in range(Utils.SHOW_DOGS_BATCH_SIZE, len(dogs_list)):
            assert not mocked_return_args_partial_contains_string(mocked_print, Utils.DOG_ID_PRINT+str(dogs_list[i].dog_id.value))


@mock.patch("builtins.print")
def test_print_dogs_prints_dogs_inside_dog_list_1_batch(mocked_print, dogs_list):
    app: App = App()
    dogs_list_one = [dogs_list[0]]
    app.print_dogs(dogs_list_one)
    for dog in dogs_list_one:
        assert mocked_return_args_partial_contains_string(mocked_print, str(dog.dog_id.value))

@mock.patch("builtins.print")
def test_show_dogs_prints_retreived_dogs_from_show_dogs(mocked_print, single_batch_json):
    with patch('builtins.input', side_effect=['2', '1', '0']):
        app: App = App()
        with patch.object(doghousetui.App.App, 'make_dogs_request') as mocked_show_dogs_get:
            response = Mock(status_code=200)
            response.json.return_value = single_batch_json
            mocked_show_dogs_get.return_value = response
            app.run()
            for entry in single_batch_json:
                dog = entry['dog']
                assert mocked_return_args_partial_contains_string(mocked_print, str(dog["id"]))


@mock.patch("builtins.print")
def test_show_dogs_prints_retreived_dogs_from_show_dogs_receive_corrupted_data_print_error(mocked_print):
    with patch('builtins.input', side_effect=['2', '1', '0']):
        app: App = App()
        with patch.object(doghousetui.App.App, 'make_dogs_request') as mocked_show_dogs_get:
            response = Mock(status_code=400)
            app.run()
            assert mocked_return_args_partial_contains_string(mocked_print, Utils.SHOW_DOGS_ERROR)

@mock.patch("builtins.print")
def test_show_dogs_prints_connection_error_upon_exception_from_request(mocked_print, single_batch_json):
    with patch('builtins.input', side_effect=['2', '1', '0']):
        app: App = App()
        with patch.object(doghousetui.App.App, 'make_dogs_request') as mocked_show_dogs_get:
            mocked_show_dogs_get.side_effect = ConnectionError("")
            app.run()
            assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)

@mock.patch("builtins.print")
def test_remove_dog_prints_connection_error_upon_exception_from_request(mocked_print, valid_username, valid_password, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '3', '12', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response = Mock(status_code=200)
                    response.json.return_value = {"key": valid_token}
                    mocked_post_login.return_value = response
                    response_role = Mock(status_code=200)
                    response_role.json.return_value = {Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                    mocked_post_role.return_value = response_role
                    with patch.object(doghousetui.App.App, 'make_dog_remove_request') as mocked_remove_dog_request:
                        mocked_remove_dog_request.side_effect = ConnectionError("")
                        app.run()
                        assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)


@mock.patch('builtins.print')
def test_show_dogs_with_filters_prints_connection_error_if_server_is_not_reachable(mocked_print):
    with patch('builtins.input', side_effect=['2', '2', 'Half-breed', 'M', '2023', '2023', '0']):
        app: App = App()
        with patch.object(doghousetui.App.App, 'make_dogs_with_filters_request') as mocked_show_dogs_get:
            mocked_show_dogs_get.side_effect = ConnectionError("")
            app.run()
            assert mocked_return_args_partial_contains_string(mocked_print, Utils.CONNECTION_ERROR)


@mock.patch('builtins.print')
def test_read_dog_id_prints_error_when_invalid_error(mocked_print):
    with patch('builtins.input', side_effect=['-1', 'a', '3']):
        app: App = App()
        app.read_dog_id()
        assert mocked_return_args_partial_contains_string_exactly_x_times(mocked_print,Utils.DOG_ID_VALIDATION_ERROR, 2)

@mock.patch("builtins.print")
def test_create_dogs_list_from_json_receive_invalid_dog_print_error(mocked_print):
    app:App = App()
    app.create_dog_list_from_json([{'user':1, 'dog': {'id': 13, 'name': 'Toby', 'breed': 'Half-breed', 'sex': 'M', 'birth_date': '2023-12-16',
      'entry_date': '2023-12-15', 'neutered': False, 'description': '', 'estimated_adult_size': 'M',
      'picture': ''}}])
    mocked_print.assert_called_with(Utils.DOG_RECEIVED_ERROR)

def test_pack_filters_params_returns_a_correct_dictionary():
    my_dict = {"breed": "Half-breed", "estimated_adult_size": "M", "birth_date_gte": "2023", "birth_date_lte": "2023"}
    my_dict_packed = App().pack_filters_params("Half-breed", "M", "2023", "2023")
    assert my_dict == my_dict_packed

@mock.patch('builtins.print')
def test_main_app_print_panic_error_for_unhandled_errors(mocked_print):
    with patch.object(doghousetui.App.App, "run") as mocked_run:
        mocked_run.side_effect = Exception("test panic error")
        main("__main__")
        mocked_print.assert_called_with(Utils.PANIC_ERROR)
