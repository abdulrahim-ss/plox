from typing_extensions import Protocol
from typing import Optional, Union, Type

class ErrorCallback(Protocol):
    def __call__(
            self, line: int,
            where: str,
            message: str,
            error:Optional[Type[Exception]] = None
                ) -> Union[Type[Exception], None]: ...
