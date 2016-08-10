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


class RequestsAuth2DataBlock(Resource, MongoDB):
    def __init__(self):

        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_post.add_argument('item', 
            type=str, 
            required=True, 
            location='json', 
            help="missing item name")

        self.reqparse_post.add_argument('sender', 
            type=dict, 
            required=True, 
            location='json', 
            help="missing sender")

        self.reqparse_post.add_argument('receivers', 
            type=list, 
            required=True, 
            location='json',
            action='append', 
            help="missing receivers, at least one is required")

        self.reqparse_post.add_argument('uuid', 
            type=str, 
            required=True, 
            location='json',
            help="missing uuid")

        self.reqparse_post.add_argument('optional_data', 
            type=dict, 
            required=False,
            default={"optional_data":"no_data_given"}, 
            location='json')

        self.reqparse_post.add_argument('locality_info', 
            type=dict, 
            required=False, 
            location='json')


        self.reqparse_put = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_put.add_argument('req_uuid', 
            type=str, 
            required=True, 
            location='json', 
            help="missing request id")

        self.reqparse_put.add_argument('uuid',
            type=str,
            required=True,
            location='json',
            help='missing family id')

        ## when uid is included, server recognizes the command
        ## as deletion of the uid from acceptors 
        self.reqparse_put.add_argument('uid',
            type=str,
            required=False,
            location='json')

        self.reqparse_put.add_argument('data_to_update',
            type=dict,
            required=False,
            location='json')

        super(RequestsAuth2DataBlock, self).__init__()


    def get(self, arg):
        reqs = self.find_all_requests(arg)

        if 'errorMsg' in reqs:
            return reqs, 404
        else:
            resp = {
                "requests":[],
                "req_count":self.count_requests(arg),
                "action":"GET",
                "status":200,
                "images":{
                    "href":"/family/<string:family_name>/requests/<string:req_uuid>/images",
                    "method":"GET",
                    "rel":"list"
                },
                "links":[
                {
                    "href":"/family/<string:uuid>/requests",
                    "method":"GET",
                    "rel":"list"
                },
                {
                    "href":"/family/<string:uuid>/requests",
                    "method":"POST",
                    "rel":"create",
                    "required":
                    {
                        "item":"<string:item>",
                        "sender":
                        {
                            "uid":"<string:uid>"
                        },
                        "receivers":[
                        {
                            "uid":"<string:uid>"
                        }],
                        "uuid":"<string:uuid>"
                    }
                },
                {
                    "href":"/family/<string:family_name>/requests",
                    "method":"PUT",
                    "rel":"update",
                    "required":
                    {
                        "uuid":"<string:uuid>",
                        "req_uuid":"<string:req_uuid>"
                    }
                },
                {
                    "href":"/family/<string:family_name>/requests",
                    "method":"DELETE",
                    "rel":"unregister"
                }]
            }

            for req in reqs:
                resp['requests'].append(
                    {
                        "created_at":None if not 'created_at' in req else req['created_at'],
                        "req_uuid":None if not 'req_uuid' in req else str(req['req_uuid']),
                        "owner":None if not 'owner' in req else req['owner'],
                        "item":None if not 'item' in req else req['item'],
                        "images":None if not 'images' in req else req['images'],
                        "sender":None if not 'sender' in req else req['sender'],
                        "time_of_need":None if not 'time_of_need' in req else req['time_of_need'],
                        "urgency":None if not 'urgency' in req else req['urgency'],
                        "location":None if not 'location' in req else req['location'],
                        "price":None if not 'price' in req else req['price'],
                        "description":None if not 'description' in req else req['description'],
                        "comments":None if not 'comments' in req else req['comments'],
                        "receivers":None if not 'receivers' in req else req['receivers'],
                        "acceptors":None if not 'acceptors' in req else req['acceptors']
                    })

            return resp, 200


    def post(self, arg):
        args = self.reqparse_post.parse_args()
        args['family_name'] = arg
        res = self.create_request(**args)

        if 'errorMsg' in res:
            return res, int(res['status'])
        else:
            return res, 201


    ## list of values available to update::
    ## time_of_need, urgency, description, comments, acceptors
    def put(self, arg):     # arg: family name
        args = self.reqparse_put.parse_args()
        args['family_name'] = arg

        res = self.update_requests_info(**args)
        return res, res['status']


