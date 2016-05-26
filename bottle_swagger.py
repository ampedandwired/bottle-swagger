import re
from bottle import request, response
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.request import IncomingRequest, unmarshal_request
from bravado_core.response import OutgoingResponse, validate_response, get_response_spec
from bravado_core.spec import Spec
from jsonschema import ValidationError


def _error_response(status, e):
    response.status = status
    return {"code": status, "message": str(e)}


def _server_error_handler(e):
    return _error_response(500, e)


def _bad_request_handler(e):
    return _error_response(400, e)


def _not_found_handler(e):
    return _error_response(404, e)


class SwaggerPlugin:
    DEFAULT_SWAGGER_SCHEMA_URL = '/swagger.json'

    name = 'swagger'
    api = 2

    def __init__(self, swagger_def,
                 validate_requests=True,
                 validate_responses=True,
                 ignore_undefined_routes=False,
                 invalid_request_handler=_bad_request_handler,
                 invalid_response_handler=_server_error_handler,
                 swagger_op_not_found_handler=_not_found_handler,
                 exception_handler=_server_error_handler,
                 serve_swagger_schema=True,
                 swagger_schema_url=DEFAULT_SWAGGER_SCHEMA_URL):
        self.swagger = Spec.from_dict(swagger_def)
        self.validate_requests = validate_requests
        self.validate_responses = validate_responses
        self.ignore_undefined_routes = ignore_undefined_routes
        self.invalid_request_handler = invalid_request_handler
        self.invalid_response_handler = invalid_response_handler
        self.swagger_op_not_found_handler = swagger_op_not_found_handler
        self.exception_handler = exception_handler
        self.serve_swagger_schema = serve_swagger_schema
        self.swagger_schema_url = swagger_schema_url

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            return self._swagger_validate(callback, route, *args, **kwargs)

        return wrapper

    def setup(self, app):
        if self.serve_swagger_schema:
            @app.get(self.swagger_schema_url)
            def swagger_schema():
                return self.swagger.spec_dict

    def _swagger_validate(self, callback, route, *args, **kwargs):
        try:
            swagger_op = self._swagger_op(route)
            if not swagger_op and not self.ignore_undefined_routes and not self._is_swagger_schema_route(route):
                return self.swagger_op_not_found_handler(route)

            if swagger_op and self.validate_requests:
                try:
                    self._validate_request(swagger_op)
                except ValidationError as e:
                    return self.invalid_request_handler(e)

            result = callback(*args, **kwargs)

            if swagger_op and self.validate_responses:
                try:
                    self._validate_response(swagger_op, result)
                except (ValidationError, MatchingResponseNotFound) as e:
                    return self.invalid_response_handler(e)

        except Exception as e:
            return self.exception_handler(e)

        return result

    @staticmethod
    def _validate_request(swagger_op):
        unmarshal_request(BottleIncomingRequest(request), swagger_op)

    @staticmethod
    def _validate_response(swagger_op, result):
        response_spec = get_response_spec(int(response.status_code), swagger_op)
        outgoing_response = BottleOutgoingResponse(response, result)
        validate_response(response_spec, swagger_op, outgoing_response)

    def _swagger_op(self, route):
        # Convert bottle "<param>" style path params to swagger "{param}" style
        path = re.sub(r'/<(.+?)>', r'/{\1}', route.rule)
        return self.swagger.get_op_for_request(request.method, path)

    def _is_swagger_schema_route(self, route):
        return self.serve_swagger_schema and route.rule == self.swagger_schema_url


class BottleIncomingRequest(IncomingRequest):
    def __init__(self, bottle_request):
        self.request = bottle_request
        self.path = bottle_request.url_args

    def json(self):
        return self.request.json


class BottleOutgoingResponse(OutgoingResponse):
    def __init__(self, bottle_response, response_json):
        self.response = bottle_response
        self.response_json = response_json
        self.content_type = bottle_response.content_type if bottle_response.content_type else 'application/json'

    def json(self):
        return self.response_json
