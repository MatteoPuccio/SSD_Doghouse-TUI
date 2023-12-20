import json
import os
from dataclasses import dataclass, InitVar
from enum import IntEnum
from functools import cached_property
from pathlib import Path

from typeguard import typechecked
from valid8 import validate, ValidationError
from typing import Optional, ClassVar, Any
from dataclasses import field

from datetime import date, timedelta
from doghousetui import Utils, Helpmsg_utils
from doghousetui.Exception import DateWrongFormatError
from validation.regex import pattern
from difflib import SequenceMatcher

@typechecked
@dataclass(order=True, frozen=True)
class Dogname:
    __value: str = field(default="")

    def __post_init__(self):
        validate("Dog name", self.value, min_len=0, max_len=50, custom=pattern(r"([A-Z][a-z]+)?"))

    @property
    def value(self):
        return self.__value

    def is_default(self):
        return self.value == ""


@typechecked
@dataclass(order=True, frozen=True)
class Breed:
    value: str

    @staticmethod
    def read_breeds():
        path_to_file: Path = Path(__file__).parent.parent / Utils.PATH_TO_BREED_JSON
        with open(str(path_to_file), "r") as json_file:
            breeds: dict = json.load(json_file)
            return frozenset(breeds["dogs"])

    breeds: ClassVar[frozenset] = field(default=read_breeds())

    @staticmethod
    def similar_breeds(searched_breed: str) -> list:
        number_of_similar = 3
        most_similar_breeds = []
        min_ratio = 0.0
        for breed in Breed.breeds:
            ratio = SequenceMatcher(a=searched_breed.lower(), b=breed.lower()).ratio()
            if len(most_similar_breeds) < number_of_similar:
                most_similar_breeds.append((breed,ratio))
                min_ratio = max(ratio, min_ratio)

            elif ratio > min_ratio:
                most_similar_breeds[number_of_similar-1], min_ratio = (breed, ratio), ratio

            most_similar_breeds.sort(key=lambda x: x[1],reverse=True)

        return list(map(lambda x: x[0], most_similar_breeds))

    def __post_init__(self):
        validate("breed validation", self.value, min_len=2, max_len=60, custom=lambda v: v in Breed.breeds)


@typechecked
@dataclass(order=True, frozen=True)
class Sex:
    __value: str = field(init=True)

    def __post_init__(self):
        validate("Sex value", self.__value, min_len=1, max_len=1, custom=pattern(r"M|F"))

    def __eq__(self, other):
        if isinstance(other, Sex):
            return self.__value == other.__value
        return False

    @property
    def value(self):
        return self.__value


@typechecked
@dataclass(order=True, frozen=True)
class Date:
    __value: date

    def __post_init__(self):
        validate("date at most today", self.__value, custom=lambda _ : self.__value <= date.today())

    def calculate_years_to_today(self) -> int:
        today = date.today()
        years = today.year - self.__value.year
        if (today.month, today.day) < (self.__value.month, self.__value.day):
            years -= 1
        return years

    def days_elapsed(self, d: 'Date') -> int:
        if d.__value >= self.__value:
            return (d.__value - self.__value).days
        return (self.__value - d.__value).days

    @staticmethod
    def parse_date(date_str:str) -> 'Date':
        try:
            d = date.fromisoformat(date_str)
            return Date(d)
        except ValueError as e:
            raise DateWrongFormatError()

    def __str__(self) -> str:
        return self.__value.strftime("%Y-%m-%d")


@typechecked
@dataclass(order=True, frozen=True)
class DogDescription:
    value: Optional[str] = field(default_factory=str)

    def __post_init__(self):
        validate("dog description", self.value, min_len=0, max_len=400, custom=pattern(r"^[a-zA-Z0-9,;. \-\t?!]*$"))

    def __eq__(self, other):
        if not isinstance(other, DogDescription):
            return False
        return self.value == other.value
    def is_default(self):
        return self.value == ""


@typechecked
@dataclass(order=True, frozen=True)
class EstimatedAdultSize:
    value: str

    def __post_init__(self):
        validate("size validation", self.value, min_len=0, max_len=7,
                 custom=lambda v: v in ["XS", "S", "M", "L", "XL"])

@typechecked
@dataclass(order=True, frozen=True)
class PictureUrl:
    value: Optional[str] = field(default="")

    def __post_init__(self):
        validate("picture url", self.value, min_len=0, max_len=60,
                 custom=pattern(r"^(https\:\/\/imgur\.com\/[a-zA-Z0-9_]+\.(jpeg|png|jpg))?$"))

    def is_default(self):
        return self.value == ""


