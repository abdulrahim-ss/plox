# from typing_extensions import Protocol
# from typing import Optional, Union, Type

# class ErrorCallback(Protocol):
#     def __call__(
#             self, line: int,
#             where: str,
#             message: str,
#             error:Optional[Type[Exception]] = None
#                 ) -> Union[Type[Exception], None]: ...
from plox_token import PloxToken


class RunTimeError(RuntimeError):
    def __init__(self, token: PloxToken, msg: str):
        super().__init__(msg)
        self.token = token


class ParserError(Exception):
    pass
