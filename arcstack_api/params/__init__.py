from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, Any, TypeVar

from .models import BodyModel, PathModel, QueryModel


# isort: off


__all__ = ['Query', 'Path', 'Body']


class ParamShortcut:
    def __init__(self, base_func: Callable[..., Any]) -> None:
        self._base_func = base_func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._base_func(*args, **kwargs)

    def __getitem__(self, args: Any) -> Any:
        if isinstance(args, tuple):
            return Annotated[args[0], self._base_func(**args[1])]
        return Annotated[args, self._base_func()]


if TYPE_CHECKING:
    T = TypeVar('T')
    Query = Annotated[T, QueryModel()]
    Path = Annotated[T, PathModel()]
    Body = Annotated[T, BodyModel()]
else:
    Query = ParamShortcut(QueryModel)
    Path = ParamShortcut(PathModel)
    Body = ParamShortcut(BodyModel)
