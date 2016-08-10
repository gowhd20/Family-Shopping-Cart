####################################
## Readable code versus less code ##
####################################


from .api import api

logger = api.__get_logger("mongo_meta")

class MongoMetaData(object):

    def __init__(self, db):
    	self.db = db
    	super(MongoMetaData, self).__init__()


    def count_all_images(self):
    	return self.db.images.find().count()


    def count_family_images(self, f_name):
    	return self.db.images.find({
    			"owner":f_name
    		}).count()


    ## move the about-to-delete item to the history 
    def store_metadata_requests(self, **req):
        return self.db.requestHistory.insert_one(req).inserted_id


    def store_metadata_images(self, f_name, raw_images):
		if type(raw_images) is list and not None:
			a_i_cnt = self.count_all_images()+1
			f_i_cnt = self.count_family_images(f_name)+1


################################################### Id indexing ####################################################
## "family name" - "all image count in db" - "all image count in family" - "count for images registered together" ## 

			if len(raw_images) == 1:
				new_i = self.db.images.insert_one(
					{
						"_id":f_name+"-"+str(
								self.count_all_images()+1)+"-"+str(
								self.count_family_images(f_name)+1)+"-"+str(1),	
						"owner":f_name,
					})
				return [{
					"id":new_i.inserted_id,
					"data":raw_images[0]
					}]

			else:
				ids = []
				for x in xrange(len(raw_images)):
					ids.append(
						f_name+"-"+str(a_i_cnt)+"-"+str(f_i_cnt)+"-"+str(len(raw_images)))
					## auto increment for indexing images id
					a_i_cnt+=1
					f_i_cnt+=1

				new_ids = self.db.images.insert_many(map(lambda x:{
						"_id":x,
						"owner":f_name
					}, ids), ordered=True)

				return map(lambda i, d:{
						"id":i,
						"rdata":d
					}, new_ids.inserted_ids, raw_images)

		else:
			#logger.error("Type of input image valiable is not the list")
			raise TypeError("Type of input image valiable is not the list")

