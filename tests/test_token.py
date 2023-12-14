import pytest
from unittest.mock import patch, call, Mock
from valid8 import ValidationError

from doghousetui import Utils
from doghousetui.Token import Token


@pytest.fixture
def valid_tokens():
    return ["asd8g8asf9af89d9gas9f8gsjabhka123445ywef", "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b", "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "1111111111111111111111111111111111111111"]


@pytest.fixture
def invalid_tokens():
    return ["", "39lengthf9af89d9gas9f8gsjabhka123445ywe","41lenght000000000000000000000000000000000","@qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "11111111111111111111111111111111111#1111"]


def test_creation_of_valid_token(valid_tokens):
    for t in valid_tokens:
        Token(t)


def test_creation_of_invalid_token(invalid_tokens):
    with pytest.raises(ValidationError):
        for t in invalid_tokens:
            Token(t)

def test_creation_of_Token_with_default_value():
    token = Token()
    assert token.value == Utils.DEFAULT_TOKEN_VALUE

def test_equality_of_tokens(valid_tokens):
    token = Token()
    token2 = Token()
    assert token == token2
    for i in valid_tokens:
        token = Token(i)
        token2 = Token(i)
        assert token == token2

def test_not_equality_of_tokens(valid_tokens):
    default_token = Token()
    for i in valid_tokens:
        token = Token(i)
        assert token != default_token

def test_hash_of_tokens(valid_tokens):
    token = Token()
    token2 = Token()
    assert token.__hash__() == token2.__hash__()
    for i in valid_tokens:
        token = Token(i)
        token2 = Token(i)
        assert token.__hash__() == token2.__hash__()
