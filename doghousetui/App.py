import sys
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
        #self.__app_status = AppStatus()
        self.__login_menu = Menu.Builder(Description(Utils.LOGIN_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.LOGIN_ENTRY, on_selected=lambda: self.__login())) \
            .with_entry(
            MenuEntry.create('2', Utils.CONTINUE_WITHOUT_LOGIN_ENTRY, on_selected=self.__continue_without_login)) \
            .with_entry(MenuEntry.create('3', Utils.REGISTER_ENTRY, on_selected=self.__register)) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__logged_user_menu = Menu.Builder(Description(Utils.USER_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(MenuEntry.create('2', Utils.SHOW_PREFERENCES_ENTRY, on_selected=self.__show_preferences)) \
            .with_entry(MenuEntry.create('3', Utils.ADD_PREFERENCE_ENTRY, on_selected=self.__add_preference)) \
            .with_entry(MenuEntry.create('4', Utils.REMOVE_PREFERENCE_ENTRY, on_selected=self.__remove_preference)) \
            .with_entry(
            MenuEntry.create('0', Utils.LOGOUT_ENTRY, is_exit=True, on_selected= lambda: self.__logout())) \
            .build()

        self.__logged_admin_menu = Menu.Builder(Description(Utils.ADMIN_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(MenuEntry.create('2', Utils.ADD_DOG_ENTRY, on_selected=self.__add_dog)) \
            .with_entry(MenuEntry.create('3', Utils.REMOVE_DOG_ENTRY, on_selected=self.__remove_dog)) \
            .with_entry(
            MenuEntry.create('0', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: self.__logout())) \
            .build()

        self.__not_logged_menu = Menu.Builder(Description('generic user Menu')) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

    def __read_username(self) -> str:
        username:str = input("Insert username: ")
        validate("login username", username, min_len=2, max_len=30, custom=pattern(r"[a-zA-Z0-9]*"))
        return username

    def __read_password(self) -> str:
        password: str = input("Insert password: ")
        validate("login password", password, min_len=8, max_len=30, custom=pattern(r"[a-zA-Z0-9@!#]*"))
        return password

    def login_request(self, username: str, password: str) -> Response:
        return requests.post(Utils.API_SERVER_LOGIN, params={"username": username, "password": password})

    def logout_request(self) -> Response:
        return requests.post(Utils.API_SERVER_LOGOUT, params={"token": self.__token})

    def __login_parse_response(self, response: Response, username: str):

        if 200 == response.status_code:

            json_response = response.json()
            try:
                self.__token = Token(json_response["session_token"])
            except (ValidationError):
                print(Utils.INVALID_CREDENTIALS)
                return
            print(Utils.LOGGED_IN_MESSAGE % (username))
            if json_response[Utils.RESPONSE_ROLE_KEY] == Utils.RESPONSE_USER_ROLE_USER_VALUE:
                self.__logged_user_menu.run()
            elif json_response[Utils.RESPONSE_ROLE_KEY] == Utils.RESPONSE_USER_ROLE_ADMIN_VALUE:
                self.__logged_admin_menu.run()
        else:
            print(Utils.LOGIN_ERROR)

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
        try:
            response: Response = self.login_request(username, password)
        except ConnectionError:
            print(Utils.CONNECTION_ERROR)
            return

        self.__login_parse_response( response, username)


    def __logout(self):
        try:
            #self.__app_status.logout()
            self.__token = Utils.DEFAULT_TOKEN_VALUE
            response: Response = self.logout_request()
            print(Utils.LOGOUT_MESSAGE)
        except ConnectionError:
            print(Utils.CONNECTION_ERROR)

    def __continue_without_login(self):
        try:
            #self.__app_status.continue_without_login()
            self.__not_logged_menu.run()
        except ValidationError:
            print(Utils.LOGOUT_WITHOUT_FIRST_LOGIN)

    def __register(self):

        # print("Insert username: ")
        # print("Insert password: ")
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

    def __close_app(self):
        print(Utils.EXIT_MESSAGE)

    def run(self):
        self.__login_menu.run()


# @typechecked
# class AppStatus:
#     class LoginStatus(Enum):
#         NOT_LOGGED = 1
#         USER = 2
#         ADMIN = 3
#         USER_WITHOUT_LOGIN = 4
#
#     __login_status: LoginStatus
#
#     def __init__(self):
#         self.__login_status = AppStatus.LoginStatus.NOT_LOGGED
#
#     #TODO should raise invalid state, not validation error
#     def login(self):
#         validate(self.__login_status, custom=lambda v: v == AppStatus.LoginStatus.NOT_LOGGED)
#
#
#     def logout(self):
#         validate(self.__login_status, custom=lambda v: v != AppStatus.LoginStatus.NOT_LOGGED)
#         self.__login_status = AppStatus.LoginStatus.NOT_LOGGED
#
#     def register(self):
#         validate(self.__login_status, custom=lambda v: v != AppStatus.LoginStatus.NOT_LOGGED)
#
#     def continue_without_login(self):
#         #validate(self.__login_status, custom=lambda v: v == AppStatus.LoginStatus.NOT_LOGGED)
#         self.__login_status = AppStatus.LoginStatus.USER_WITHOUT_LOGIN
#
#     def is_logged_as_admin(self):
#         return self.__login_status == AppStatus.LoginStatus.ADMIN
#
#     def is_logged_as_user(self):
#         return self.__login_status == AppStatus.LoginStatus.USER

    

def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
