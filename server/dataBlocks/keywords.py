####################################
## Readable code versus less code ##
####################################

import config
import logging as logger
import json

from ..api.api import KeywordsHandler
from ..model_mongodb import MongoDB

try:
    from flask.ext.restful import Resource, reqparse, Response
except:
    from flask_restful import Resource, reqparse


class KeyWordsAdd(Resource, MongoDB): 
    def __init__(self):
        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)
        self.reqparse_post.add_argument('text', 
            type=str, 
            required=True, 
            location='json', 
            help="missing text")
        super(KeyWordsAdd, self).__init__()

    def post(self):
        arg = self.reqparse_post.parse_args()
        res = self.meta._store_metadata_keywords(arg)
        return 200

class KeyWords(Resource, MongoDB): 
    def __init__(self):
        super(KeyWords, self).__init__()


    ## get family info, requires uuid
    def get(self, text):
        res = self.meta._get_vector_simiarity(text.replace("_", " "))
        return res['data']