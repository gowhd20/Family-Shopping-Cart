####################################
## Readable code versus less code ##
####################################

import config
import logging as logger
import json

from ..model_mongodb import MongoDB

try:
    from flask.ext.restful import Resource, reqparse
except:
    from flask_restful import Resource, reqparse


class BaseURIs(Resource):
    def __init__(self):
        super(BaseURIs, self).__init__()


    def get(self):
        return {
            "version":"v1",
            "links":[
            {
                "href":"/family",
                "rel":"list",
                "method":"GET"
            },
            {
                "href":"/family",
                "rel":"create",
                "method":"POST",
                "required":[
                    {
                        "family_name":"<string:family_name>", 
                        "user_name":"<string:user_name>",
                        "mac_addr":"<string:mac_addr>",
                        "google_token":"<string:google_token>"
                    }]
            }]
        }, 200