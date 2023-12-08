import pytest
from unittest.mock import patch, call, Mock
from valid8 import ValidationError
from doghousetui.Menu import Description, Key, MenuEntry


def test_description_length_1000_chars():
    Description("a"*1000)
    with pytest.raises(ValidationError):
        Description("a"*1001)


def test_description_must_be_string():
    Description('ok')
    with pytest.raises(TypeError):
        Description(0)
    with pytest.raises(TypeError):
        Description(None)


def test_description_must_be_non_empty_string():
    Description('correct')
    with pytest.raises(ValidationError):
        Description('')

@pytest.fixture
def special_char():
    return ['\n', '\r', '*', '^', '$', '@', '#']


def test_description_must_not_contain_special_chars(special_char):
    with pytest.raises(ValidationError):
        Description(special_char)


def test_key_cannot_be_empty():
    with pytest.raises(ValidationError):
        Key('')


def test_key_cannot_exceed_10_chars():
    with pytest.raises(ValidationError):
        Key('1'*11)


def test_key_cannot_contain_special_chars(special_char):
    with pytest.raises(ValidationError):
        Key(special_char)

def test_key_cannot_contain_letters():
    for i in ["aaa001", "00n2", "0az03", "1234b","2e","k"]:
        with pytest.raises(ValidationError):
            Key(i)

def test_key_cannot_contain_letters():
    with pytest.raises(ValidationError):
        Key("")

def test_key_value_cannot_be_an_integer():
    with pytest.raises(TypeError):
        Key(1)

    with pytest.raises(TypeError):
        Key(1.5)

def test_key_can_start_with_0_only_if_length_1():
    Key("0")
    with pytest.raises(ValidationError):
        Key("01")

def test_menu_entry_cannot_be_created_by_constructor():
    key = Mock()
    description = Mock()
    on_selected = Mock()
    with pytest.raises(ValidationError):
        MenuEntry(key,  description, on_selected())

@pytest.fixture
def key():
    return Key("0")

@pytest.fixture
def description():
    return Description("description")


def test_menu_entry_must_be_create_by_create_method():
    on_selected = Mock()
    MenuEntry.create("0", "description", on_selected())





