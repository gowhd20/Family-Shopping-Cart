####################################
## Readable code versus less code ##
####################################

from . import db_config
from .api import api
from gcm import GCM
from . import gcm_config
from . import weather_api_config

from pprint import pprint   # for debugging

## for caching weather data
from werkzeug.contrib.cache import SimpleCache ## modified 24/06/2016 while migration

from flask_restful import Resource, Api, reqparse
#from pymongo import ReturnDocument
try:
    from pymongo import PyMongo, MongoClient
    # support local usage without installed package
except:
    from flask.ext.pymongo import PyMongo, MongoClient

import json
import requests
#from flask.ext.mongoengine import *#MongoEngine, MongoEngineSessionInterface, Document

logger = api.__get_logger("model_mongodb")

cache = SimpleCache()

## @Note, __method won't be able to be called within the class
class MongoDB(object):

    _KEY_TYPES = frozenset(["created_at", "req_uuid", "owner", "item", "sender",
        "time_of_need", "urgency", "location", "price", "description", "comments",
        "receivers", "acceptors"])

    def __init__(self):
        client = MongoClient(db_config.MONGO_URI_CUSTOM, db_config.PORT)
        self.db = client['ms']
        self.db.authenticate(db_config.USERNAME, db_config.PASSWORD)
        self.weather_api_key = weather_api_config.API_KEY
        self.weather_url_config = weather_api_config.config_url
        self.gcm_api_key = gcm_config.API_KEY
        ## make a new request only more than 10 mins passed after the last request
        self.timeframe_allows_requests = 10*60*1

        from .mongo_meta import MongoMetaData
        self.meta = MongoMetaData(self.db)

    # [START create a new family]
    def create_family(self, **args):
        if self._check_family_name_exist(args['family_name']):
            return False

        elif self._check_user_exist(args['mac_addr']):
            return False

        else:
            ## uuid is for wild environment use
            uuid = api.uuid_generator_4()  
            
            new_f = self.db.family.insert_one(
            ## creation time will base on local time of where the server is seated
            ## store as epoch/unix time
            {
                "created_at":api.get_unix_from_datetime(api.get_current_time()),
                "uuid":uuid,
                "family_name":args['family_name'],
                "requests":[],
                "members":[]
            })

            logger.info("family count: "+str(self.count_families()))
            ## store _uid and send out uuid for wild use
            self._key_mapper({"secret":new_f.inserted_id, "uuid":uuid})
            f_info = self._find_family_by_id(new_f.inserted_id)
            args['uuid'] = uuid         ## Modified 23/6/2016
            ## register user to the family
            res = self.update_family_member(**args)
            if res == False:
                return res

            elif 'errorMsg' in res:
                return res

            else:                
                ## uid => user's id, uuid => family id
                return {
                    "uuid":res['uuid'],
                    "uid":res['uid']
                    }
    # [END create a new family]


    # [START count families in the database]
    def count_families(self):
        return self.db.family.count()
    # [END count families in the database]


    # [START count family members in the database]
    def count_members(self, f_name):
        return self.db.users.find(
            {
                "family_name":f_name
            }).count()
    # [END count family members in the database]


    # [START count requests in the database]
    def count_requests(self, uuid):
        f_id = self.__get_secure_id(uuid)
        f_info = self._find_family_by_id(f_id)

        return self.db.requests.find(
            {
                "owner":f_info['family_name']
            }).count()
    # [END count requests in the database]


    # [START create a new collection of requests]
    def create_request(self, **args):
        f_id = self.__get_secure_id(args['uuid'])
        logger.info(f_id)

        if f_id == None:
            return {
                "action":"POST",
                "status":404,
                "errorMsg":"uuid not exist"
            }

        else:
            f_info = self._find_family_by_id(f_id)

            if f_info == None:
                return {
                    "action":"POST",
                    "inner_action":"CHECK",
                    "status":404,
                    "errorMsg":"uuid does not match with family's id"
                }

            else:                   
                if f_info['family_name'] != args['family_name']:
                    return {
                        "action":"POST",
                        "status":400,
                        "errorMsg":"uuid doesn't match with the family name"
                    }

                else:
                    req_uuid = api.uuid_generator_4()
                    opt_data = args['optional_data'] if args['optional_data'] is not None else {"default":"no_data_given"}
                    receivers = args['receivers'][0]

                    if 'images' in opt_data:
                        loimages = self.meta.store_metadata_image(
                            f_info['family_name'], opt_data['images'])
                     
                    new_r = self.db.requests.insert_one(
                        {
                            "created_at":api.get_unix_from_datetime(api.get_current_time()),
                            "req_uuid":req_uuid,
                            "owner":f_info['family_name'],
                            "item":args['item'],
                            "sender":args['sender'],
                            "images":map(lambda x:x['id'], loimages) if 'images' in opt_data else None,     ##  store ids generated above
                            "time_of_need":opt_data['time_of_need'] if 'time_of_need' in opt_data else None,
                            "urgency":opt_data['urgency'] if 'urgency' in opt_data else 0,
                            "location":opt_data['location'] if 'location' in opt_data else None,
                            "price":opt_data['price'] if 'price' in opt_data else None,
                            "description":opt_data['description'] if 'description' in opt_data else None,
                            "comments":[],
                            "acceptors":[],
                            "receivers":receivers    # [{"uid":receiver1}, {"uid":receiver2}, ...]}
                        })

                    if new_r.inserted_id != None:
                        self._key_mapper({"secret":new_r.inserted_id, "uuid":req_uuid})

                        api.write_image_file(loimages)

                        ## register to family document
                        res = self._register_new_request(new_r.inserted_id, f_id)
                        if 'errorMsg' in res:
                            return res

                        ## register succeed
                        else:
                            ## send gcm to members in the receivers
                            req = self.find_one_request(f_info['family_name'], req_uuid)

                            ## data to send in a downstream message
                            data = {
                                "created_at":req['created_at'],
                                "item":req['item'],
                                "owner":req['owner'],
                                "location":req['location'],
                                "req_uuid":str(req['req_uuid']),
                                "description":req['description'],
                                "price":req['price'],
                                "receivers":list(r['uid'] for r in req['receivers']),
                                "urgency":req['urgency'],
                                "sender":req['sender']['uid']
                            }
                            
                            tks = self._find_google_token_by_uid(receivers)

                            #if tks is not None:
                            #    self._make_gcm_request(tks, data=data)

                            loc = args['locality_info']
                            if loc is not None:
                                if 'locality' in loc and loc['locality'] is not None:
                                    url = self.weather_url_config(loc['locality'])

                                    wt_data = self._make_request(url, exc_ids=req_uuid, 
                                        locality=loc['locality'])
                                    if not 'errorMsg' in wt_data:
                                        id = self._create_weather_record(**{
                                                "req_uuid":req_uuid,
                                                "weather_record":wt_data
                                            })
                                    else:
                                        pass
                                    del wt_data, url, loc

                                elif 'country' in loc and loc['country'] is not None:
                                    url = self.weather_url_config(loc['country'])

                                    wt_data = self._make_request(url, exc_ids=req_uuid, 
                                        locality=loc['country'])
                                    if not 'errorMsg' in wt_data:
                                        id = self._create_weather_record(**{
                                                "req_uuid":req_uuid,
                                                "weather_record":wt_data
                                            })
                                    else:
                                        pass
                                    del wt_data, url, loc

                            return {
                                    "action":"POST",
                                    "status":201,
                                    "data":
                                    {
                                        "req_uuid":str(req_uuid)
                                    }
                                }
                    else:
                         {
                            "action":"POST",
                            "errorMsg":"insert_one failed or and item not inserted",
                            "status":400
                        }               
    # [END create a new collection of requests]


    # [START create many collection of requests]
    def create_many_requests(self, **args):
        f_id = self.__get_secure_id(args['uuid'])

        if f_id == None:
            return {
                "action":"POST",
                "status":404,
                "errorMsg":"uuid not exist"
            }

        else:
            f_info = self._find_family_by_id(f_id)

            if f_info == None:
                return {
                    "action":"POST",
                    "inner_action":"CHECK",
                    "status":404,
                    "errorMsg":"uuid does not match with family's id"
                }

            elif f_info['family_name'] != args['family_name']:
                return {
                    "action":"POST",
                    "status":400,
                    "errorMsg":"uuid doesn't match with the family name"
                }

            else:
                requests = args['requests']     ## list of request
                r_ids = []
                items = []
                
                ##  'for' number of requests register together
                for req in requests:
                    req['created_at'] = api.get_unix_from_datetime(api.get_current_time())
                    req['req_uuid'] = api.uuid_generator_4()
                    r_ids.append(req['req_uuid'])
                    items.append(req['item'])

                    ## @Note, system will think 'receivers' is already in 'req'
                    ## also system will not regard value of comments, acceptors as
                    ## those are not generally filled when the request is created
                    req['comments'] = []
                    req['acceptors'] = []
                    req['sender'] = args['sender']
                    req['owner'] = f_info['family_name']



                    if 'optional_data' in req:
                        opt_data = req['optional_data']
                        req['optional_data'] = None         # this variable not needed anymore

                        #   if images exist in a request, store them also separately 
                        if 'images' in opt_data:
                            loimages = self.meta.store_metadata_image(
                                f_info['family_name'], opt_data['images'])

                            #   write image file in the server storage (NOTE!, this is not the database storage)
                            api.write_image_file(loimages)

                            req['images'] = None if not 'images' in opt_data else map(lambda x:x['id'], loimages)

                        req['time_of_need'] = None if not 'time_of_need' in opt_data else opt_data['time_of_need']
                        req['urgency'] = 0 if not 'urgency' in opt_data else opt_data['urgency']
                        req['location'] = None if not 'location' in opt_data else opt_data['location']
                        req['description'] = None if not 'description' in opt_data else opt_data['description']
                        req['price'] = None if not 'price' in opt_data else opt_data['price']
                
                n_ids = self.db.requests.insert_many(requests, ordered=True).inserted_ids
                
                ids = []
                for c in range(len(n_ids)):
                    ids.append(
                        {
                            "req_id":n_ids[c]
                        })

                res = self._register_many_requests(ids, f_id)

                if 'errorMsg' in res:
                    return res

                ## everything is ok
                else:
                    ids = []
                    resp = []

                    for c in range(len(r_ids)):
                        ids.append({
                                "uuid":r_ids[c],
                                "secret":n_ids[c]
                                })
                        resp.append({
                                "req_uuid":str(r_ids[c]),
                                "item":items[c]
                            })
                    del c
                    self._key_mapper(ids)
                    del ids #ids[:]

                    tks = self._find_google_token_by_uid(req['receivers'])

                    """if tks is not None:
                        ## send gcm messages to receivers
                        self._make_gcm_request(tks, data={
                                "status":201,
                                "method":"POST",
                                "target":"requests"
                            })"""
                  
                    ## fetch and store weather data if possible
                    loc = args['locality_info']
                    if loc is not None:
                        if 'locality' in loc and loc['locality'] is not None:
                            url = self.weather_url_config(loc['locality'])

                            wt_data = self._make_request(url, exc_ids=r_ids, 
                                locality=loc['locality'])
                            if not 'errorMsg' in wt_data:
                                id = self._create_weather_record(**{
                                        "req_uuid":r_ids,
                                        "weather_record":wt_data
                                    })
                                r = self.db.weatherRecord.find_one({"_id":api._id(id)})
                            else:
                                pass

                        #########################################################################
                        ## this may significantly inaccurate than using 'locality' in weather status 
                        elif 'country' in loc and loc['country'] is not None:
                            url = self.weather_url_config(loc['country'])

                            wt_data = self._make_request(url, exc_ids=r_ids, 
                                locality=loc['country'])
                            if not 'errorMsg' in wt_data:
                                self._create_weather_record(**{
                                        "req_uuid":r_ids,
                                        "weather_record":wt_data
                                    })

                            else:
                                pass
                        del wt_data
                        #########################################################################
                    del loc
                    return resp


    # [END create many collection of requests]


    # [START find all families]
    def find_all_families(self):
        return map(lambda f:{
                "family_name":f['family_name']
            }, self.db.family.find())
    # [END find all families]


    # [START find all requests]
    def find_all_requests(self, uuid):
        f_id = self.__get_secure_id(uuid)
        logger.info(f_id)

        if f_id != None:
            f_info = self._find_family_by_id(f_id)

            return map(lambda r:{
                    "created_at":r['created_at'],
                    "req_uuid":r['req_uuid'],
                    "owner":r['owner'],
                    "item":r['item'],
                    "images":r['images'],
                    "sender":r['sender'],
                    "time_of_need":r['time_of_need'],
                    "urgency":r['urgency'],
                    "location":r['location'],
                    "price":r['price'],
                    "description":r['description'],
                    "acceptors":r['acceptors'],
                    "comments":r['comments'],
                    "receivers":r['receivers']
                }, self.db.requests.find(
                {
                    "owner":f_info['family_name']
                }))

        else:
            return {
                "action":"GET",
                "status":404,
                "errorMsg":"uuid not exist",
                "help":"this call requires family id. If you have one already, "+
                "you may want to try /family/<string:uuid>/request"
            }
    # [END find all requests]


    # [START find all members in the family]
    def find_all_members(self, arg):
        ## checking if arg is family_name or uuid

        _arg = api._uuid(arg)
        if _arg is None:
            return map(lambda m:{
                "user_name":m['user_name'],
                "created_at":m['created_at'],
                "user_name":m['user_name'],
                "family_name":m['family_name'],
                "mac_addr":m['mac_addr'],
                "google_token":m['google_token'],
                "uid":str(m['uid'])
            }, self.db.users.find(
                {
                    "family_name":arg       
                }))   

        else:
            f_id = self.__get_secure_id(_arg)    ## uuid
            f_info = self._find_family_by_id(f_id)

            if f_id == None or f_info == None:
                return {
                    "action":"GET",
                    "status":404,
                    "inner_action":"FIND",
                    "errorMsg":"uuid not exist"
                }

            else:
                return map(lambda m:{
                "user_name":m['user_name'],
                "created_at":m['created_at'],
                "user_name":m['user_name'],
                "family_name":m['family_name'],
                "mac_addr":m['mac_addr'],
                "google_token":m['google_token'],
                "uid":str(m['uid'])
            }, self.db.users.find(
                    {
                        "family_name":f_info['family_name']   
                    }))           
    # [END find all members in the family]


    # [START find family info by uuid]
    def find_family_by_uuid(self, uuid):
        uuid = api._uuid(uuid)

        if uuid is None:
            return {
                "action":"GET",
                "status":400,
                "errorMsg":"given uuid is not instance of uuid",
                "help":"this call requires family id. If you have one already, "+
                "try /family/""<string:uuid>"" to achieve result what you may wished"
            }

        else:
            id = self.__get_secure_id(uuid)

            if id != None:
                return self._find_family_by_id(id)

            else:
                return None
    # [END find family info by uuid]


    # [START find family cart by uuid]
    def find_cart_by_uuid(self, uuid):
        f_id = self.__get_secure_id(api._uuid(uuid))

        if f_id != None:
            c_info = self._find_cart_by_id(self._find_family_by_id(f_id)['cart_id'])

            return {
                "action":"FIND",
                "status":200,
                "data":
                {
                    "created_at":c_info['created_at'],
                    "owner":c_info['owner']
                }
            }

        else:
            return {
                "action":"FIND",
                "status":404,
                "errorMsg":"uuid not exist"
            }

    # [END find family cart by uuid]


    # [START find user info]
    def find_user_by_id(self, id):
        return self.db.users.find_one(_id(id))
    # [END find user info]


    # [START find user info by uid]
    def find_user_by_uid(self, uid):
        id = self.__get_secure_id(uid)
        if id != None:
            return self.find_user_by_id(id)
        else:
            return None
    # [END find user info by uid]


    # [START find all requests]
    def find_one_request(self, f_name, req_uuid):
        req_id = self.__get_secure_id(req_uuid)

        if req_id == None:
            return {
                "action":"GET",
                "status":404,
                "errorMsg":"request id not exists"
            }

        else:
            res = self.db.requests.find_one({
                    "_id":api._id(req_id)
                })
            #logger.info(res)

            if res != None:
                ## everything is ok
                if res['owner'] == f_name:
                    return res

                else:
                    return {
                        "action":"GET",
                        "status":400,
                        "errorMsg":"given family name does not match with request id"
                    }
            else:
                return {
                    "action":"GET",
                    "status":404,
                    "errorMsg":"request not exists"
                }
    # [END find all requests]


    # [START remove request]
    def remove_request(self, f_name, req_uuid):
        req_id = self.__get_secure_id(req_uuid)

        if req_id == None:
            return {
                "action":"DELETE",
                "inner_action":"FIND",
                "status":404,
                "errorMsg":"requst id does not exist"
            }

        else:
            r_info = self.db.requests.find_one({
                    "_id":api._id(req_id)
                })

            # authentication meets
            if r_info['owner'] == f_name:
                res = self._remove_doc_ele("_id",
                    "requests",
                    req_id)

                if 'errorMsg' in res:
                    return res

                else:
                    logger.info(res)
                    res = self._remove_request_from_family(r_info['owner'], 
                        req_id)

                    ## move the request to the history for further study
                    self._move_request_to_history(**r_info)

                    return res
            else:
                return {
                    "action":"DELETE",
                    "inner_action":"CHECK",
                    "status":400,
                    "errorMsg":"given request id does not match with family name"
                }
    # [END remove request]


    # [START leave family]
    def unregister_from_family(self, f_name, uid):
        ## @Note, uid = user's uuid, userid = user's ObjectId
        userid = self.__get_secure_id(api._uuid(uid))    

        if userid == None:
            return {
                "action":"DELETE",
                "inner_action":"FIND",
                "status":404,
                "errorMsg":"user id not found"
            }

        else:
            f_info = self._find_family_by_userid(userid)
            u_info = self.find_user_by_uid(uid)
            logger.info(userid)
            logger.info(f_name)
            logger.info(f_info)
            logger.info(u_info)

            if u_info != None:
                ## check if family name in url matches with family name of given uid
                if f_info != None and f_info['family_name'] == f_name:

                    try:
                        r_res = self._remove_user_from_requests(u_info['uid'])
                        u_f_res = self._remove_user_from_family(f_info['family_name'], 
                            userid)

                        ## key name of id for conidtion, doc name, value
                        u_res = self._remove_doc_ele("_id", 
                            "users", 
                            userid)
                        s_res = self._remove_doc_ele("secret", 
                            "secret", 
                            userid)

                        f_info = self._find_family_by_name(f_name)
                        
                        if self._check_family_has_member(f_info['_id']) == False:
                            f_res = self._remove_doc_ele("_id", 
                                "family", 
                                f_info['_id'])
                            f_res['inner_action'] = {"inner_action":"CHECK"}

                        else:
                            f_res = {
                                "action":"DELETE",
                                "inner_action":"CHECK",
                                "status":"OK",
                                "member_count":len(f_info['members'])
                            }

                        return {
                                "res_col":[u_f_res, 
                                r_res, u_res, s_res, 
                                f_res]
                            }
                    except Exception:
                        return {
                            "action":"DELETE",
                            "status":500,
                            "errorMsg":"error risen while removing user " +
                            "from requests, family, secret, users"
                        }

                else:
                    return {
                        "action":"DELETE",
                        "inner_action":"CHECK",
                        "status":400,
                        "errorMsg":"wrong family name"
                    }
            else:
                return {
                    "action":"DELETE",
                    "inner_action":"CHECK",
                    "status":404,
                    "errorMsg":"uid not exists"
                }
    # [END leave family]


    # [START update family member]
    def update_family_member(self, **args):
        if self._check_user_exist(args['mac_addr']):
            return False

        elif not self._check_family_name_exist(args['family_name']):
            return False

        else:
            f_info = self._find_family_by_name(args['family_name'])
            logger.info(f_info)

            if api._uuid(args['uuid']) != f_info['uuid']:
                return {
                    "action":"POST",        # PUT used /family/family_name is deprecated 
                    "inner_action":"CHECK",
                    "errorMsg":"family id not matching with given name",
                    "status":400
                }

            else:
                _args = {
                            "user_name":args['user_name'],
                            "family_name":args['family_name'],
                            "mac_addr":args['mac_addr'],
                            "google_token":args['google_token']
                        }
                res = self._create_user(**_args)

                if not api.is_id(res):
                    return res
                if not isinstance(res, ObjectId):
                    return res

                else:
                    u_info = self.find_user_by_id(res)
                    logger.info(u_info)
                    res = self.db.family.update_one(
                    {
                        "_id":api._id(f_info['_id'])
                    },
                    {
                        "$push":
                        {
                            "members":
                            {
                                "user_id":res   ## user id
                            }   
                        }
                    })

                logger.info(res.modified_count)
                logger.info(res.matched_count)

                return {
                    "uuid":f_info['uuid'],
                    "uid":u_info['uid']
                } if res.modified_count == 1 and res.matched_count == 1 else False
        
    # [END update family member]


    # [START update requests]
    def update_requests_info(self, **args):
        if not self._check_family_name_exist(args['family_name']):
            return {
                "action":"PUT",
                "inner_action":"CHECK",
                "status":404,
                "errorMsg":"family name not exists"
            }

        else:
            f_id = self.__get_secure_id(args['uuid'])
            f_info = self._find_family_by_id(f_id)

            ## check if given uuid is valid 
            if f_id == None or f_info == None:
                return {
                    "action":"PUT",
                    "inner_action":"FIND",
                    "status":404,
                    "errorMsg":"family id not exists"
                }

            ## check if given family name and found family name by given uuid matches 
            elif f_info['family_name'] != args['family_name']:
                return {
                    "action":"PUT",
                    "inner_action":"CHECK",
                    "status":400,
                    "errorMsg":"family id and family name does not match"                    
                }

            else:
                res = self.find_one_request(f_info['family_name'], args['req_uuid'])

                if 'errorMsg' in res:
                    res['inner_action'] = res['action']
                    res['action'] = "UPDATE"
                    return res

                ## update any items arrived along with
                elif args['data_to_update'] is not None:
                    n_data = args['data_to_update']

                    ## sort keys that need to be updated
                    keys_to_update = list(n_ele for n_ele in n_data if n_ele in res)
                    data_to_update = {}

                    for key in res:
                        if key in keys_to_update:
                            data_to_update[key] = n_data[key]
                        else:
                            data_to_update[key] = res[key]

                    logger.info(data_to_update)

                    ## when update acceptors it should be type of dict, NOT LIST!!
                    ## if a new acceptor has added, system will inform sender 
                    resp = self._update_one_requests(data_to_update)
                    if not 'errorMsg' in resp and 'acceptors' in keys_to_update:
                        gt = self._find_google_token_by_uid(res['sender'])   # {"sender":{"uid":"senrder_uid"}}

                        if gt is not None:
                            self._make_gcm_request(gt, data={"default":"A_new_acceptor"})

                    return resp 

                ## delete this uid from acccepters
                elif args['uid'] is not None:
                    data = {}
                    data['_id'] = res['_id']
                    data['uid'] = args['uid']
                    return self._remove_user_from_acceptors(data)

                else:
                    return {
                        "status":400,
                        "action":"PUT",
                        "errorMsg":"missing data to update"
                    }
                    

    def _remove_user_from_acceptors(self, data):
        res = self.db.requests.update_one(
            {
                "_id":api._id(data['_id'])
            },
            {
                 "$pull":
                {
                    "acceptors":
                    {
                        "uid":data['uid']
                    }
                }               
            })

        return {
            "action":"PUT",
            "status":200,
            "target":"requests.acceptors",

        } if res.modified_count == 1 and res.matched_count == 1 else {
            "action":"PUT",
            "status":400,
            "target":"requests.acceptors",
            "errorMsg":"google_token was not found in acceptors",
        }


    def _update_one_requests(self, n_data):
        ## bracket needs to be controled accordingly to $each syntax
        logger.info(n_data)
        if type(n_data['receivers']) == list and not None:
            receivers = n_data['receivers']
        elif n_data['receivers'] is None:
            receivers = None
        else:
            receivers = [n_data['receivers']]

        if type(n_data['acceptors']) == list and not None:
            acceptors = n_data['acceptors']
        elif n_data['acceptors'] is None:
            acceptors = None
        else:
            acceptors = [n_data['acceptors']]


        if type(n_data['comments']) == list and not None:
            comments = n_data['comments']
        elif n_data['comments'] is None:
            comments = None
        else:
            comments = [n_data['comments']]


        res = self.db.requests.update(
            {
                "_id":api._id(n_data['_id'])
            },
            {
                "$set":
                { 
                    "time_of_need":n_data['time_of_need'],
                    "urgency":n_data['urgency'],
                    "description":n_data['description'],
                    "time_of_need":n_data['time_of_need'],
                    "location":n_data['location'],
                    "price":n_data['price']
                },
                "$addToSet":
                {
                    "receivers":
                    {
                        "$each":receivers
                    },
                    "acceptors":
                    {
                        "$each":acceptors
                    },
                    "comments":
                    {
                        "$each":comments
                    }
                }
                
            })

        if res['n'] == 0:
            return {
                "status":404,
                "errorMsg":"request id not found",
                "action":"PUT",
                "target":"requests",
            }

        elif res['n'] > 0 and res['nModified'] > 0:
            return {
                "status":200,
                "action":"PUT",
                "target":"requests",
            }

        else:
            return {
                "status":200,
                "errorMsg":"found item but not mofidied as probably "+
                "items values were same",
                "action":"PUT",
                "target":"requests",
            }

    # [END update requests]


    # [START private functions]
    ## move the about-to-delete item to the history 
    def _move_request_to_history(self, **req):
        logger.info(req)
        return self.db.requestHistory.insert_one(req).inserted_id


    ## check if family is empty
    def _check_family_has_member(self, id):
        res = self.db.family.find_one(
            {
                "_id":api._id(id)
            })
        logger.info(res)
        logger.info(len(res['members']))

        return True if len(res['members'])>0 else False


    ## check if family name exists
    def _check_family_name_exist(self, f_name):
        return True if self.db.family.find_one(
            {
                "family_name":f_name
            }) != None else False


    ## check if family name exists
    def _check_request_exist(self, id):
        return True if self.db.requests.find_one(
            {
                "_id":api._id(id)
            }) != None else None


    ## user cannot be taken part of more than one family group thus, if user exists,
    ## this user should not be considered to join any other family group
    def _check_user_exist(self, mac_addr):
        return True if self.db.users.find_one(
            {
                "mac_addr":mac_addr
            }) != None else False


    ## create a new weather record
    def _create_weather_record(self, **args):
        if not isinstance(args, list):
            ids = [args['req_uuid']]
        else:
            ids = args['req_uuid']

        new_w_r = self.db.weatherRecord.insert_one(
            {   
                "req_uuid":ids,
                "created_at":api.get_unix_from_datetime(api.get_current_time()),
                "weather_record":args['weather_record']
            })
        return new_w_r.inserted_id


    ## create a new user
    def _create_user(self, **args):
        if self._check_family_name_exist(args['family_name']):
            uid = api.uuid_generator_1()

            new_u = self.db.users.insert_one(
            {
                "created_at":api.get_unix_from_datetime(api.get_current_time()),
                "user_name":args['user_name'],
                "family_name":args['family_name'],
                "mac_addr":args['mac_addr'],
                "google_token":args['google_token'],
                "uid":uid
            })

            self._key_mapper({"secret":new_u.inserted_id, "uuid":uid})
            return new_u.inserted_id

        else:
            return {
                "inner_action":"CHECK",
                "action":"CREATE",
                "errorMsg":"family name not exist",
                "status":400
            }


    ## find family info
    def _find_family_by_id(self, id):
        return self.db.family.find_one(
            {
                "_id":api._id(id)
            })


    ## find family info by family name 
    def _find_family_by_name(self, f_name):
        return self.db.family.find_one(
            {
                "family_name":f_name
            })


    ## find family info by uid
    def _find_family_by_uid(self, uid):
        u_id = self.__get_secure_id(uid)

        if u_id == None:
            return None
        else:
            return self.db.family.find_one(
                {
                    "members":
                    {
                        "user_id":api._id(u_id)
                    }
                })


    ## find family info by userid
    def _find_family_by_userid(self, id):
        return self.db.family.find_one(
            {
                "members":
                {
                    "$in":[
                    {
                        "user_id":api._id(id)
                    }]
                }
            })
    

    ## find google token from user with given uid
    def _find_google_token_by_uid(self, uids):
        if not isinstance(uids, list):
            uids = [uids]

        uids = list({"uid":api._uuid(uids[idx]['uid'])} for idx,dic in enumerate(uids) if 'uid' in dic)
        # check if there is None value in uids
        if not any(uids[idx]['uid'] is None for idx,dic in enumerate(uids)):
            logger.info(uids)

            cur = self.db.users.find(
                {
                    "$or":uids
                })

            if cur.count()>0:
                tks = list(tk['google_token'] for tk in cur)
                logger.info(tks)
                return tks
            else:
                return None
        else:
            return None


    ## find user info
    def _find_user_by_mac_addr(self, mac_addr):
        return self.db.users.find_one(
            {
                "mac_addr":mac_addr
            })


    ## check time for making request for weather data
    ## true if system has the record of making request within pre-defined mins
    ## false if system has not
    def _check_timeframe(self, exc_ids):
        now = api.get_unix_from_datetime(api.get_current_time())

        if not isinstance(exc_ids, list):
            exc_ids = [exc_ids]

        # not necessarily check if ids are corrupted
        # as they are genearted by server
        exc_ids = list(api._uuid(exc_ids[idx]) for idx, dic in enumerate(exc_ids))

        res = self.db.requests.find_one(
            {   
                "$and":[
                {
                    "created_at":
                    {
                        "$gt":now-self.timeframe_allows_requests
                    },
                    "req_uuid":
                    {
                        "$nin":exc_ids
                    }
                }]
            })
        logger.info(res)
        if res is None:
            del res
            res = self.db.requestHistory.find_one(
                {
                    "$and":[
                    {
                        "created_at":
                        {
                            ## check if there was a request call within last pre-defined(recommended 10 mins) mins
                            "$gt":now-self.timeframe_allows_requests
                        },
                        "req_uuid":
                        {
                            "$nin":exc_ids
                        }
                    }]
                })

            if res is None:
                return False

            elif res is not None:
                return True

        elif res is not None:
            del res, now
            return True


    ## make request to the weather center
    ## exc_ids: array of req_uuid to ignore when checking timeframe
    ##          for weather request 
    def _make_request(self, url, is_json=True, session=None, exc_ids=None, locality="Oulu"):
        """
        Makes a HTTP request to open weather data servers with the constructed payload

        :param data: return value from construct_payload method
        :param session: requests.Session object to use for request (optional)
        """
        cached = cache.get(locality.lower())

        if not self._check_timeframe(exc_ids) or cached is None:
            print "request for weather data has been made"
            headers = {
                'Authorization': 'key=%s' % self.weather_api_key,
            }

            if is_json:
                headers['Content-Type'] = 'application/json'
            else:
                headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'

            new_session = None
            if not session:
                session = new_session = requests.Session()
            
            try:
                response = session.get(url, 
                    verify='C:/Users/haejong/Documents/ms_server/certfile.txt')
            finally:
                if new_session:
                    new_session.close()

            logger.info(response.status_code)
            logger.info(response.reason)
            logger.info(response.headers)
            logger.info(response.text)

            # 5xx or 200 + error:Unavailable
            self.retry_after = api._get_retry_after(response.headers)

            # Successful response
            if response.status_code == 200:
                if is_json:
                    response = response.json()
                else:
                    response = response.content
                return response

            ## caches weather info 
            cache.set(locality.lower(), response, timeout=None)
            return response
        
        else:
            print "using cache data for weather info"
            print cached
            return cached


    ## make gcm request
    ## token must be list
    def _make_gcm_request(self, tks, data={"default":"data"}):
        gcm = GCM(self.gcm_api_key)

        response = gcm.json_request(registration_ids=tks, data=data)
        logger.info(response)
        if 'success' in response:
            pass
        else:
            pass       


    ## delete user by id
    def _remove_doc_ele(self, key, doc, value):
        res = self.db[doc].remove(
            {  
                key:api._id(value)
            },
            {
                "justOne":True
            })
        logger.info(res)

        #if res.hasWriteError():
        #    return False

        if 'WriteError' in res:
            return {
                    "status":"error",
                    "code":res['writeError'].code,
                    "errorMsg":res['writeError'].errmsg,
                    "action":"DELETE",
                    "target":doc
                }
        elif res['n'] == 0:
            return {
                "status":404,
                "errorMsg":"user not found",
                "action":"DELETE",
                "target":doc
            }
        elif res['n'] > 0:
            return {
                "status":200,
                "action":"DELETE",
                "target":doc
            }
        else:
            return {
                "status":200,
                "errorMsg":"found item but not mofidied",
                "action":"DELETE",
                "target":doc
            }


    ## register a new request
    def _register_new_request(self, r_id, f_id):
        res = self.db.family.update_one(
            {
                "_id":api._id(f_id)
            },
            {
                "$push":
                {
                    "requests":
                    {
                        "req_id":api._id(r_id)
                    }
                }
            })

        return {
            "action":"POST",
            "status":201,
            "target":"family.requests",
            "inner_action":"UPDATE"

        } if res.modified_count == 1 and res.matched_count == 1 else {
            "action":"POST",
            "status":400,
            "target":"family.requests",
            "errorMsg":"user not found or failed $push",
            "inner_action":"UPDATE"
        }


    ## register many requests to the family collection
    def _register_many_requests(self, req_ids, f_id):
        res = self.db.family.update_many(
            {
                "_id":api._id(f_id)
            },
            {
                "$push":
                {
                    "requests":
                    {
                        "$each":req_ids
                    }
                }
            })

        logger.info(res.modified_count)
        logger.info(res.matched_count)
        return {
            "action":"POST",
            "status":201,
            "target":"family.requests",
            "inner_action":"UPDATE"

        } if res.modified_count == 1 and res.matched_count == 1 else {
            "action":"POST",
            "status":400,
            "target":"family.requests",
            "errorMsg":"user not found or failed $push",
            "inner_action":"UPDATE"
        }


    ## remove request from family members
    def _remove_request_from_family(self, f_name, r_id):
        res = self.db.family.update_one(
            {
                "family_name":f_name
            },
            {
                "$pull":
                {
                    "requests":
                    {
                        "req_id":api._id(r_id)
                    }
                }
            })
        logger.info(res.modified_count)
        logger.info(res.matched_count)

        return {
            "action":"DELETE",
            "status":200,
            "target":"family.requests",
            "inner_action":"UPDATE"

        } if res.modified_count == 1 and res.matched_count == 1 else {
            "action":"DELETE",
            "status":400,
            "target":"family.requests",
            "errorMsg":"request not found or failed $pull",
            "inner_action":"UPDATE"
        }

    ## remove user from family members
    def _remove_user_from_family(self, f_name, u_id):
        res = self.db.family.update_one(
            {  
                "family_name":f_name
            },
            {
                "$pull":
                {
                    "members":
                    {
                        "user_id":api._id(u_id)
                    }
                }
            })

        return {
            "action":"DELETE",
            "status":200,
            "target":"family.members",
            "inner_action":"UPDATE"

        } if res.modified_count == 1 and res.matched_count == 1 else {
            "action":"DELETE",
            "status":400,
            "target":"family.members",
            "errorMsg":"user not found or failed $pull",
            "inner_action":"UPDATE"
        }


    ## remove user from request collection
    def _remove_user_from_requests(self, uid):
        ## @Note!, uids in requests are stored as str
        ## TODO: handle uid as instance of UUID
        res = self.db.requests.update(
            {
                "$or":[
                {
                    "receivers":
                    {
                        "uid":str(uid)
                    }
                },
                {
                    "acceptors":
                    {
                        "uid":str(uid)
                    }
                }]
            },
            {
                "$pull":
                {

                    "receivers":
                    {
                        "uid":str(uid)
                    },
                    "acceptors":
                    {
                        "uid":str(uid)
                    }
                }
            
            }, multi=True)
        logger.info(res)
        
        if 'WriteError' in res:
            return {
                "status":"error",
                "code":res['writeError'].code,
                "errorMsg":res['writeError'].errmsg,
                "action":"DELETE",
                "target":"requests",
                "inner_action":"UPDATE"
                }

        elif res['n'] == 0:
            return {
                "status":404,
                "errorMsg":"uid is not found",
                "action":"DELETE",
                "target":"requests",
                "inner_action":"UPDATE"
            }

        elif res['n'] > 0 and res['nModified'] > 0:
            return {
                "status":200,
                "action":"DELETE",
                "target":"requests",
                "inner_action":"UPDATE"
            }

        else:
            return {
                "status":200,
                "errorMsg":"found item but not mofidied",
                "action":"DELETE",
                "target":"requests",
                "inner_action":"UPDATE"
            }


    # [START secure manager]
    ## identifying collections by objectid would speed up the use of db methods than using
    ## uuid as a id value thus here we map uuids to internally coupled objectids
    ## also this considers less of security issue by sending out ids to the wild

    # http://stackoverflow.com/questions/5949/whats-your-opinion-on-using-uuids-as-database-row-identifiers-particularly-in 
    def _key_mapper(self, obj):
        if type(obj) is not list: 
            res = self.db.secret.insert_one(
                {
                    "secret":obj['secret'],
                    "uuid":obj['uuid'] 
                })
            return res.inserted_id

        else:
            res = self.db.secret.insert_many(obj, ordered=True)   ## multiple key pairs
            return res.inserted_ids
    # [END secure manager]


    def _convert_id_to_humanreadable(self, f_name, uuid):
        rid = api.random_id_generator(5)    # len = 5
        nid = f_name+rid
        logger.info(nid)
        res = self.db.readableId.insert_one(
            {
                "uuid":api._uuid(uuid),
                "readable_id":nid
            })
        return nid


    # [START get secure id]
    def __get_secure_id(self, uuid):
        uuid = api._uuid(uuid)

        if uuid is None:
            return None

        else:
            res = self.db.secret.find_one(
                {
                    # @Note, this will turn str uuid into obj uuid
                    "uuid":uuid
                })
            return res['secret'] if res != None else None
    # [END get secure id]
    # [END private functions]

