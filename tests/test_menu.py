import pytest
from unittest.mock import patch, call, Mock
from valid8 import ValidationError

from doghousetui.Menu import Description, Key, MenuEntry, Menu


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


@pytest.fixture
def menu_entry():
    return MenuEntry.create("1", "description")
@pytest.fixture
def exit_menu_entry():
    return MenuEntry.create("0", "description", is_exit=True)

def test_menu_builder_cannot_create_empty_menu():
    menu_builder = Menu.Builder(Description('a description'))
    with pytest.raises(ValidationError):
        menu_builder.build()


def test_menu_builder_cannot_create_menu_with_no_exit(menu_entry):
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(menu_entry)
    with pytest.raises(ValidationError):
        menu_builder.build()

def test_menu_builder_cannot_create_menu_with_duplicate_entries(menu_entry):
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(menu_entry)
    with pytest.raises(ValidationError):
        menu_builder.with_entry(menu_entry)

def test_menu_builder_create_menu_with__exit(exit_menu_entry):
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(exit_menu_entry)
    menu_builder.build()

def test_menu_builder_cannot_call_two_times_build():
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(MenuEntry.create('0', 'description', is_exit=True))
    menu_builder.build()
    with pytest.raises(ValidationError):
        menu_builder.build()

@pytest.fixture
def two_entries_menu():
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(MenuEntry.create('0', 'entry 1', is_exit=True, on_selected=lambda : print("entry 1 selected")))
    menu_builder.with_entry(MenuEntry.create('1', 'entry 2', is_exit=False, on_selected=lambda: print("Bye!")))
    return menu_builder.build()


@patch('builtins.input', side_effect=['1', '0'])
@patch('builtins.print')
def test_menu_selection_call_on_selected(mocked_print, mocked_input, two_entries_menu):
    menu = Menu.Builder(Description('a description'))\
        .with_entry(MenuEntry.create('1', 'first entry', on_selected=lambda: print('first entry selected')))\
        .with_entry(MenuEntry.create('0', 'exit', is_exit=True))\
        .build()
    menu.run()
    mocked_print.assert_any_call('first entry selected')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['-1', '0'])
@patch('builtins.print')
def test_menu_selection_on_wrong_key(mocked_print, mocked_input):
    menu = Menu.Builder(Description('a description'))\
        .with_entry(MenuEntry.create('1', 'first entry', on_selected=lambda: print('first entry selected')))\
        .with_entry(MenuEntry.create('0', 'exit', is_exit=True, on_selected=lambda : print('Bye!')))\
        .build()
    menu.run()
    mocked_print.assert_any_call('Invalid selection. Please, try again...')
    mocked_print.assert_any_call('Bye!')
    mocked_input.assert_called()
