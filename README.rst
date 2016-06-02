=====================
Bottle Swagger Plugin
=====================

About
-----
This project is a Bottle plugin for working with Swagger.
`Bottle <http://bottlepy.org/>`_ is a Python web framework.
`Swagger (OpenAPI) <http://swagger.io/>`_ is a standard for defining REST APIs.

So if you are serving a REST API with Bottle,
and you have a defined a Swagger schema for that API,
this plugin can:

* Validate incoming requests and outgoing responses against the swagger schema
* Return appropriate error responses on validation failures
* Serve your swagger schema via Bottle (for use in `Swagger UI <http://swagger.io/swagger-ui/>`_ for example)

Requirements
------------

* Python >= 2.7
* Bottle >= 0.12
* Swagger specification >= 2.0

This project relies on `bravado-core <https://github.com/Yelp/bravado-core>`_ to perform the swagger schema validation,
so any version of the Swagger spec supported by that project is also supported by this plugin.

Installation
------------
::

  $ pip install bottle-swagger

Usage
-----
See the "example" directory for a working example of using this plugin.

The simplest usage is::

  import bottle

  swagger_def = _load_swagger_def()
  bottle.install(SwaggerPlugin(swagger_def))

Where "_load_swagger_def" returns a dict representing your swagger specification
(loaded from a yaml file, for example).

There are a number of arguments that you can pass to the plugin constructor:

* ``validate_requests`` - Boolean (default ``True``) indicating if incoming requests should be validated or not
* ``validate_responses`` - Boolean (default ``True``) indicating if outgoing responses should be validated or not
* ``ignore_undefined_paths`` - Boolean (default ``False``) indicating if undefined paths
  (that is, paths not defined in the swagger spec) should be passed on ("True") or return a 404 ("False")
* ``invalid_request_handler`` - Callback called when request validation has failed.
  Default behaviour is to return a "400 Bad Request" response.
* ``invalid_response_handler`` - Callback called when response validation has failed.
  Default behaviour is to return a "500 Server Error" response.
* ``swagger_op_not_found_handler`` - Callback called when no swagger operation matching the request was found in the swagger schema.
  Default behaviour is to return a "404 Not Found" response.
* ``exception_handler=_server_error_handler`` - Callback called when an exception is thrown by downstream handlers (including exceptions thrown by your code).
  Default behaviour is to return a "500 Server Error" response.
* ``serve_swagger_schema`` - Boolean (default ``True``) indicating if the Swagger schema JSON should be served
* ``swagger_schema_url`` - URL (default ``/swagger.json``) on which to serve the Swagger schema JSON

All the callbacks above receive a single parameter representing the ``Exception`` that was raised,
or in the case of ``swagger_op_not_found_handler`` the ``Route`` that was not found.
They should all return a Bottle ``Response`` object.

Contributing
------------
Development happens in the `bottle-swagger GitHub respository <https://github.com/ampedandwired/bottle-swagger>`_.
Pull requests (with accompanying unit tests), feature suggestions and bug reports are welcome.

Use "tox" to run the unit tests::

  $ tox
