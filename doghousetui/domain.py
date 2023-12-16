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
from doghousetui import Utils
from doghousetui.Exception import DateWrongFormatError
from validation.regex import pattern


@typechecked
@dataclass(order=True, frozen=True)
class Dogname:
    __value: str = field(default="Unnamed")

    def __post_init__(self):
        validate("Dog name", self.value, min_len=2, max_len=50, custom=pattern(r"[A-Z][a-z]+"))

    @property
    def value(self):
        return self.__value


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

    __breeds: ClassVar[frozenset] = field(default=read_breeds())

    def __post_init__(self):
        validate("breed validation", self.value, min_len=2, max_len=60, custom=lambda v: v in Breed.__breeds)

    @staticmethod
    def read_breeds():
        path_to_file: Path = Path(__file__).parent.parent / Utils.PATH_TO_BREED_JSON
        with open(str(path_to_file), "r") as json_file:
            breeds: dict = json.load(json_file)
            return frozenset(breeds["dogs"])


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


@typechecked
@dataclass(order=True, frozen=True)
class EstimatedAdultSize:
    value: Optional[str] = field(default="Unknown")

    def __post_init__(self):
        validate("size validation", self.value, min_len=1, max_len=7,
                 custom=lambda v: v in ["XS", "S", "M", "L", "XL", "Unknown"])


@typechecked
@dataclass(order=True, frozen=True)
class PictureUrl:
    value: Optional[str] = field(default="")

    def __post_init__(self):
        validate("picture url", self.value, min_len=0, max_len=60,
                 custom=pattern(r"^(https\:\/\/imgur\.com\/[a-zA-Z0-9_]+)?$"))


@typechecked
@dataclass(order=True, frozen=True)
class DogId:
    value: int

    def __post_init__(self):
        validate("id validation", self.value, min_value=0)


@typechecked
@dataclass(frozen=True)
class DogBirthInfo:
    name: Dogname
    breed: Breed
    sex: Sex
    birth_date: Date
    create_key: InitVar[Any]

    __creation_key:Any = object()
    def __post_init__(self, create_key: Any) -> None:
        validate("creation key", create_key, equals=DogBirthInfo.__creation_key)

    @staticmethod
    def create(name_str: str, breed_str: str, sex_str:str, birth_date_str: str ) -> 'DogBirthInfo':
        return DogBirthInfo( Dogname(name_str), Breed(breed_str), Sex(sex_str), Date.parse_date(birth_date_str), DogBirthInfo.__creation_key)

    def age(self) -> int:
        return self.birth_date.calculate_years_to_today()


@typechecked
class Dog:

    def __init__(self, id: DogId, dog_birth_info: DogBirthInfo, entry_date: Date, neutered: bool, create_key: Any):
        validate("creation_key", create_key, custom=Dog.Builder.is_valid_key)
        self.__dog_id: DogId = id
        self.__birth_info: DogBirthInfo = dog_birth_info
        self.__entry_date: Date = entry_date
        self.__neutered: bool = neutered
        self.estimated_size: EstimatedAdultSize = EstimatedAdultSize()
        self.__description: DogDescription = DogDescription()
        self.__picture: PictureUrl = PictureUrl()

    def _add_description(self, description: DogDescription,create_key:Any):
        validate("add description with builder", create_key, custom=Dog.Builder.is_valid_key)
        self.__description = description

    def _add_picture(self, picture: PictureUrl, create_key:Any):
        validate("add picture with builder", create_key, custom=Dog.Builder.is_valid_key)
        self.__picture = picture

    def _is_entry_after_birth(self) -> bool:
        return self.__birth_info.birth_date <= self.__entry_date

    def _add_estimated_adult_size(self, estimated_size: EstimatedAdultSize, create_key: Any):
        validate("add estimated_adult_size with builder", create_key, custom=Dog.Builder.is_valid_key)
        validate("estimated_size", estimated_size)
        self.__estimated_size = estimated_size

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

        def with_estimated_adult_size(self, value: EstimatedAdultSize) -> 'Dog.Builder':
            validate('dog', self.__dog)
            self.__dog._add_estimated_adult_size(value, self.__create_key)
            return self

        def with_picture(self, value: PictureUrl) -> 'Dog.Builder':
            validate('dog', self.__dog)
            self.__dog._add_picture(value, self.__create_key)
            return self

        def build(self) -> 'Dog':
            validate('dog', self.__dog)
            validate('dog.entry', self.__dog._is_entry_after_birth(), equals=True)
            res, self.__dog = self.__dog, None
            return res
