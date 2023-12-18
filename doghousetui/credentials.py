from dataclasses import dataclass

from typeguard import typechecked
from valid8 import validate
from typing import Optional
from dataclasses import field

from doghousetui import Utils
from validation.regex import pattern


@typechecked
@dataclass(order=True, frozen=True)
class Token:
    __value: str = field(default=Utils.DEFAULT_TOKEN_VALUE, repr=False)

    def __post_init__(self):
        validate('token value', self.__value, min_len=40, max_len=40, custom= pattern(r'[0-9a-z]+'))

    @property
    def value(self):
        return self.__value

    def __eq__(self, __o):
        if isinstance(__o, Token):
            return self.value == __o.value
        return False

    def __hash__(self):
        self.__value.__hash__()

    def __str__(self):
        return self.__value



@typechecked
@dataclass(order=True, frozen=True)
class Username:
    value:str = field()
    def __post_init__(self):
        validate("validation username", self.value, min_len=2, max_len=30, custom=pattern(r"[a-zA-Z0-9]*"))

    def __str__(self):
        return self.value
@typechecked
@dataclass(order=True, frozen=True)
class Password:
    value:str
    def __post_init__(self):
        validate("validaton password", self.value, min_len=8, max_len=30, custom=pattern(r"[a-zA-Z0-9@!#]*"))

@typechecked
@dataclass(order=True, frozen=True)
class Email:
    value:Optional[str] = field(default="")
    def __post_init__(self):
        validate("validaton email", self.value, min_len=0, max_len=320, custom=pattern(r"^([a-zA-Z0-9\+\_\.-]+@(([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)?))+)?$"))