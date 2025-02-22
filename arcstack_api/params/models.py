from abc import ABC, abstractmethod
from typing import Any, TypeVar

from django.http import HttpRequest
from pydantic import BaseModel

from ..conf import settings
from ..errors import ValidationError
from ..utils import Parser


TModel = TypeVar('TModel', bound='Param')


class Param(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def get_request_data(cls, request: HttpRequest, path: dict[str, Any]) -> TModel:
        pass


class QueryModel(Param):
    @classmethod
    def get_request_data(
        cls, request: HttpRequest, path: dict[str, Any]
    ) -> dict[str, Any] | None:
        return Parser.parse_querydict(request.GET)


class PathModel(Param):
    @classmethod
    def get_request_data(
        cls, request: HttpRequest, path: dict[str, Any]
    ) -> dict[str, Any] | None:
        return path


class BodyModel(Param):
    @classmethod
    def get_request_data(
        cls, request: HttpRequest, path: dict[str, Any]
    ) -> dict[str, Any] | None:
        if request.body:
            try:
                data = Parser.parse_body(request)
            except Exception as e:
                msg = 'Cannot parse request body'

                if settings.DEBUG:
                    msg += f': {e}'

                raise ValidationError([msg]) from e

            return data

        return None
