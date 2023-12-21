import pytest
from unittest.mock import patch, call, Mock
from valid8 import ValidationError

from doghousetui import Utils
from doghousetui.credentials import Token, Username, Email, Password


class Test_Token:
    @pytest.fixture
    def valid_tokens(self):
        return ["asd8g8asf9af89d9gas9f8gsjabhka123445ywef", "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b", "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "1111111111111111111111111111111111111111"]


    @pytest.fixture
    def invalid_tokens(self):
        return ["", "39lengthf9af89d9gas9f8gsjabhka123445ywe","41lenght000000000000000000000000000000000","@qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "11111111111111111111111111111111111#1111"]


    def test_creation_of_valid_token(self,valid_tokens):
        for t in valid_tokens:
            Token(t)


    def test_creation_of_invalid_token(self,invalid_tokens):
        with pytest.raises(ValidationError):
            for t in invalid_tokens:
                Token(t)

    def test_creation_of_Token_with_default_value(self):
        token = Token()
        assert token.value == Utils.DEFAULT_TOKEN_VALUE

    def test_equality_of_tokens(self,valid_tokens):
        token = Token()
        token2 = Token()
        assert token == token2
        for i in valid_tokens:
            token = Token(i)
            token2 = Token(i)
            assert token == token2

    def test_not_equality_of_tokens(self,valid_tokens):
        default_token = Token()
        for i in valid_tokens:
            token = Token(i)
            assert token != default_token

    def test_hash_of_tokens(self,valid_tokens):
        token = Token()
        token2 = Token()
        assert token.__hash__() == token2.__hash__()
        for i in valid_tokens:
            token = Token(i)
            token2 = Token(i)
            assert token.__hash__() == token2.__hash__()

class Test_Username:
    @pytest.fixture
    def valid_usernames(self):
        return ['user22', '01', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', "paoloapaoloaaapoalo"]

    @pytest.fixture
    def invalid_usernames(self):
        return ['a', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'abcs#?', 'localhost@hi']
    def test_valid_username_print_its_value(self,  valid_usernames):
        for i in valid_usernames:
            assert str(Username(i)) == i


    def test_username_throws_validation_error_when_invalid_input(self, valid_usernames, invalid_usernames):
        for i in valid_usernames:
            Username(i)
        for i in invalid_usernames:
            with pytest.raises(ValidationError):
                Username(i)

class Test_Email:
        @pytest.fixture
        def valid_emails(self):
            return ['aaa@aaa', "", 'email+@pip.com', 'valid@em.a', "+@1.1"]

        @pytest.fixture
        def valid_email(self):
            return 'aaa@aaa'

        @pytest.fixture
        def invalid_emails(self):
            return ['aaaaaa', 'email+#ù@pip.com', 'valid@e.m.a', "email@b."]

        def test_email_can_be_created_empty_with_empty_default(self):
            assert Email().value == ""

        def test_email_throws_validation_error_when_invalid_input(self, valid_emails, invalid_emails):
            for i in valid_emails:
                Email(i)
            for i in invalid_emails:
                with pytest.raises(ValidationError):
                    Email(i)

        def test_email_is_default_value(self, valid_email):
            if Email().value == "":
                assert Email().is_default()
                email = Email(valid_email)
                assert email.is_default() == False


class Test_Password:
        @pytest.fixture
        def valid_passwords(self):
            return ["aaaaaaaa", "123###78", "PASSWORDASAASD@@@ASDAS", "a!aaaaaaaaaasas9as89a89a89a98a"]

        @pytest.fixture
        def invalid_passwords(self):
            return ["aaaaaaa", "12?3###78", "PASSWORDASAASD@@@ASD'AS", "a!aaasasdasdasdas9as89a8989a98a"]

        def test_password_throws_validation_error_when_invalid_input(self, valid_passwords, invalid_passwords):
            for i in valid_passwords:
                Password(i)
            for i in invalid_passwords:
                with pytest.raises(ValidationError):
                    Password(i)

        def test_password_equality_when_values_are_equal(self, valid_passwords):
            for i in range(len(valid_passwords)):
                assert Password(valid_passwords[i]) == Password(valid_passwords[i])
                if i+1 < len(valid_passwords):
                    assert Password(valid_passwords[i]) != Password(valid_passwords[i+1])
                if i-1 > 0:
                    assert Password(valid_passwords[i]) != Password(valid_passwords[i-1])