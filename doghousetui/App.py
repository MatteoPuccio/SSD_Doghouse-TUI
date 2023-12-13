from dataclasses import dataclass

from requests import Response
from typeguard import typechecked
from valid8 import validate, ValidationError
from doghousetui import Utils
from doghousetui.Menu import Menu, Description, MenuEntry
from enum import Enum
from getpass import getpass
from doghousetui.Token import Token
import requests

from validation.regex import pattern


class App:
    # menu
    def __init__(self):
        self.__token = Token()
        self.__app_status = AppStatus()
        self.__login_menu = Menu.Builder(Description(Utils.LOGIN_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.LOGIN_ENTRY, on_selected=lambda: self.__login())) \
            .with_entry(
            MenuEntry.create('2', Utils.CONTINUE_WITHOUT_LOGIN_ENTRY, on_selected=self.__continue_without_login)) \
            .with_entry(MenuEntry.create('3', Utils.REGISTER_ENTRY, on_selected=self.__register)) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: print(Utils.EXIT_MESSAGE))) \
            .build()

        self.__logged_user_menu = Menu.Builder(Description(Utils.USER_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(MenuEntry.create('2', Utils.SHOW_PREFERENCES_ENTRY, on_selected=self.__show_preferences)) \
            .with_entry(MenuEntry.create('3', Utils.ADD_PREFERENCE_ENTRY, on_selected=self.__add_preference)) \
            .with_entry(MenuEntry.create('4', Utils.REMOVE_PREFERENCE_ENTRY, on_selected=self.__remove_preference)) \
            .with_entry(
            MenuEntry.create('0', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: print(Utils.LOGOUT_MESSAGE))) \
            .build()

        self.__logged_admin_menu = Menu.Builder(Description(Utils.ADMIN_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(MenuEntry.create('2', Utils.ADD_DOG_ENTRY, on_selected=self.__add_dog)) \
            .with_entry(MenuEntry.create('3', Utils.REMOVE_DOG_ENTRY, on_selected=self.__remove_dog)) \
            .with_entry(
            MenuEntry.create('0', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: print(Utils.LOGOUT_MESSAGE))) \
            .build()

        self.__not_logged_menu = Menu.Builder(Description('generic user Menu')) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: print(Utils.EXIT_MESSAGE))) \
            .build()

    def __read_username(self) -> str:
        username:str = input("Insert username: ")
        validate("login username", username, min_len=2, max_len=30, custom=pattern(r"[a-zA-Z0-9]*"))
        return username

    def __read_password(self) -> str:
        password: str = input("Insert password: ")
        validate("login password", password, min_len=8, max_len=30, custom=pattern(r"[a-zA-Z0-9@!#]*"))
        return password


    @staticmethod
    def login_request( username: str, password: str) -> Response:
        return requests.post(Utils.API_SERVER_LOGIN, params={"username": username, "password": password})

    def __login_parse_response(self, response: Response, username: str):

        if 200 == response.status_code:

            json_response = response.json()
            try:
                pass
                self.__token = Token(json_response["session_token"])
            except (ValidationError):
                print(Utils.INVALID_CREDENTIALS)
                return
            except (ConnectionError):
                print(Utils.CONNECTION_ERROR)
                return
            print(Utils.LOGGED_IN_MESSAGE % (username))
            self.__logged_user_menu.run()
        else:
            print(Utils.SERVER_ERROR_STATUS_CODE % (response.status_code, "log in"))

    def __login(self):
        try:
            username: str = self.__read_username()
        except ValidationError:
            print(Utils.INVALID_USERNAME_ERROR)
            return
        try:
            password: str = self.__read_password()
        except ValidationError:
            print(Utils.INVALID_PASSWORD_ERROR)
            return

        response: Response = App.login_request(username, password)

        self.__login_parse_response( response, username)


    def __logout(self):
        pass
        # try:
        #    self.__app_status.logout()
        #    self.__token = Utils.DEFAULT_TOKEN_VALUE
        #    if self.__app_status.is_logged_as_user():
        #        self.__logged_user_menu.stop()
        #    else:
        #        self.__logged_admin_menu.stop()
        # except Exception:
        #    pass

    def __continue_without_login(self):
        self.__not_logged_menu.run()

    def __register(self):

        # print("Insert username: ")
        # print("Insert password: ")
        pass

    def __continue_without_login(self):
        pass

    def __show_dogs(self):
        pass

    def __show_preferences(self):
        pass

    def __add_preference(self):
        pass

    def __add_dog(self):
        pass

    def __remove_dog(self):
        pass

    def __remove_preference(self):
        pass

    def run(self):
        self.__login_menu.run()


@typechecked
class AppStatus:
    class LoginStatus(Enum):
        NOT_LOGGED = 1
        USER = 2
        ADMIN = 3

    __login_status: LoginStatus

    def __init__(self):
        self.__login_status = AppStatus.LoginStatus.NOT_LOGGED

    def login(self):
        validate(self.__login_status, custom=lambda v: v == AppStatus.LoginStatus.NOT_LOGGED)
    def logout(self):
        validate(self.__login_status, custom=lambda v: v != AppStatus.LoginStatus.NOT_LOGGED)

    def register(self):
        validate(self.__login_status, custom=lambda v: v != AppStatus.LoginStatus.NOT_LOGGED)

    # def is_logged_as_admin(self):
    #    return self.__login_status == AppStatus.LoginStatus.ADMIN

    # def is_logged_as_user(self):
    #    return self.__login_status == AppStatus.LoginStatus.USER


def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
