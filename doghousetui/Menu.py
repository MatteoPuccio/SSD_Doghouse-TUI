from valid8 import validate
from typeguard import typechecked
from dataclasses import field, InitVar, dataclass

from doghousetui import Utils
from validation.regex import pattern
from typing import Callable, Any, Dict, Optional


@typechecked
@dataclass(order=True, frozen=True)
class Description:
    value: str

    def __post_init__(self):
        validate('Description.value', self.value, min_len=1, max_len=1000, custom=pattern(r'[0-9A-Za-z ;.,_-]*'))

    def __str__(self):
        return self.value


@typechecked
@dataclass(order=True, frozen=True, eq=True)
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


@typechecked
@dataclass(frozen=True)
class Menu:
    description: Description
    __key2entry: Dict[Key, MenuEntry] = field(default_factory=dict, repr=False, init=False)
    create_key: InitVar[Any] = field(default='it must be Builder.__create_key')


    def __post_init__(self, create_key: Any):
        validate('create_key', create_key, custom=Menu.Builder.is_valid_key)

    def _add_entry(self, value: MenuEntry, create_key: Any) -> None:
        validate('create_key', create_key, custom=Menu.Builder.is_valid_key)
        validate('value.key', value.key, custom=lambda v: v not in self.__key2entry)
        self.__key2entry[value.key] = value

    def _contains_exit(self):
        return any(list(filter(lambda v: v.is_exit, self.__key2entry.values())))

    def __print(self) -> None:
        length = len(str(self.description))
        fmt = '***{}{}{}***'
        print(fmt.format('*', '*' * length, '*'))
        print(fmt.format(' ', self.description.value, ' '))
        print(fmt.format('*', '*' * length, '*'))
        for k, v in self.__key2entry.items():
            print(f'{k}:\t{v.description}')

    def __select_from_input(self) -> bool:
        while True:
            try:
                line: str = input(" ")
                key = Key(line.strip())
                entry = self.__key2entry[key]
                entry.on_selected()
                return entry.is_exit
            except (KeyError, TypeError, ValueError):
                print(Utils.INVALID_MENU_SELECTION)


    def run(self) -> None:
        while True:
            self.__print()
            is_exit = self.__select_from_input()
            if is_exit:
                return

    @typechecked
    @dataclass()
    class Builder:
        __menu: Optional['Menu']
        __create_key = object()

        def __init__(self, description: Description):
            self.__menu = Menu(description, self.__create_key)

        @staticmethod
        def is_valid_key(key: Any) -> bool:
            return key == Menu.Builder.__create_key

        def with_entry(self, value: MenuEntry) -> 'Menu.Builder':
            validate('menu', self.__menu)
            self.__menu._add_entry(value, self.__create_key)
            return self

        def build(self) -> 'Menu':
            validate('menu', self.__menu)
            validate('menu.entries', self.__menu._contains_exit(), equals=True)
            res, self.__menu = self.__menu, None
            return res
        