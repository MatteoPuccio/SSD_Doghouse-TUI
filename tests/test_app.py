from unittest.mock import patch

import pytest
from valid8 import ValidationError

from doghousetui.App import App


#@patch('builtins.input', side_effect=['1', 'username', 'password'])
#@patch('builtins.print')
#def test_menu_login_success():
#    app = App()
#    app.run()
@pytest.fixture
def invalid_usernames():
    return ['a', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'abcs#?', 'localhost@hi']

@pytest.fixture
def valid_usernames():
    return ['user22', '01', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']

@patch('builtins.input', side_effect=['1', '1'])
def test_easy(mocked_input):
    app: App = App()

    with pytest.raises(ValidationError):
        app.login()
        #mocked_input.assert_any_call()

#@patch('builtins.print')
def test_read_username_receives_invalid_username(invalid_usernames):
    for username in invalid_usernames:
        app: App = App()
        with patch('builtins.input', side_effect=["1", username]):
            with pytest.raises(ValidationError):
                app.run()


@patch('builtins.input', side_effect=[''])
@patch('builtins.print')
def test_read_username_receives_valid_username(invalid_usernames):
    pass