import json
from typing import Any, cast

from django.http import HttpRequest
from django.utils.datastructures import MultiValueDict


class Parser:
    """Default json parser"""

    @staticmethod
    def parse_body(request: HttpRequest) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(request.body))

    @staticmethod
    def parse_querydict(
        data: MultiValueDict, list_fields: list[str] | None = None
    ) -> dict[str, Any]:
        if list_fields is None:
            list_fields = []

        result: dict[str, Any] = {}
        for key in data.keys():
            if key in list_fields:
                result[key] = data.getlist(key)
            else:
                result[key] = data[key]
        return result
