import sys
from dataclasses import dataclass
from typing import Any, Callable

from requests import Response
from typeguard import typechecked
from urllib3.exceptions import NewConnectionError
from valid8 import validate, ValidationError
from doghousetui import Utils
from doghousetui.Menu import Menu, Description, MenuEntry
from enum import Enum
import getpass
import requests

from doghousetui.credentials import Username, Password, Token, Email
from doghousetui.domain import DogId, Dog, DogBirthInfo, DogDescription, PictureUrl, Dogname, Date

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
            MenuEntry.create('2', Utils.CONTINUE_WITHOUT_LOGIN_ENTRY, is_exit=True,
                             on_selected=lambda: self.__continue_without_login())) \
            .with_entry(
            MenuEntry.create('3', Utils.REGISTER_ENTRY, is_exit=True, on_selected=lambda: self.__register())) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__logged_user_menu = Menu.Builder(Description(Utils.USER_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=lambda: self.__show_dogs())) \
            .with_entry(
            MenuEntry.create('2', Utils.SHOW_PREFERENCES_ENTRY, on_selected=lambda: self.__show_preferences())) \
            .with_entry(MenuEntry.create('3', Utils.ADD_PREFERENCE_ENTRY, on_selected=lambda: self.__add_preference())) \
            .with_entry(
            MenuEntry.create('4', Utils.REMOVE_PREFERENCE_ENTRY, on_selected=lambda: self.__remove_preference())) \
            .with_entry(
            MenuEntry.create('5', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: self.__logout())) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__logged_admin_menu = Menu.Builder(Description(Utils.ADMIN_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=lambda: self.__show_dogs())) \
            .with_entry(MenuEntry.create('2', Utils.ADD_DOG_ENTRY, on_selected=self.__add_dog)) \
            .with_entry(MenuEntry.create('3', Utils.REMOVE_DOG_ENTRY, on_selected=lambda: self.__remove_dog())) \
            .with_entry(
            MenuEntry.create('4', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: self.__logout())) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__not_logged_menu = Menu.Builder(Description(Utils.GENERIC_USER_MENU_DESCRIPTION)) \
            .with_entry(MenuEntry.create('1', Utils.SHOW_DOGS_ENTRY, on_selected=lambda: self.__show_dogs())) \
            .with_entry(
            MenuEntry.create('2', Utils.BACK_TO_LOGIN_MENU_ENTRY, is_exit=True,
                             on_selected=lambda: self.__switch_menu(self.__login_menu))) \
            .with_entry(
            MenuEntry.create('0', Utils.EXIT_ENTRY, is_exit=True, on_selected=lambda: self.__close_app())) \
            .build()

        self.__current_menu: Menu = self.__login_menu

    def __read_username(self, message) -> Username:
        username: str = input(message)
        return Username(username)

    def __read_email(self, message) -> Email:
        email: str = input(message)
        if email == "":
            return Email()
        else:
            return Email(email)


    def __read_password(self, message) -> Password:
        password: str = getpass.getpass(message)
        return Password(password)

    def make_login_request(self, username: Username, password: Password) -> Response:
        return requests.post(Utils.API_SERVER_LOGIN, json={"username": username, "password": password})

    def make_logout_request(self) -> Response:
        return requests.post(Utils.API_SERVER_LOGOUT)

    def make_registration_request(self, username: Username, email:Email, password: Password) -> Response:
        return requests.post(Utils.API_SERVER_REGISTER, json={"username": username.value, "email":email, "password1": password.value, "password2": password.value})

    def make_role_request(self) -> Response:
        return requests.get(Utils.API_SERVER_LOGIN_ROLE, headers={'Authorization': f'Token {self.__token}'})

    def make_dogs_request(self) -> Response:
        return requests.get(Utils.API_SERVER_DOGS)

    def __login(self):
        try:
            username: Username = self.__read_username(Utils.INSERT_USERNAME_MESSAGE)
        except ValidationError:
            print(Utils.INVALID_USERNAME_ERROR)
            return
        try:
            password: Password = self.__read_password(Utils.INSERT_PASSWORD_MESSAGE)
        except ValidationError:
            print(Utils.INVALID_PASSWORD_ERROR)
            return

        response: Response = self.make_login_request(username, password)

        if 200 == response.status_code:
            json_response = response.json()
            try:
                self.__token = Token(json_response["key"])
            except ValidationError:
                print(Utils.INVALID_TOKEN)
                return

            response_role: Response = self.make_role_request()

            role = response_role.json()[Utils.RESPONSE_ROLE_KEY]

            print(Utils.LOGGED_IN_MESSAGE % username)
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
        self.__switch_menu(self.__not_logged_menu)

    def __repeat_until_valid(self, message: str, error_message:str, function: Callable[[str], Any]) -> Any:
        valid = False
        while not valid:
            try:
                result = function(message)
                valid = True
                return result
            except ValidationError:
                print(error_message)
                valid = False



    def __read_registration_data(self) -> tuple:
        username: Username = self.__repeat_until_valid(Utils.INSERT_USERNAME_MESSAGE, Utils.INVALID_USERNAME_ERROR, self.__read_username)
        email: Email = self.__repeat_until_valid(Utils.INSERT_EMAIL_MESSAGE, Utils.INVALID_EMAIL_ERROR, self.__read_email)
        password1: Password = self.__repeat_until_valid(Utils.INSERT_PASSWORD_MESSAGE, Utils.INVALID_PASSWORD_ERROR, self.__read_password)
        invalid = False
        try:
            password2: Password = self.__read_password(Utils.INSERT_PASSWORD_MESSAGE)
            if password1 != password2:
                print(Utils.REGISTRATION_PASSWORDS_DO_NOT_COINCIDE)
                invalid = True
        except ValidationError:
            print(Utils.REGISTRATION_PASSWORDS_DO_NOT_COINCIDE)
            invalid = True
        return username, email, password1, invalid

    @staticmethod
    def __print_error_message(errors):
        for error in errors:
            print(error)

    @staticmethod
    def __print_registration_errors(json):
        if 'non_field_errors' in json:
            App.__print_error_message(json['non_field_errors'])
        if 'username' in json:
            App.__print_error_message(json['username'])

    @staticmethod
    def __print_login_errors(json):
        print(json)
        if 'non_field_errors' in json:
            App.__print_error_message(json['non_field_errors'])

    def __register(self):
        username, email, password, invalid = self.__read_registration_data()
        if not invalid:
            try:
                response: Response = self.make_registration_request(username, email, password)
            except:
                print(Utils.CONNECTION_ERROR)
                self.__switch_menu(self.__login_menu)
                return
            if response.status_code == 204:
                print(Utils.REGISTRATION_SUCCEEDED_MESSAGE)
            else:
                App.__print_registration_errors(response.json())
            self.__switch_menu(self.__login_menu)

    def make_dog_remove_request(self, dog_id: DogId) -> Response:
        return requests.delete(f'{Utils.API_SERVER_DOGS}{dog_id.value}/',
                               headers={'Authorization': f'Token {self.__token}'})

    def __show_dogs(self):
        try:
            dogs_response: Response = self.make_dogs_request()
        except Exception:
            print(Utils.CONNECTION_ERROR)
            return
        if dogs_response.status_code == 200:
            dogs = dogs_response.json()
            all_dogs = []
            for dog_json in dogs:
                dog = self.__create_dog_from_json(dog_json)
                all_dogs.append(dog)
        else:
            print(Utils.SHOW_DOGS_ERROR)
        if len(all_dogs) <= Utils.SHOW_DOGS_BATCH_SIZE:
            for dog in all_dogs:
                print(dog)
        else:
            wants_more: bool = True
            start_idx = 0
            while wants_more:
                for i in range(start_idx, start_idx + Utils.SHOW_DOGS_BATCH_SIZE):
                    if i < len(dogs):
                        print(dogs[i])

                if start_idx + Utils.SHOW_DOGS_BATCH_SIZE < len(dogs):
                    selection: str = input(Utils.WANTS_MORE_QUESTION)
                    if selection.lower() != Utils.WANTS_MORE_YES_ANSWER:
                        wants_more = False
                else:
                    wants_more = False
                start_idx += Utils.SHOW_DOGS_BATCH_SIZE

    def __create_dog_from_json(self, json) -> Dog:
        print("Dogsssss")
        # name picture description are optional
        dogBuilder: Dog.Builder = Dog.Builder(id=DogId(json['id']), dog_birth_info=DogBirthInfo.create(breed_str=json['breed'], sex_str=json['sex'], birth_date_str=json['birth_date'], estimated_adult_size=json['estimated_adult_size']),
                                               entry_date=Date.parse_date(json['entry_date']), neutered=True) #eval(json['neutered'])
        if 'description' in json:
            dogBuilder.with_description(DogDescription(json['description']))
        if 'name' in json:
            dogBuilder.with_dogname(Dogname(json['name']))
        if 'picture' in json:
            dogBuilder.with_picture(PictureUrl(json['picture']))
        return dogBuilder.build()

    def __add_dog(self):
        print(Utils.REQUIRE_INPUT_DOG_DATA)
        dog_name = input(Utils.DOG_NAME_PRINT)
        dog_description = input(Utils.DOG_DESCRIPTION_INPUT)
        dog_breed = input(Utils.DOG_BREED_INPUT)
        dog_sex = input(Utils.DOG_SEX_INPUT)
        dog_birth_date = input(Utils.DOG_BIRTH_DATE_INPUT)
        dog_entry_date = input(Utils.DOG_ENTRY_DATE_INPUT)
        dog_neutered = input(Utils.DOG_NEUTERED_INPUT)
        dog_picture = input(Utils.DOG_PICTURE_INPUT)
        print(Utils.DOG_ADDED_MESSAGE)

    def __show_preferences(self):
        pass

    def __add_preference(self):
        pass


    def __remove_dog(self):
        invalid = True
        while invalid:
            invalid = False
            try:
                id_input: int = int(input(Utils.DOG_ID_INPUT))
                dog_id: DogId = DogId(id_input)
            except Exception:
                print(Utils.DOG_ID_VALIDATION_ERROR)
                invalid = True
        try:
            response: Response = self.make_dog_remove_request(dog_id)
        except Exception as e:
            print(Utils.CONNECTION_ERROR)
            return
        if response.status_code == 200:
            print(f'Dog with id {dog_id.value}: {Utils.DOG_DELETED_MESSAGE}')
        else:
            if response.status_code == 404:
                print(Utils.DOG_NOT_FOUND_ERROR)

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
