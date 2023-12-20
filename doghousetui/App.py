import sys
from dataclasses import dataclass
from typing import Any, Callable, List

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
from doghousetui.domain import DogId, Dog, DogBirthInfo, DogDescription, PictureUrl, Dogname, Date, Breed, Sex, \
    EstimatedAdultSize

from validation.regex import pattern


class App:
    # menu
    def __init__(self):
        self.__token = Token()
        self.__running = True
        # self.__app_status = AppStatus()
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
            MenuEntry.create('4', Utils.SHOW_PREFERENCES_ENTRY, on_selected=lambda: self.__show_preferences())) \
            .with_entry(MenuEntry.create('5', Utils.ADD_PREFERENCE_ENTRY, on_selected=lambda: self.__add_preference())) \
            .with_entry(
            MenuEntry.create('6', Utils.REMOVE_PREFERENCE_ENTRY, on_selected=lambda: self.__remove_preference())) \
            .with_entry(
            MenuEntry.create('7', Utils.LOGOUT_ENTRY, is_exit=True, on_selected=lambda: self.__logout())) \
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

    def __read_dog_id(self) -> DogId:
        invalid = True
        while invalid:
            invalid = False
            try:
                id_input: int = int(input(Utils.DOG_ID_INPUT))
                dog_id: DogId = DogId(id_input)
            except Exception:
                print(Utils.DOG_ID_VALIDATION_ERROR)
                invalid = True
        return dog_id

    def make_dogs_request(self) -> Response:
        return requests.get(Utils.API_SERVER_DOGS)

    def make_show_preferences_request(self) -> Response:
        return requests.get(Utils.API_SERVER_PREFERENCES, headers={'Authorization': f'Token {self.__token}'})

    def make_add_preference_to_dog_request(self, dog_id: int) -> Response:
        return requests.post(Utils.API_SERVER_PREFERENCES, headers={'Authorization': f'Token {self.__token}'},
                             json={Utils.PREFERENCES_DOG_ID_KEY: str(dog_id)})

    def make_remove_preference_to_dog_request(self, dog_id) -> Response:
        return requests.delete(f'{Utils.API_SERVER_PREFERENCES}{str(dog_id)}/',
                               headers={'Authorization': f'Token {self.__token}'})

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

    def __read_dog_name(self, message) -> Dogname:
        dogname: str = input(message)
        return Dogname(dogname)

    def __read_dog_description(self, message) -> DogDescription:
        description: str = input(message)
        return DogDescription(description)

    def __read_breed(self, message) -> Breed:
        breed: str = input(message)
        return Breed(breed)

    def __read_sex(self, message) -> Sex:
        sex: str = input(message)
        return Sex(sex)

    def __read_date(self, message) -> Date:
        date: str = input(message)
        return Date.parse_date(date)

    def __read_neutered(self, message) -> bool:
        neutered: str = input(message)
        validate("neutered", neutered, min_len=1, max_len=1, custom=pattern(r"[YN]"))
        return neutered == "Y"

    def __read_picture_url(self, message) -> PictureUrl:
        url: str = input(message)
        return PictureUrl(url)

    def __read_estimated_size(self, message) -> EstimatedAdultSize:
        estimated_size: str = input(message)
        return EstimatedAdultSize(estimated_size)

    def make_login_request(self, username: Username, password: Password) -> Response:
        return requests.post(Utils.API_SERVER_LOGIN, json={"username": username.value, "password": password.value})

    def make_logout_request(self) -> Response:
        return requests.post(Utils.API_SERVER_LOGOUT)

    def make_registration_request(self, username: Username, email: Email, password: Password) -> Response:
        if email.is_default():
            return requests.post(Utils.API_SERVER_REGISTER,
                                 json={"username": username.value, "password1": password.value,
                                       "password2": password.value})
        return requests.post(Utils.API_SERVER_REGISTER,
                             json={"username": username.value, "email": email.value, "password1": password.value,
                                   "password2": password.value})

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

    def __repeat_until_valid(self, message: str, error_message: str, function: Callable[[str], Any]) -> Any:
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
        username: Username = self.__repeat_until_valid(Utils.INSERT_USERNAME_MESSAGE, Utils.INVALID_USERNAME_ERROR,
                                                       self.__read_username)
        email: Email = self.__repeat_until_valid(Utils.INSERT_EMAIL_MESSAGE, Utils.INVALID_EMAIL_ERROR,
                                                 self.__read_email)
        password1: Password = self.__repeat_until_valid(Utils.INSERT_PASSWORD_MESSAGE, Utils.INVALID_PASSWORD_ERROR,
                                                        self.__read_password)
        invalid = False
        try:
            password2: Password = self.__read_password(Utils.REPEAT_PASSWORD_MESSAGE)
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
    def __print_add_dog_error(json):
        if 'non_field_errors' in json:
            App.__print_error_message(json['non_field_errors'])

    @staticmethod
    def __print_registration_errors(json):
        if 'non_field_errors' in json:
            App.__print_error_message(json['non_field_errors'])
        if 'username' in json:
            App.__print_error_message(json['username'])

    def __show_preferences(self):
        try:
            response: Response = self.make_show_preferences_request()
        except Exception:
            print(Utils.CONNECTION_ERROR)
            return
        print(response.json())

    def __add_preference(self):
        input_id: DogId = self.__read_dog_id()
        try:
            response: Response = self.make_add_preference_to_dog_request(input_id.value)
        except Exception:
            print(Utils.CONNECTION_ERROR)
            return
        print(response.json())
        print(response.status_code)
        if response.status_code == 201:
            print(Utils.ADD_PREFERENCE_SUCCEEDED_MESSAGE)
        else:
            App.__print_add_preference_errors(response.json())

    def __remove_preference(self):
        input_id: DogId = self.__read_dog_id()
        try:
            response: Response = self.make_remove_preference_to_dog_request(input_id.value)
        except Exception:
            print(Utils.CONNECTION_ERROR)
            return
        if response.status_code == 204:
            print(Utils.REMOVE_PREFERENCE_SUCCEEDED_MESSAGE)
        else:
            if response.status_code == 404:
                print(Utils.REMOVE_PREFERENCE_FAILED_MESSAGE)

    @staticmethod
    def __print_add_preference_errors(json):
       # print(json)
        if 'non_field_errors' in json:
            print(Utils.ADD_PREFERENCE_FAILED_DUPLICATE)
        if 'dog_id' in json:
            print(Utils.ADD_PREFERENCE_FAILED_DOG_ID)


    @staticmethod
    def __print_login_errors(json):
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
        print(dogs_response.status_code)
        print(dogs_response.json())
        if dogs_response.status_code == 200:
            dogs = dogs_response.json()
            all_dogs: List[Dog] = []
            for dog_json in dogs:
                try:
                    dog = self.__create_dog_from_json(dog_json)
                    all_dogs.append(dog)
                except ValidationError as e:
                    print(Utils.DOG_RECEIVED_ERROR)

        else:
            print(Utils.SHOW_DOGS_ERROR)
        if len(all_dogs) <= Utils.SHOW_DOGS_BATCH_SIZE:
            for dog in all_dogs:
                print(dog.extended_representation())
        else:
            wants_more: bool = True
            start_idx = 0
            while wants_more:
                for i in range(start_idx, start_idx + Utils.SHOW_DOGS_BATCH_SIZE):
                    if i < len(all_dogs):
                        print(all_dogs[i].extended_representation())

                if start_idx + Utils.SHOW_DOGS_BATCH_SIZE < len(all_dogs):
                    selection: str = input(Utils.WANTS_MORE_QUESTION)
                    if selection.lower() != Utils.WANTS_MORE_YES_ANSWER:
                        wants_more = False
                else:
                    wants_more = False
                start_idx += Utils.SHOW_DOGS_BATCH_SIZE

    def __create_dog_from_json(self, json) -> Dog:
        # name picture description are optional
        dogBuilder: Dog.Builder = Dog.Builder(id=DogId(int(json['id'])),
                                              dog_birth_info=DogBirthInfo(Breed(json['breed']),
                                                                                 Sex(json['sex']),
                                                                                 Date.parse_date(json['birth_date']),
                                                                                 EstimatedAdultSize(json[
                                                                                     'estimated_adult_size'])),
                                              entry_date=Date.parse_date(json['entry_date']),
                                              neutered=True)  # eval(json['neutered'])
        if 'description' in json:
            dogBuilder.with_description(DogDescription(json['description']))
        if 'name' in json:
            dogBuilder.with_dogname(Dogname(json['name']))
        if 'picture' in json:
            dogBuilder.with_picture(PictureUrl(json['picture']))
        return dogBuilder.build()

    def __read_dog_birth_info(self) -> DogBirthInfo:
        dog_breed = self.__repeat_until_valid(Utils.DOG_BREED_INPUT, Utils.INVALID_BREED, self.__read_breed)
        dog_sex = self.__repeat_until_valid(Utils.DOG_SEX_INPUT, Utils.INVALID_SEX, self.__read_sex)
        dog_birth_date = self.__repeat_until_valid(Utils.DOG_BIRTH_DATE_INPUT, Utils.INVALID_DATE, self.__read_date)
        dog_estimated_size = self.__repeat_until_valid(Utils.DOG_ESTIMATED_ADULT_SIZE_INPUT,
                                                       Utils.INVALID_ESTIMATED_SIZE, self.__read_estimated_size)

        return DogBirthInfo(dog_breed, dog_sex, dog_birth_date, dog_estimated_size)

    def __read_dog_optional_field(self, dog_builder: Dog.Builder):
        dog_name: Dogname = self.__repeat_until_valid(Utils.DOG_NAME_PRINT, Utils.INVALID_DOG_NAME,
                                                      self.__read_dog_name)
        if not dog_name.is_default():
            dog_builder.with_dogname(dog_name)

        dog_description: DogDescription = self.__repeat_until_valid(Utils.DOG_DESCRIPTION_PRINT,
                                                                    Utils.INVALID_DESCRIPTION, self.__read_dog_description)
        if not dog_description.is_default():
            dog_builder.with_description(dog_description)

        dog_picture: PictureUrl = self.__repeat_until_valid(Utils.DOG_PICTURE_PRINT, Utils.INVALID_URL,
                                                            self.__read_picture_url)
        if not dog_picture.is_default():
            dog_builder.with_picture(dog_picture)

        return dog_builder

    def __read_dog_essential(self) -> Dog.Builder:
        dog_birt_info: DogBirthInfo = self.__read_dog_birth_info()
        dog_entry_date:Date = self.__repeat_until_valid(Utils.DOG_ENTRY_DATE_INPUT, Utils.INVALID_DATE, self.__read_date)
        dog_neutered:bool = self.__repeat_until_valid(Utils.DOG_NEUTERED_INPUT, Utils.INVALID_NEUTERED_VALUE,self.__read_neutered)
        default_add_id: DogId = DogId(1)
        return Dog.Builder(default_add_id, dog_birt_info, dog_entry_date, dog_neutered)

    def make_add_dog_request(self, dog: Dog):
        json = {
                "entry_date": str(dog.entry_date),
                "neutered": dog.neutered,
                "breed": dog.birth_info.breed.value,
                "sex": dog.birth_info.sex.value,
                "birth_date": str(dog.birth_info.birth_date),
                "estimated_adult_size": dog.birth_info.estimated_adult_size.value}
        if dog.has_picture(): json["picture"] = dog.picture.value
        if dog.has_name(): json["name"] = dog.name.value
        if dog.has_description(): json["description"] = dog.description.value
        return requests.post(url=Utils.API_SERVER_DOGS,
                             headers={'Authorization': f'Token {self.__token}'},
                             json=json)

    def __read_dog(self) -> Dog:
        dog_builder: Dog.Builder = self.__read_dog_essential()
        dog_builder = self.__read_dog_optional_field(dog_builder)
        return dog_builder.build()

    def __add_dog(self):
        print(Utils.REQUIRE_INPUT_DOG_DATA)
        try:
            dog: Dog = self.__read_dog()
        except ValidationError as e:
            print(e.help_msg)
            return
        try:
            response: Response = self.make_add_dog_request(dog)
        except Exception as e:
            print(Utils.CONNECTION_ERROR)
            print(e.args)
            return
        if response.status_code == 201:
            print(Utils.DOG_ADDED_MESSAGE)
        else:
            App.__print_add_dog_error(response.json())

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
        if response.status_code == 204:
            print(f'Dog with id {dog_id.value}: {Utils.DOG_DELETED_MESSAGE}')
        else:
            if response.status_code == 404:
                print(Utils.DOG_NOT_FOUND_ERROR)

    def __close_app(self):
        print(Utils.EXIT_MESSAGE)
        self.__running = False

    def __switch_menu(self, menu):
        self.__current_menu = menu
        # self.run()

    def run(self):
        while self.__running:
            self.__current_menu.run()


def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
