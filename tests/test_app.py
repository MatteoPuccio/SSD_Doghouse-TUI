import builtins
from getpass import getpass
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
                if Utils.NOT_LOGGED_MENU_DESCRIPTION in a:
                    printed = True
                    break
        assert printed



@mock.patch("builtins.print")
def test_app_login_valid_user_credentials_show_user_menu(mocked_print, valid_password, valid_username, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '0', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post:
                app: App = App()
                response = Mock(status_code=200)
                response.json.return_value = {"session_token": valid_token,
                                              Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                mocked_post.return_value = response
                app.run()
                assert mocked_return_args_partial_contains_string(mocked_print, Utils.USER_MENU_DESCRIPTION)


@mock.patch("builtins.print")
def test_app_login_valid_user_credentials_show_admin_menu(mocked_print, valid_password, valid_username, valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '0', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with patch.object(doghousetui.App.App, 'make_login_request') as mocked_post:
                app: App = App()
                response = Mock(status_code=200)
                response.json.return_value = {"session_token": valid_token,
                                              Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_ADMIN_VALUE}
                mocked_post.return_value = response
                app.run()
                assert mocked_return_args_partial_contains_string(mocked_print, Utils.ADMIN_MENU_DESCRIPTION)


@mock.patch("builtins.print")
def test_app_logout_after_login_as_user_shows_login_menu_again(mocked_print, valid_username, valid_password,
                                                               valid_token):
    with patch('builtins.input', side_effect=['1', valid_username, '5', '0']):
        with patch('getpass.getpass', side_effect=[valid_password]):
            with mock.patch.object(doghousetui.App.App, 'make_login_request') as mocked_post_login:
                with patch.object(doghousetui.App.App, 'make_role_request') as mocked_post_role:
                    app: App = App()
                    response_login = Mock(status_code=200)
                    response_login.json.return_value = {"key": valid_token,
                                                        Utils.RESPONSE_ROLE_KEY: Utils.RESPONSE_USER_ROLE_USER_VALUE}
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
    with patch('builtins.input', side_effect=['1', valid_username, '4', '0']):
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
    with patch('builtins.input', side_effect=['1', valid_username, valid_email, '5', '0']):
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
    with patch('builtins.input', side_effect=['2', '2', '0']):
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
                        response_delete = Mock(status_code=200)
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


# @mock.patch.object(doghousetui.App.App, 'make_registration_request')
# def test_make_logout_request_makes_sends_logout_request(make_registration_request, requests_mock):
#     app: App = App()
#     app.make_logout_request()
#     assert requests_mock.requests_post.called()
