import sys
from dataclasses import dataclass

from requests import Response
from typeguard import typechecked
from urllib3.exceptions import NewConnectionError
from valid8 import validate, ValidationError
from doghousetui import Utils
from doghousetui.Menu import Menu, Description, MenuEntry
from enum import Enum
import getpass
from doghousetui.Token import Token
import requests

from validation.regex import pattern


class App:
    # menu
    def __init__(self):
        self.__token = Token()
        self.__running = True
        #self.__app_status = AppStatus()
        self.__login_menu = Menu.Builder(Description(Utils.LOGIN_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.LOGIN_ENTRY, is_exit=True, on_selected=lambda: self.__login())) \
            .with_entry(
            MenuEntry.create('2', Utils.CONTINUE_WITHOUT_LOGIN_ENTRY, is_exit=True, on_selected=lambda: self.__continue_without_login())) \
            .with_entry(MenuEntry.create('3', Utils.REGISTER_ENTRY, is_exit=True, on_selected=lambda: self.__register())) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__logged_user_menu = Menu.Builder(Description(Utils.USER_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(MenuEntry.create('2', Utils.SHOW_PREFERENCES_ENTRY, on_selected=self.__show_preferences)) \
            .with_entry(MenuEntry.create('3', Utils.ADD_PREFERENCE_ENTRY, on_selected=self.__add_preference)) \
            .with_entry(MenuEntry.create('4', Utils.REMOVE_PREFERENCE_ENTRY, on_selected=self.__remove_preference)) \
            .with_entry(
            MenuEntry.create('5', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: self.__logout())) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected= lambda: self.__close_app())) \
            .build()

        self.__logged_admin_menu = Menu.Builder(Description(Utils.ADMIN_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(MenuEntry.create('2', Utils.ADD_DOG_ENTRY, on_selected=self.__add_dog)) \
            .with_entry(MenuEntry.create('3', Utils.REMOVE_DOG_ENTRY, on_selected=self.__remove_dog)) \
            .with_entry(
            MenuEntry.create('4', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: self.__logout())) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__not_logged_menu = Menu.Builder(Description(Utils.GENERIC_USER_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=self.__show_dogs)) \
            .with_entry(
            MenuEntry.create('2', Utils.BACK_TO_LOGIN_MENU_ENTRY, is_exit=True, on_selected=lambda: self.__switch_menu(self.__login_menu))) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__current_menu: Menu = self.__login_menu

    def __read_username(self, message) -> str:
        username: str = input(message)
        validate("validation username", username, min_len=2, max_len=30, custom=pattern(r"[a-zA-Z0-9]*"))
        return username

    def __read_password(self, message) -> str:
        password: str = getpass.getpass(message)
        validate("validaton password", password, min_len=8, max_len=30, custom=pattern(r"[a-zA-Z0-9@!#]*"))
        return password

    def make_login_request(self, username: str, password: str) -> Response:
        return requests.post(Utils.API_SERVER_LOGIN, json={"username": username, "password": password})

    def make_logout_request(self) -> Response:
        return requests.post(Utils.API_SERVER_LOGOUT)

    def make_registration_request(self, username: str, password: str) -> Response:
        return requests.post(Utils.API_SERVER_REGISTER, json={"username": username, "password1": password, "password2": password})

    def make_role_request(self) -> Response:
        return requests.get(Utils.API_SERVER_LOGIN_ROLE, headers={'Authorization': f'Token {self.__token}'})

    def __login(self):
        try:
            username: str = self.__read_username(Utils.INSERT_USERNAME_MESSAGE)
        except ValidationError:
            print(Utils.INVALID_USERNAME_ERROR)
            return
        try:
            password: str = self.__read_password(Utils.INSERT_PASSWORD_MESSAGE)
        except ValidationError:
            print(Utils.INVALID_PASSWORD_ERROR)
            return

        response: Response = self.make_login_request(username, password)

        if 200 == response.status_code:
            json_response = response.json()
            try:
                self.__token = Token(json_response["key"])
            except ValidationError:
                App.__print_login_errors(json_response)
                return

            response_role: Response = self.make_role_request()

            role = response_role.json()[Utils.RESPONSE_ROLE_KEY]

            print(Utils.LOGGED_IN_MESSAGE % (username))
            if role == Utils.RESPONSE_USER_ROLE_USER_VALUE:
                self.__switch_menu(self.__logged_user_menu)
            elif role == Utils.RESPONSE_USER_ROLE_ADMIN_VALUE:
                self.__switch_menu(self.__logged_admin_menu)
        else:
            print(Utils.LOGIN_ERROR)
            App.__print_login_errors(response.json())
            self.__switch_menu(self.__login_menu)


    def __logout(self):
        response: Response = self.make_logout_request()
        if 200 == response.status_code:
            self.__token = Utils.DEFAULT_TOKEN_VALUE
            print(Utils.LOGOUT_MESSAGE)
            self.__switch_menu(self.__login_menu)
        else:
            print(Utils.LOGOUT_ERROR)

    def __continue_without_login(self):
        self.__current_menu = self.__not_logged_menu

    def __read_registration_data(self) -> tuple:
        invalid: bool = True
        username:str = ''
        password1:str = ''
        password2:str = ''
        while invalid:
            invalid = False
            try:
                username: str = self.__read_username(Utils.INSERT_USERNAME_MESSAGE)
            except ValidationError:
                print(Utils.INVALID_USERNAME_ERROR)
                invalid = True
                continue
            try:
                password1: str = self.__read_password(Utils.INSERT_PASSWORD_MESSAGE)
            except ValidationError:
                print(Utils.INVALID_PASSWORD_ERROR)
                invalid = True
                continue
            try:
                password2: str = self.__read_password(Utils.REPEAT_PASSWORD_MESSAGE)
                if password1 != password2:
                    print(Utils.REGISTRATION_PASSWORDS_DO_NOT_COINCIDE)
                    invalid = True
            except ValidationError:
                invalid = True
            return username, password1, invalid

    @staticmethod
    def __print_error_message_list(error_list):
        for error_message in error_list:
            print('\t', error_message)

    @staticmethod
    def __print_registration_errors(json):
        if 'non_field_errors' in json:
            App.__print_error_message_list(json['non_field_errors'])
        if 'username' in json:
            App.__print_error_message_list(json['username'])

    @staticmethod
    def __print_login_errors(json):
        if 'non_field_errors' in json:
            App.__print_error_message_list(json['non_field_errors'])

    def __register(self):
        username, password, invalid = self.__read_registration_data()
        if not invalid:
            response: Response = self.make_registration_request(username, password)
            if response.status_code == 204:
                print(Utils.REGISTRATION_SUCCEEDED_MESSAGE)
            else:
                print(Utils.REGISTRATION_ERROR)
                App.__print_registration_errors(response.json())
            self.__switch_menu(self.__login_menu)

    def __show_dogs(self):
        pass

    def __show_preferences(self):
        pass

    def __add_preference(self):
        pass

    def __add_dog(self):
        #print(Utils.REQUIRE_INPUT_DOG_DATA)
        pass

    def __remove_dog(self):
        pass

    def __remove_preference(self):
        pass


    def __close_app(self):
        print(Utils.EXIT_MESSAGE)
        self.__running = False

    def __switch_menu(self, menu):
        self.__current_menu = menu
        #self.run()

    def run(self):
        while self.__running:
            self.__current_menu.run()



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
