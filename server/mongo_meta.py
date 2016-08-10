####################################
## Readable code versus less code ##
####################################


from .api import api

logger = api.__get_logger("mongo_meta")

class MongoMetaData(object):

    def __init__(self, db):
    	self.db = db
    	super(MongoMetaData, self).__init__()


    def _count_all_images(self):
    	return self.db.images.find().count()


    def _count_family_images(self, f_name):
    	return self.db.images.find({
    			"owner":f_name
    		}).count()
	

	## retrive images from a request
    def _retrive_request_images(self, f_name, req_uuid):
	    res = self.db.images.find({
	            "owner":f_name,
	            "req_uuid":api._uuid(req_uuid)
	        })

	    if res != None:
	        return {
	        	"images":api.read_image_file(
	        		map(lambda x:x['_id'], list(res))),	#	res-> Cursor type
	        	"status":200,
	        	"action":"GET",
	        	"image-count":res.count()
	        }
	    else:
	    	return {
	    		"errorMsg":"matching image does not exists"
	    	}


    ## move the about-to-delete item to the history 
    def _store_metadata_requests(self, **req):
        return self.db.requestHistory.insert_one(req).inserted_id


    def _store_metadata_images(self, f_name, raw_images, req_uuid):
		if type(raw_images) is list and not None:
			icnt = len(raw_images)
			a_i_cnt = self._count_all_images()+1
			f_i_cnt = self._count_family_images(f_name)+1


################################################### Id indexing ####################################################
## "family name" - "all image count in db" - "all image count in family" - "count for images registered together" ## 

			if icnt == 1:
				new_i = self.db.images.insert_one(
					{
						"_id":f_name+"-"+str(
								self._count_all_images()+1)+"-"+str(
								self._count_family_images(f_name)+1)+"-"+str(1),	
						"owner":f_name,
						"req_uuid":req_uuid
					})
				res = [{
					"id":new_i.inserted_id,
					"data":raw_images[0]
					}]

				api.write_image_file(res)
				return map(lambda x:x['id'], res)

			else:
				ids = []
				for x in xrange(icnt):
					ids.append(
						f_name+"-"+str(a_i_cnt)+"-"+str(f_i_cnt)+"-"+str(icnt))
					## auto increment for indexing images id
					a_i_cnt+=1
					f_i_cnt+=1

				new_ids = self.db.images.insert_many(map(lambda x:{
						"_id":x,
						"owner":f_name,
						"req_uuid":req_uuid
					}, ids), ordered=True)

				res = map(lambda i, d:{
						"id":i,
						"rdata":d
					}, new_ids.inserted_ids, raw_images)

				api.write_image_file(res)
				return map(lambda x:x['id'], res) 

		else:
			#logger.error("Type of input image valiable is not the list")
			raise TypeError("Type of input image valiable is not the list")