@typechecked
@dataclass(order=True, frozen=True)
class DogId:
    value: int

    def __post_init__(self):
        validate("id validation", self.value, min_value=0)

    def __str__(self):
        return self.value

@typechecked
@dataclass(frozen=True)
class DogBirthInfo:
    breed: Breed
    sex: Sex
    birth_date: Date
    estimated_adult_size: EstimatedAdultSize

    def age(self) -> int:
        return self.birth_date.calculate_years_to_today()

    def representation(self) -> str:
        return Utils.DOG_BREED_PRINT + self.breed.value + "\n" \
                + Utils.DOG_SEX_PRINT + self.sex.value + "\n" \
                + Utils.DOG_BIRTH_DATE_PRINT + self.birth_date.__str__() + "\n" \
                + Utils.DOG_ESTIMATED_ADULT_SIZE_PRINT + self.estimated_adult_size.value



@typechecked
class Dog:

    def __init__(self, id: DogId, dog_birth_info: DogBirthInfo, entry_date: Date, neutered: bool, create_key: Any):
        validate("creation_key", create_key, custom=Dog.Builder.is_valid_key)
        self.dog_id: DogId = id
        self.birth_info: DogBirthInfo = dog_birth_info
        self.entry_date: Date = entry_date
        self.neutered: bool = neutered
        self.name: Dogname = Dogname()
        self.description: DogDescription = DogDescription()
        self.picture: PictureUrl = PictureUrl()

    def _add_description(self, description: DogDescription,create_key:Any):
        validate("add description with builder", create_key, custom=Dog.Builder.is_valid_key)
        self.description = description

    def _add_picture(self, picture: PictureUrl, create_key:Any):
        validate("add picture with builder", create_key, custom=Dog.Builder.is_valid_key)
        self.picture = picture

    def _is_entry_after_birth(self) -> bool:
        return self.birth_info.birth_date <= self.entry_date

    def _add_name(self, dogname: Dogname, create_key: Any):
        validate("add dogname with builder", create_key, custom=Dog.Builder.is_valid_key)
        self.name = dogname

    def has_name(self) -> bool:
        return  self.name != Dogname()

    def has_description(self) -> bool:
        return self.description != DogDescription()

    def has_picture(self) -> bool:
        return self.picture != PictureUrl()

    def compact_representation(self):
        return f'{Utils.DOG_ID_PRINT}{self.dog_id.value}\n{self.birth_info.representation()}\n{Utils.DOG_ENTRY_DATE_PRINT}{self.entry_date}\n'

    def extended_representation(self):
        return (f'{Utils.DOG_ID_PRINT}{self.dog_id.value}\n{self.birth_info.representation()}\n' \
                f'{Utils.DOG_ENTRY_DATE_PRINT}{self.entry_date}\n{Utils.DOG_NEUTERED_PRINT}{self.neutered}\n' \
                f'{Utils.DOG_NAME_PRINT}{self.name.value}\n{Utils.DOG_DESCRIPTION_PRINT}{self.description.value}\n' \
                f'{Utils.DOG_PICTURE_PRINT}{self.picture.value}\n')


    @typechecked
    @dataclass()
    class Builder:
        __dog: Optional['Dog']
        __create_key = object()

        def __init__(self, id: DogId, dog_birth_info: DogBirthInfo, entry_date: Date, neutered: bool,):
            self.__dog = Dog(id, dog_birth_info, entry_date, neutered, Dog.Builder.__create_key)

        @staticmethod
        def is_valid_key(key: Any) -> bool:
            return key == Dog.Builder.__create_key

        def with_description(self, value: DogDescription) -> 'Dog.Builder':
            validate('dog', self.__dog)
            self.__dog._add_description(value, self.__create_key)
            return self

        def with_dogname(self, value: Dogname) -> 'Dog.Builder':
            validate('dog', self.__dog)
            self.__dog._add_name(value, self.__create_key)
            return self

        def with_picture(self, value: PictureUrl) -> 'Dog.Builder':
            validate('dog', self.__dog)
            self.__dog._add_picture(value, self.__create_key)
            return self

        def build(self) -> 'Dog':
            validate('dog', self.__dog)
            validate('dog.entry', self.__dog._is_entry_after_birth(), equals=True, help_msg=Helpmsg_utils.DOG_BIRTH_AFTER_ENTRY)
            res, self.__dog = self.__dog, None
            return res
