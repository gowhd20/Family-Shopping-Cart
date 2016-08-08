####################################
## Readable code versus less code ##
####################################

import config
import logging as logger
import json

from ..model_mongodb import MongoDB

try:
    from flask.ext.restful import Resource, reqparse, Response
except:
    from flask_restful import Resource, reqparse


class FamilyDataBlock(Resource, MongoDB): 
    def __init__(self):
        ## set prerequisites for requests
        ## this will handle error messages if invalide 
        self.reqparse_put = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_put.add_argument('user_name', 
            type=str, 
            required=True, 
            location='json', 
            help="missing user name")

        self.reqparse_put.add_argument('uuid', 
            type=str, 
            required=True, 
            location='json', 
            help="missing uuid")

        self.reqparse_put.add_argument('mac_addr',
            type=str,
            required=True,
            location='json',
            help='missing mac_addr of the member')

        self.reqparse_put.add_argument('google_token',
            type=str,
            required=True,
            default=None,
            location='json',
            help='missing google token of the user, recommended to update sooner or later')

        super(FamilyDataBlock, self).__init__()


    ## get family info, requires uuid
    def get(self, arg):
        res = self.find_family_by_uuid(arg)
        logger.info(res)

        if res == None:
            return {
                    "action":"GET",
                    "status":"error",
                    "errorMsg":"family name/uuid not exists",
                    "inner_action":"FIND"
                }, 404
        elif 'errorMsg' in res:
            return res, 404

        else:
            return {
            "family":
            {
                "family_name":res['family_name'],
                "created_at":res['created_at'],
                "uuid":str(res['uuid']),
                "requests":
                {
                    "links":[
                    {
                        "href":"/family/<string:uuid>/requests",
                        "method":"GET",
                        "rel":"list"
                    }]
                },
                "members":
                {
                    "links":[
                    {
                        "href":"/family/<string:family_name>/users",
                        "method":"GET",
                        "rel":"list"
                    }]
                }
            }
        }, 200


    ## for update family members
    def put(self, arg):
        args = self.reqparse_put.parse_args()
        args['family_name'] = arg
        res = self.update_family_member(**args)
        logger.info(res)

        if res != False and not 'errorMsg' in res:
            return {
                    "action":"PUT",
                    "status":"succeed",
                    "data":
                    {
                        "uid":str(res['uid']),
                        "uuid":str(res['uuid']) 
                    }
                }, 200
        else:
            return {
                "inner_action":"CHECK",
                "action":"PUT",
                "status":"error", 
                "errMsg":"either user already belongs to a family"+
                " or family name not exists"
            }, 400
        

class FamilyIndex(Resource, MongoDB):
    def __init__(self):
        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_post.add_argument('family_name', 
            type=str, 
            required=True, 
            location='json', 
            help="missing family name")

        self.reqparse_post.add_argument('user_name', 
            type=str, 
            required=True, 
            location='json', 
            help="missing user name")

        self.reqparse_post.add_argument('mac_addr', 
            type=str, 
            required=True, 
            location='json', 
            help="missing mac address")

        self.reqparse_post.add_argument('google_token', 
            type=str, 
            required=True, 
            location='json', 
            help="missing google token")

        super(FamilyIndex, self).__init__()


    ## list of families
    def get(self):
		families = self.find_all_families()
		resp = {"families":[]}

		for family in families:       
		    resp["families"].append({
		        "family_name":family['family_name'],
		        "requests":
		        {
		            "href":"/family/requests",
		            "method":"GET",
		            "rel":"index"
		        },
		        "members":
		        {
		            "users":
		            {
		                "href":"/family/"+family['family_name']+"/users",
		                "method":"GET",
		                "rel":"list"
		            }
		        },
		        "links":[
		        {
		            # family info in detail
		            "href":"/family/<string:uuid>",
		            "rel":"self",
		            "method":"GET"
		        },
		        {
		            "href":"/family/"+family['family_name'],
		            "rel":"update",
		            "method":"PUT",
		            "required":[
		            {
		                "uuid":"<string:uuid>",
		                "user_name":"<string:user_name>",
		                "mac_addr":"<string:mac_addr>",
		                "google_token":"<string:google_token>"
		            }]
		        }]
		    })
		return resp, 200


    ## for creating family
    def post(self):
        res = self.create_family(**self.reqparse_post.parse_args())
        logger.info(res)

        if res != False:
            return {
                    "action":"POST",
                    "status":201,
                    "data":
                    {
                        "uid":str(res['uid']),
                        "uuid":str(res['uuid'])
                    }
                }, 201

        elif res == False:
            return {
                    "action":"POST",
                    "status":409, 
                    "inner_action":"CHECK",
                    "errMsg":"family name already exists or " +
                    "this user has been registered to another family group"
                }, 409

        elif 'errorMsg' in res:
            return res, 400

