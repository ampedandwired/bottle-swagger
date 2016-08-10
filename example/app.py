import bottle
import os
import yaml
from bottle_swagger import SwaggerPlugin

this_dir = os.path.dirname(os.path.abspath(__file__))
with open("{}/swagger.yml".format(this_dir)) as f:
    swagger_def = yaml.load(f)

bottle.install(SwaggerPlugin(swagger_def))


@bottle.get('/thing')
def hello():
    return {"id": "1", "name": "Thing1"}


@bottle.get('/thing/<thing_id>')
def hello(thing_id):
    return {"id": thing_id, "name": "Thing{}".format(thing_id)}


@bottle.get('/thing_query')
def hello():
    thing_id = bottle.request.query['thing_id']
    return {"id": thing_id, "name": "Thing{}".format(thing_id)}


@bottle.get('/thing_header')
def hello():
    thing_id = bottle.request.headers['thing_id']
    return {"id": thing_id, "name": "Thing{}".format(thing_id)}


@bottle.post('/thing_formdata')
def hello():
    thing_id = bottle.request.forms['thing_id']
    return {"id": thing_id, "name": "Thing{}".format(thing_id)}


@bottle.post('/thing')
def hello():
    return bottle.request.json

