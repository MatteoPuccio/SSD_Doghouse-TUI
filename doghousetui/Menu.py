from valid8 import validate
from typeguard import typechecked
from dataclasses import field, InitVar, dataclass
from validation.regex import pattern
from typing import Callable,Any


@typechecked
@dataclass(order=True, frozen=True)
class Description:
    value: str

    def __post_init__(self):
        validate('Description.value', self.value, min_len=1, max_len=1000, custom=pattern(r'[0-9A-Za-z ;.,_-]*'))

    def __str__(self):
        return self.value


@typechecked
@dataclass(order=True, frozen=True)
class Key:
    value: str

    def __post_init__(self):
        validate('Key.value', self.value, min_len=1, max_len=10, custom=pattern(r'[0]|[1-9][0-9]*'))

    def __str__(self):
        return self.value


@typechecked
@dataclass(order=True, frozen=True)
class MenuEntry:
    key: Key
    description: Description
    on_selected: Callable[[], None] = field(default=lambda: None)
    is_exit: bool = field(default=False)
    create_key: InitVar[Any] = field(default="create key default")

    __create_key = object()

    def __post_init__(self, create_key):
        validate('create_key', create_key, equals=self.__create_key)

    @staticmethod
    def create(key: str, description: str, on_selected: Callable[[], None]=lambda: None, is_exit: bool=False) -> 'MenuEntry':
        return MenuEntry(Key(key), Description(description), on_selected, is_exit, MenuEntry.__create_key)

