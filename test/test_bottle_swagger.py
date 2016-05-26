from unittest import TestCase

from bottle import Bottle
from bottle_swagger import SwaggerPlugin
from webtest import TestApp


class TestBottleSwagger(TestCase):
    VALID_JSON = {"id": "123", "name": "foo"}
    INVALID_JSON = {"not_id": "123", "name": "foo"}

    SWAGGER_DEF = {
        "swagger": "2.0",
        "info": {"version": "1.0.0", "title": "bottle-swagger"},
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "definitions": {
            "Thing": {
                "type": "object",
                "required": ["id"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"}
                }
            }
        },
        "paths": {
            "/thing": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "",
                            "schema": {
                                "$ref": "#/definitions/Thing"
                            }
                        }
                    }
                },
                "post": {
                    "parameters": [{
                        "name": "thing",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/Thing"
                        }
                    }],
                    "responses": {
                        "200": {
                            "description": "",
                            "schema": {
                                "$ref": "#/definitions/Thing"
                            }
                        }
                    }
                }
            },
            "/thing/{thing_id}": {
                "get": {
                    "parameters": [{
                        "name": "thing_id",
                        "in": "path",
                        "required": True,
                        "type": "string"
                    }],
                    "responses": {
                        "200": {
                            "description": "",
                            "schema": {
                                "$ref": "#/definitions/Thing"
                            }
                        }
                    }
                }
            }
        }
    }

    def test_valid_get_request_and_response(self):
        response = self._test_request()
        self.assertEqual(response.status_int, 200)

    def test_valid_post_request_and_response(self):
        response = self._test_request(method='POST')
        self.assertEqual(response.status_int, 200)

    def test_invalid_request(self):
        response = self._test_request(method='POST', request_json=self.INVALID_JSON)
        self._assert_error_response(response, 400)

    def test_invalid_response(self):
        response = self._test_request(response_json=self.INVALID_JSON)
        self._assert_error_response(response, 500)

    def test_disable_request_validation(self):
        self._test_disable_validation(validate_requests=False, expected_request_status=200,
                                      expected_response_status=500)

    def test_disable_response_validation(self):
        self._test_disable_validation(validate_responses=False, expected_request_status=400,
                                      expected_response_status=200)

    def test_disable_all_validation(self):
        self._test_disable_validation(validate_requests=False, validate_responses=False, expected_request_status=200,
                                      expected_response_status=200)

    def test_exception_handling(self):
        def throw_ex():
            raise Exception("Exception occurred")

        response = self._test_request(response_json=throw_ex)
        self._assert_error_response(response, 500)

    def test_invalid_route(self):
        response = self._test_request(url="/invalid")
        self._assert_error_response(response, 404)

    def test_ignore_invalid_route(self):
        swagger_plugin = self._make_swagger_plugin(ignore_undefined_routes=True)
        response = self._test_request(swagger_plugin=swagger_plugin, url="/invalid")
        self.assertEqual(response.status_int, 200)
        response = self._test_request(swagger_plugin=swagger_plugin, url="/invalid", method='POST',
                                      request_json=self.INVALID_JSON, response_json=self.INVALID_JSON)
        self.assertEqual(response.status_int, 200)

    def test_path_parameters(self):
        response = self._test_request(url="/thing/123", route_url="/thing/<thing_id>")
        self.assertEqual(response.status_int, 200)

    def test_get_swagger_schema(self):
        bottle_app = Bottle()
        bottle_app.install(self._make_swagger_plugin())
        test_app = TestApp(bottle_app)
        response = test_app.get(SwaggerPlugin.DEFAULT_SWAGGER_SCHEMA_URL)
        self.assertEquals(response.json, self.SWAGGER_DEF)

    def _test_request(self, swagger_plugin=None, method='GET', url='/thing', route_url=None, request_json=VALID_JSON,
                      response_json=VALID_JSON):
        if swagger_plugin is None:
            swagger_plugin = self._make_swagger_plugin()
        if response_json is None:
            response_json = {}
        if route_url is None:
            route_url = url

        bottle_app = Bottle()
        bottle_app.install(swagger_plugin)

        @bottle_app.route(route_url, method)
        def do_thing(*args, **kwargs):
            return response_json() if hasattr(response_json, "__call__") else response_json

        test_app = TestApp(bottle_app)
        if method.upper() == 'GET':
            response = test_app.get(url, expect_errors=True)
        elif method.upper() == 'POST':
            response = test_app.post_json(url, request_json, expect_errors=True)
        else:
            raise Exception("Invalid method {}".format(method))

        return response

    def _test_disable_validation(self, validate_requests=True, validate_responses=True, expected_request_status=200,
                                 expected_response_status=200):
        swagger_plugin = self._make_swagger_plugin(validate_requests=validate_requests,
                                                   validate_responses=validate_responses)

        response = self._test_request(swagger_plugin=swagger_plugin, method='POST', request_json=self.INVALID_JSON)
        self.assertEqual(response.status_int, expected_request_status)

        response = self._test_request(swagger_plugin=swagger_plugin, response_json=self.INVALID_JSON)
        self.assertEqual(response.status_int, expected_response_status)

    def _assert_error_response(self, response, expected_status):
        self.assertEqual(response.status_int, expected_status)
        self.assertEqual(response.json['code'], expected_status)
        self.assertIsNotNone(response.json['message'])

    def _make_swagger_plugin(self, *args, **kwargs):
        return SwaggerPlugin(self.SWAGGER_DEF, *args, **kwargs)
