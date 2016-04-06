#!/Python27/python

#from manage import app
from flask import Blueprint, Response, request, g, json, make_response
from flask_restful import Resource

import api

private_key = api.generate_private_key
public_key = api.generate_public_key(private_key)

import redis


red = redis.StrictRedis()

web_server = Blueprint('web_server', __name__)

def register_family():
	#resp = make_response("good job", 201)
	data = {
		"uid":api.__uuid_generator_4()
	}
	resp = make_response(json.dumps(data), 201)

	return resp
	#return resp

def families():
	return 200

def create_family_group(tagID):
    data = {
        "uid":api.__uuid_generator_4()
    }
    #resp = make_response(json.dumps(data), 201)
    print "Connection started"
    resp = Response(event_stream(tagID), mimetype="text/event-stream")
    return resp


def event_stream(channel):
    pubsub = red.pubsub()
    pubsub.subscribe(channel)
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']

web_server.add_url_rule('/create_family_group/<tagID>', 
	'create_family_group', 
	create_family_group, 
	methods=['GET'])