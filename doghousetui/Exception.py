import typeguard
from valid8 import ValidationError

from doghousetui import Utils

@typeguard.typechecked
class DateWrongFormatError(ValueError, ValidationError):
    def __init__(self, help_msg: str = Utils.DATE_WRONG_FORMAT_MESSAGE):
        self.help_msg = help_msg
        super().__init__(self.help_msg)
