####################################
## Readable code versus less code ##
####################################

import config
import logging as logger
import json

from exceptions import RequestException
from flask import Blueprint, Flask, redirect, request, Response, url_for

from .dataBlocks.comments import CommentsDataBlock, CommentsIndex
from .dataBlocks.requests_item import RequestsAuth2DataBlock, RequestsAuth1DataBlock, RequestsIndex, RequestManyAuthDataBlock
from .dataBlocks.family import FamilyDataBlock, FamilyIndex
from .dataBlocks.base import BaseURIs
from .dataBlocks.users import UsersAuth2DataBlock, UsersAuth1DataBlock, UsersIndex

try:
    from flask.ext.restful import Resource, Api, reqparse
except:
    from flask_restful import Resource, Api, reqparse

try:
    from flask_restful import Resource, Api, reqparse
    # support local usage without installed package
except:
    from flask.ext.cors import cross_origin
    # this is how you would normally import

ms = Blueprint('ms', __name__)

from model_mongodb import MongoDB

class DataBlock(Resource, MongoDB):
    def __init__(self):

        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_post.add_argument('uuid', 
            type=str, 
            required=True, 
            location='json', 
            help="missing uuid")

        self.reqparse_post.add_argument('sender', 
            type=dict, 
            required=True, 
            location='json', 
            help="missing sender")

        self.reqparse_post.add_argument('requests', 
            type=list, 
            required=True, 
            location='json', 
            help="missing requests")

        super(DataBlock, self).__init__()

    def post(self, arg):
        args = self.reqparse_post.parse_args()
        args['family_name'] = arg
        res = self.create_requests(**args)
        #raise RequestException("what exception?")
        return str(res), 200

    def get(self, arg):
        res = self._convert_id_to_humanreadable("tellus","5f6ebdac-f368-40e8-a7cf-4ff929591afe")
        return res



def init_restful():
    api = Api(ms)
    # [START CommentsDataBlock, handled methods : POST, GET]
    api.add_resource(CommentsDataBlock,
        '/family/<string:f_name>/requests/<string:arg>/comments',
        methods=['GET', 'POST'],  
        endpoint='/family/<family_name>/requests/<item_or_req_uuid>/comments>')
    # [END CommentsDataBlock, handled methods : POST, GET]


    ## @NOTE! this PUT is deprecated !! use /family/family_name/users instead
    # [START FamilyDataBlock, handled methods : GET, PUT]
    api.add_resource(FamilyDataBlock,
        '/family/<string:arg>',
        methods=['GET', 'PUT'],  
        endpoint='/family/<family_name_or_uuid>')
    # [END FamilyDataBlock, handled methods : GET, PUT]


    # [START FamilyIndex, handled methods : GET, POST]
    api.add_resource(FamilyIndex,
        '/family',
        methods=['GET', 'POST'],
        endpoint='/family')
    # [END FamilyIndex, handled methods : GET, POST]


    # [START UsersIndex, handled methods : GET, POST]
    api.add_resource(UsersIndex,
        '/family/<string:f_name>/users',
        methods=['GET','POST'],
        endpoint='/family/<family_name>/users')
    # [END UsersIndex, handled methods : GET, POST]


    # [START UsersAuth2DataBlock, handled methods : GET, DELETE]
    api.add_resource(UsersAuth2DataBlock,
        '/family/<string:f_name>/users/<string:uid>',
        methods=['GET', 'DELETE'],
        endpoint='/family/<family_name>/users/<uid>')
    # [END UsersAuth2DataBlock, handled methods : GET, DELETE]
    

    # [START UsersAuth1DataBlock, handled methods : GET]
    api.add_resource(UsersAuth1DataBlock,
        '/family/<string:uuid>/users/all',
        methods=['GET'],
        endpoint='/family/<uuid>/users/all')
    # [END UsersAuth1DataBlock, handled methods : GET]


    # [START RequestsAuth1DataBlock, handled methods : GET, DELETE]
    api.add_resource(RequestsAuth1DataBlock, 
        '/family/<string:f_name>/requests/<string:req_uuid>',
        methods=['GET', 'DELETE'], 
        endpoint='/family/<family_name>/requests/<req_uuid>')
    # [END RequestsAuth1DataBlock, handled methods : GET, DELETE]


    # [START RequestAuth2DataBlock, handled methods : GET, POST, 'PUT']
    api.add_resource(RequestsAuth2DataBlock, 
        '/family/<string:arg>/requests',
        methods=['GET', 'POST', 'PUT'], 
        endpoint='/family/<uuid_or_family_name>/requests')
    # [END RequestsAuth2DataBlock, handled methods : GET, POST, 'PUT']


    # [START RequestManyAuthDataBlock, handled methods : POST]
    api.add_resource(RequestManyAuthDataBlock, 
        '/family/<string:f_name>/requests/many',
        methods=['POST'], 
        endpoint='/family/<family_name>/requests/many')
    # [END RequestManyAuthDataBlock, handled methods : POST]


    # [START RequestsIndex, handled methods : GET]
    api.add_resource(RequestsIndex,
        '/family/requests',
        methods=['GET'],
        endpoint='/family/<family_name>/requests')
    # [END RequestsIndex, handled methods : GET]


    api.add_resource(DataBlock, '/test/<string:arg>',methods=['POST', 'GET'],endpoint='/test/family_name')


    ## index of the api
    api.add_resource(BaseURIs, '/')

    return api

#api.add_resource(DataBlock2, '/family/<string:name>')



"""
@ms.route('/help', methods=['GET'])
def hi():
    logger.info("hi man2")
    return "data"

@ms.route('/create/<title>', methods=['GET'])
def create(title):
    logger.info("hi man3")
    result = get_model().create({"title":title})

    return str(result)


@ms.route('/find/<item>', methods=['GET'])
def find_by_name(item):
    logger.info("haejong test1 was called")
    return get_model().find_one(item)


@ms.route('/count', methods=['GET'])
def test3():
    return render_template("call.html")"""


"""
errors = {
    'UserAlreadyExistsError': {
        'message': "A user with that username already exists.",
        'status': 409,
    },
    'ResourceDoesNotExist': {
        'message': "A resource with that ID no longer exists.",
        'status': 410,
        'extra': "Any extra information you want.",
    },
}

app = Flask(__name__)
api = flask_restful.Api(app, errors=errors)
"""


"""
for mem in f_info['members']:
    user = self.find_user_by_id(mem['user_id'])
    resp['family'].append(
        {
            "family_name":user['family_name'],
            "mac_addr":user['mac_addr'],
            "google_token":user['google_token']
        })"""