####################################
## Readable code versus less code ##
####################################

import config
import logging as logger
import json
import os

from exceptions import RequestException
from flask_restful import Resource, Api, reqparse
from flask import Blueprint, Flask, redirect, request, url_for, Response

from .dataBlocks.comments import CommentsDataBlock, CommentsIndex
from .dataBlocks.requests_item import RequestsAuth2DataBlock, RequestsAuth1DataBlock, RequestsIndex, RequestManyAuthDataBlock, RequestImageDataBlock
from .dataBlocks.family import FamilyDataBlock, FamilyIndex
from .dataBlocks.base import BaseURIs
from .dataBlocks.users import UsersAuth2DataBlock, UsersAuth1DataBlock, UsersIndex

#from flask_restful import Resource, Api, reqparse

ms = Blueprint('ms', __name__)
photo_storage_path = "/var/www/html/Family-Shopping-Cart/server/photo_data_testing/"

from model_mongodb import MongoDB

class DataBlock(Resource, MongoDB):
    def __init__(self):

        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_post.add_argument('photo', 
            type=str, 
            required=True, 
            location='json', 
            help="missing uuid")

        super(DataBlock, self).__init__()

    def get(self):
        with os.fdopen(os.open(photo_storage_path+"newfileGet.txt", 
                os.O_RDWR|os.O_CREAT),'w+') as outfile:
            rdata = outfile.read()
            outfile.close()
            return rdata, 200
        return 200

    def post(self):
        args = self.reqparse_post.parse_args()
        
        with os.fdopen(os.open(photo_storage_path+"newfileGet.txt", 
                os.O_RDWR|os.O_CREAT),'w+') as outfile:
            outfile.write(args['photo'])
            outfile.close()
        return 200



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

    # [START RequestImageDataBlock, handled methods : DELETE]
    api.add_resource(RequestImageDataBlock, 
        '/family/<string:f_name>/requests/<string:req_uuid>/images/<string:image_id>',
        methods=['DELETE'], 
        endpoint='/family/<family_name>/requests/<request_id>/images/<image_id>')
    # [END RequestImageDataBlock, handled methods : DELETE]

    # [START RequestsIndex, handled methods : GET]
    api.add_resource(RequestsIndex,
        '/family/requests',
        methods=['GET'],
        endpoint='/family/<family_name>/requests')
    # [END RequestsIndex, handled methods : GET]


    api.add_resource(DataBlock, '/test/request/photo',methods=['POST', 'GET'],endpoint='/test/request/photo')


    ## index of the api
    api.add_resource(BaseURIs, '/')

    return api

