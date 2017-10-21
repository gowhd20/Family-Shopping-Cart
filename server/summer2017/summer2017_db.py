from . import db_config
from .api import api
import base64

try:
    from pymongo import MongoClient
    # support local usage without installed package
except:
    from flask.ext.pymongo import PyMongo, MongoClient

class CG_DB(object):

    def __init__(self):
        client = MongoClient(db_config.MONGO_URI_CUSTOM, db_config.PORT)
        self.db = client['ms']
        self.db.authenticate(db_config.USERNAME, db_config.PASSWORD)
        super(CG_DB, self).__init__()



    def add_text(self, **args):
        if not 'text' in args:
            return False
        if not 'location' in args:
            return False

        new_c = self.db.text.insert_one(
        ## creation time will base on local time of where the server is seated
        ## store as epoch/unix time
        {
            "created_at":api.get_unix_from_datetime(api.get_current_time()),
            "location":args['location'],
            "text":args['text']
        })
        return new_c.inserted_id

    def get_texts(self):
        return map(lambda f:{
                "text":base64.b64decode(f['text']),
                "location":base64.b64decode(f['location'])
            }, self.db.text.find())

