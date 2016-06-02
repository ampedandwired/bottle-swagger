=====================
Bottle Swagger Plugin
=====================

Overview
--------
`Bottle <http://bottlepy.org/>`_ is a Python web framework.

`Swagger <http://swagger.io/>`_ is a standard for defining REST APIs.

This project is a Bottle plugin for working with Swagger.
If you are serving a REST API with Bottle,
and you have a defined a Swagger schema for that API,
this plugin will:

* Validate incoming requests against the swagger schema and return an appropriate error response on failure
* Validate outgoing responses against the swagger schema and return an appropriate error response on failure
* Serve your swagger schema via Bottle

Installation
------------

Usage
-----

Contributing
------------
