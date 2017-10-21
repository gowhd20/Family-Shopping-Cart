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


class SummerSchool2017(Resource, MongoDB): 
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