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


class UsersAuth2DataBlock(Resource, MongoDB):
    def __init__(self):
        super(UsersAuth2DataBlock, self).__init__()


    ## fetch user's data
    def get(self, f_name, uid):
        res = self.find_user_by_uid(uid)
        
        if res == None:
            return {
                    "action":"GET",
                    "inner_action":"FIND",
                    "status":404,
                    "errorMsg":"user uid not exist"
                }, 404

        elif f_name != res['family_name']:
            return {
                "action":"GET",
                "status":404,
                "inner_action":"FIND",
                "errorMsg":"wrong family name"
            }, 404

        else:
            return {
                    "user":
                    {
                        "uid":str(res['uid']),
                        "mac_addr":res['mac_addr'],
                        "user_name":res['user_name'],
                        "created_at":res['created_at'],
                        "family_name":res['family_name'],
                        "google_token":res['google_token']
                    }
                }, 200
        

    ## leave family
    def delete(self, f_name, uid):
        res = self.unregister_from_family(f_name, uid)

        if 'errorMsg' in res:
            return res, 404
        else:
            res['entity-body'] = res
            return res, 207


    def put(self, f_name, uid):
        pass


class UsersAuth1DataBlock(Resource, MongoDB):
    def __init__(self):
        super(UsersAuth1DataBlock, self).__init__()


    def get(self, uuid):
        res = self.find_all_members(uuid)
        logger.info(res)
        if 'errorMsg' in res:
            return res, 404         

        else:
            resp = {
                "users":[],
                "member_count":self.count_members(res[0]['family_name'])
            }
            for mem in res:
                resp['users'].append(
                    {
                        "uid":str(mem['uid']),
                        "mac_addr":mem['mac_addr'],
                        "user_name":mem['user_name'],
                        "created_at":mem['created_at'],
                        "family_name":mem['family_name'],
                        "google_token":mem['google_token']
                    })
            return resp, 200



class UsersIndex(Resource, MongoDB):
    def __init__(self):

        ## set prerequisites for requests
        ## this will handle error messages if invalide 
        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_post.add_argument('user_name', 
            type=str, 
            required=True, 
            location='json', 
            help="missing user name")

        self.reqparse_post.add_argument('uuid', 
            type=str, 
            required=True, 
            location='json', 
            help="missing uuid")

        self.reqparse_post.add_argument('mac_addr',
            type=str,
            required=True,
            location='json',
            help='missing mac_addr of the member')

        self.reqparse_post.add_argument('google_token',
            type=str,
            required=True,
            default=None,
            location='json',
            help='missing google token of the user, recommended to update sooner or later')

        super(UsersIndex, self).__init__()


    ## for getting members in the family
    def get(self, f_name):
        resp = {
            "version":"v1",
            "users":[]
        }

        mems = self.find_all_members(f_name)
        if not mems:
            return {
                    "action":"GET",
                    "status":404,
                    "errorMsg":"family name "+f_name+" not exist"
                }, 404
        else:
            logger.info(mems)
            for mem in mems:
                resp['users'].append({
                        "user_name":mem['user_name'],
                        "mac_addr":"<string:mac_addr>",
                        "google_token":"<string:google_token>",
                        "links":[
                        {
                            "href":"/family/"+mem['family_name']+"/users/<string:uid>",
                            "method":"GET",
                            "rel":"self"
                        },
                        {
                            "href":"/family/<string:uuid>/users/all",
                            "method":"GET",
                            "rel":"list"
                        },
                        {
                            "href":"/family/"+mem['family_name']+"/users",
                            "method":"POST",
                            "rel":"create"
                        },
                        {
                            "href":"/family/"+mem['family_name']+"/users/<string:uid>",
                            "method":"PUT",
                            "rel":"update"
                        },
                        {
                            "href":"/family/"+mem['family_name']+"/users/<string:uid>",
                            "method":"DELETE",
                            "rel":"unregister"
                        }]
                    })

            return resp, 200


    ## creating a new user to the family
    def post(self, f_name):
        args = self.reqparse_post.parse_args()
        args['family_name'] = f_name
        res = self.update_family_member(**args)
        logger.info(res)

        if res != False and not 'errorMsg' in res:
            return {
                    "action":"POST",
                    "status":"succeed",
                    "data":
                    {
                        "uid":str(res['uid']),
                        "uuid":str(res['uuid']) 
                    }
                }, 200

        elif res is not False and 'errorMsg' in res:
            return res, res['status']

        else:
            return {
                "inner_action":"CHECK",
                "action":"POST",
                "status":"error", 
                "errMsg":"either user already belongs to a family"+
                " or family name not exists"
            }, 400
