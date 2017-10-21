from summer2017_db import CG_DB

try:
    from flask.ext.restful import Resource, reqparse, Response
except:
    from flask_restful import Resource, reqparse


class CommunityGraffityInterface(Resource, CG_DB):
    def __init__(self):
        self.reqparse_post = reqparse.RequestParser(bundle_errors=True)

        self.reqparse_post.add_argument('location',
            type=str,
            required=True,
            location='json',
            help="missing location")

        self.reqparse_post.add_argument('text',
            type=str,
            required=True,
            location='json',
            help="missing text")


        super(CommunityGraffityInterface, self).__init__()


    def get(self):
        resp = {"texts":[]}
        texts = self.get_texts()

        for text in texts:
            resp["texts"].append({
                "text":text['text'],
                "location":text['location']
            })
        return resp, 200


    def post(self):
        res = self.add_text(**self.reqparse_post.parse_args())

        if not res == False:
            return res
        else:
            "add text error!"