class RequestsAuth1DataBlock(Resource, MongoDB):
    def __init__(self):

        super(RequestsAuth1DataBlock, self).__init__()


    def get(self, f_name, req_uuid):
        res = self.find_one_request(f_name, req_uuid)
        logger.info(res)
        if 'errorMsg' in res:
            return res, res['status']

        else:
            return {
                "created_at":None if not 'created_at' in res else res['created_at'],
                "req_uuid":None if not 'req_uuid' in res else str(res['req_uuid']),
                "owner":None if not 'owner' in res else res['owner'],
                "item":None if not 'item' in res else res['item'],
                "images":None if not 'images' in res else res['images'],
                "sender":None if not 'sender' in res else res['sender'],
                "time_of_need":None if not 'time_of_need' in res else res['time_of_need'],
                "urgency":None if not 'urgency' in res else res['urgency'],
                "location":None if not 'location' in res else res['location'],
                "price":None if not 'price' in res else res['price'],
                "description":None if not 'description' in res else res['description'],
                "comments":None if not 'comments' in res else res['comments'],
                "receivers":None if not 'receivers' in res else res['receivers'],
                "acceptors":None if not 'acceptors' in res else res['acceptors']
            }


    def delete(self, f_name, req_uuid):
        res = self.remove_request(f_name, req_uuid)
        return res, res['status']


class RequestImageDataBlock(Resource, MongoDB):
    def __init__(self):
        super(RequestImageDataBlock, self).__init__()


    def delete(self, f_name, req_uuid, image_id):
        res = self.remove_image(f_name, req_uuid, image_id)
        return res, res['status']


class RequestImagesDataBlock(Resource, MongoDB):
    def __init__(self):
        super(RequestImagesDataBlock, self).__init__()


    def get(self, f_name, req_uuid):
        res = self.find_request_images(f_name, req_uuid)
        res['links'] = [
        {
            "href":"/family/"+f_name+"/requests/"+req_uuid+"/images/",
            "method":"GET",
            "rel":"list"
        },
        {
            "href":"/family/"+f_name+"/requests/"+req_uuid+"/images/<string:image_name>",
            "method":"DELETE",
            "rel":"remove"
        }]
        return res, res['status']


class RequestManyAuthDataBlock(Resource, MongoDB):
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
            type=nested_data_validation, 
            required=True, 
            location='json', 
            help="missing requests or one or more nested data is corrupted")

        self.reqparse_post.add_argument('locality_info', 
            type=dict, 
            required=False, 
            location='json')

        super(RequestManyAuthDataBlock, self).__init__()


    def post(self, f_name):
        args = self.reqparse_post.parse_args()
        args['family_name'] = f_name
        logger.info(args)
        res = self.create_many_requests(**args)
        
        if not 'errorMsg' in res:
            return {
                "action":"POST",
                "status":201,
                "data":res
            }, 201

        else:
            return res, res['status']

def nested_data_validation(data):
    for i in range(len(data)):
        req_json = data[i]

        if 'item' not in req_json or req_json['item'] is None:
            raise ValueError("item is missing")
        
        if 'receivers' not in req_json:
            raise ValueError("receivers is missing or wrong type")
        elif type(req_json['receivers']) is not list:
            raise ValueError("receivers is wrong type")
        elif len(req_json['receivers'])<1:
            raise ValueError("receivers is empty")
        else:
            for j in range(len(req_json['receivers'])):
                receivers = req_json['receivers'][j]
                if 'uid' not in receivers:
                    raise ValueError("receivers does not include uid as value")
        
    return data


class RequestsIndex(Resource):
    def __init__(self):
        super(RequestsIndex, self).__init__()


    def get(self):
        return {
            "version":"v1",
            "links":[
            {
                "href":"/family/<string:uuid>/requests",
                "method":"GET",
                "rel":"list"
            },
            {
                "href":"/family/<string:uuid>/requests",
                "method":"POST",
                "rel":"create",
                "required":
                {
                    "item":"<string:item>",
                    "sender":
                    {
                        "uid":"<string:uid>"
                    },
                    "receivers":[
                    {
                        "uid":"<string:uid>"
                    }],
                    "uuid":"<string:uuid>"
                }
            },
            {
                "href":"/family/<string:family_name>/requests",
                "method":"PUT",
                "rel":"update",
                "required":
                {
                    "uuid":"<string:uuid>",
                    "req_uuid":"<string:req_uuid>"
                }
            },
            {
                "href":"/family/<string:family_name>/requests",
                "method":"DELETE",
                "rel":"unregister"
            }]
        }





