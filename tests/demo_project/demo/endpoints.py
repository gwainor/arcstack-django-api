from pydantic import BaseModel

from arcstack_api import APIError, ArcStackAPI, Body, Path


KEY = 'message'
VALUE = 'Hello, world!'


class Schema(BaseModel):
    message: str


class PathSchema(BaseModel):
    who: str


class SimpleEndpoint(ArcStackAPI):
    def get(self):
        return {KEY: VALUE}


class WithReturnSchema(ArcStackAPI):
    def get(self) -> Schema:
        return {KEY: VALUE}


class WithSchemaReturned(ArcStackAPI):
    def get(self):
        return Schema(message=VALUE)


class WithPathParam(ArcStackAPI):
    def get(self, path: Path[PathSchema]):
        return path


class WithLoginRequired(ArcStackAPI):
    LOGIN_REQUIRED = True

    def get(self) -> Schema:
        return {'message': 'Hello, world!'}


class WithBody(ArcStackAPI):
    def post(self, body: Body[Schema]) -> Schema:
        return body


class WithAPIError(ArcStackAPI):
    def get(self) -> Schema:
        raise APIError('Interrupted with APIError')
