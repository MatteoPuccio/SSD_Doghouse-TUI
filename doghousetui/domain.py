import json
import os
from dataclasses import dataclass, InitVar
from enum import IntEnum
from functools import cached_property
from pathlib import Path

from typeguard import typechecked
from valid8 import validate, ValidationError
from typing import Optional, ClassVar
from dataclasses import field

from datetime import date
from doghousetui import Utils
from validation.regex import pattern


@typechecked
@dataclass(order=True, frozen=True)
class Dogname:
    __value:str = field(default="Unnamed")
    def __post_init__(self):
        validate("Dog name",self.value, min_len=2, max_len=50, custom=pattern(r"[A-Z][a-z]+"))

    @property
    def value(self):
        return self.__value

@typechecked
@dataclass(order=True, frozen=True)
class Breed:
    value: str
    __breeds:ClassVar[frozenset] = frozenset()
    def __post_init__(self):
        validate("breed validation", self.value, min_len=2, max_len=60, custom=lambda v: v in Breed.read_breeds())

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
          return self.__value ==  other.__value
        return False

    @property
    def value(self):
        return self.__value


@typechecked
@dataclass(order=True, frozen=True)
class Date:
    __value: date
    def __post_init__(self):
        validate("date at most today", self.__value, custom = lambda d: d <= date.today())

    def __str__(self) -> str:
        return self.__value.strftime("%Y-%m-%d")

@typechecked
@dataclass(order=True, frozen=True)
class Dog_description:
  value: str
  def __post_init__(self):
      validate("dog description", self.value, min_len=0, max_len=400, custom=pattern(r"^[a-zA-Z0-9,;. \-\t?!]*$"))


@typechecked
@dataclass(order=True, frozen=True)
class Estimated_adult_size:
    value:str
    def __post_init__(self):
      validate("size validation", self.value, min_len=1, max_len=2, custom=lambda v: v in ["XS","S","M","L","XL"])

@typechecked
@dataclass(order=True, frozen=True)
class PictureUrl:
    value: Optional[str] = field(default="")
    def __post_init__(self):
        validate("picture url", self.value, min_len=0, max_len=60, custom=pattern(r"^(https\:\/\/imgur\.com\/[a-zA-Z0-9_]+)?$"))
