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


class CommentsDataBlock(Resource, MongoDB):
    def __init__(self):

        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_post.add_argument('user_name', 
            type=dict, 
            required=True, 
            location='json', 
            help="missing user_name")

        self.reqparse_post.add_argument('mac_addr', 
            type=dict, 
            required=True, 
            location='json', 
            help="missing mac_addr")

        self.reqparse_post.add_argument('comment', 
            type=str, 
            required=False, 
            location='json')

        self.reqparse_post.add_argument('req_uuid', 
            type=str, 
            required=True, 
            location='json',
            help="missing req_uuid")

        super(CommentsDataBlock, self).__init__()


    def get(self, f_name, arg):
        res = self.find_one_request(f_name, arg)
        if 'errorMsg' in res:
            return res, res['status']

        else:
            resp = []
            for c in res['comments']:
                resp.append(
                    {
                        "user_name":c['user_name'],
                        "comment":c['comment']
                    })
            return resp, 200


    def post(self, f_name, item):
        args = self.reqparse_post.parse_args()
        args['family_name'] = f_name
        args['item'] = arg


class CommentsIndex(Resource):
    def __init__(self):
        super(CommentsIndex, self).__init__()

    def get(self, f_name):
        return {
            "version":"v1",
            "owner":
            {
                "href":"/family/<string:uuid>/"+f_name,
                "name":f_name
            },
            "links":[
            {
                "method":"GET",
                "rel":"lists",
                "href":"/family/"+f_name+"/requests/<string:req_uuid>/comments"
            },
            {
                "method":"POST",
                "rel":"create",
                "href":"/family/"+f_name+"/requests/<string:req_uuid>/comments",
                "required":
                {
                    "user_name":"<string:user_name>",
                    "mac_addr":"<string:mac_addr>",
                    "req_uuid":"<string:req_uuid>"
                }
            }]
        }