####################################
## Readable code versus less code ##
####################################

from __future__ import division
from .api import api

import math

logger = api.__get_logger("mongo_meta")

class MongoMetaData(object):

	def __init__(self, db):
		self.db = db
		self.keywords_handler = api.KeywordsHandler()
		super(MongoMetaData, self).__init__()


	def _count_all_images(self):
		return self.db.images.find().count()


	def _count_family_images(self, f_name):
		return self.db.images.find({
				"owner":f_name
			}).count()
	
	def _get_vector_simiarity(self, text):
		docs_sorted = list()
		tokens_sorted = list()

		tokens = self.keywords_handler.tokenizer(text)
		N = self.db.keywordArchive.find().count()
		for index in self.db.keywordIndices.find({"word":{"$in":tokens}}):
			df = len(index['docs'])
			idf = math.log10(N/df)
			tokens_sorted.append({
					"word":index['word'],
					"idf":idf
				})

			for doc in index['docs']:
				##	if docs_sorted is not empty
				if docs_sorted:
					##	check elements of sorted docs 
					for d in docs_sorted:
						doc_id = str(doc['doc_id'])
						##	if the same doc exists in the list, append and move on to next word
						if doc_id in d:
							d[doc_id].append(
								{
									"weight":doc['count'],
									"word":index['word'],
									"a":idf*doc['count'],	## weighted 'idf'
									"idf":idf
								})
							break
					else:
					##	if the doc was not found until the end of iteration, then continue with this	
						docs_sorted.append({
								doc_id:[
								{
									"weight":doc['count'],
									"word":index['word'],
									"a":idf*doc['count'],
									"idf":idf								
								}]
							})
						continue
					##	and break if preceding break was hit
					#break --> this will end before 'for' reaches the end of docs_sorted
				else:
					##	if a new document is not added yet			
					docs_sorted.append({
							str(doc['doc_id']):[
							{
								"weight":doc['count'],
								"word":index['word'],
								"a":idf*doc['count'],
								"idf":idf								
							}]
						})

		#found_docs = map(lambda x:x['docs'], docs)	#	switch from cursor to list
		#found_docs = list(itertools.chain.from_iterable(found_docs))	# sorting list
		
		if not docs_sorted:
			return {
				"status":404,
				"action":"GET",
				"target":"keywordIndices"
			}

		docs_res = list()
		for index in tokens_sorted:
			for doc in docs_sorted:
				for e_doc in doc:	## e_doc ==> id of doc
					for ee_doc in doc[e_doc]:
						##	if one of queried words match with any word in a sotred doc
						if index['word'] is ee_doc['word']:
							v = index['idf']*ee_doc['a']

							for e_res in docs_res:
								if e_doc in e_res:
									e_res[e_doc].append({
											"sim_words":v,
											"word":index['word']
										})

									break
							else:
								docs_res.append(
									{
										e_doc:[{
											"sim_words":v,	#	calculate similarity
											"word":index['word']
										}]
									})
								continue

		del docs_sorted, tokens_sorted
		query_res = list()
		for doc in docs_res:
			val = 0
			for doc_id in doc:			
				for word in doc[doc_id]:
					val += word['sim_words']
				query_res.append({
						"doc_id":doc_id,
						"sim_docs":val
					})
		
		query_res = sorted(query_res, key=lambda x:x['sim_docs'], reverse=True)	# sort the list by value of similarity between docs and query phrase

		res = self.db.keywordArchive.find({
					"_id":api._id(query_res[0]['doc_id']) #list(api._id(ids['doc_id']) for ids in query_res)
				})

		return {
			"status":200,
			"action":"GET",
			"target":"keywordIndices",
			"data":map(lambda x:x['text'], res)
		}

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

	def _store_metadata_keywords(self, text):
		text = text['text']
		doc_id = self.db.keywordArchive.insert_one({
				"text":text
			}).inserted_id

		tokens = self.keywords_handler.tokenizer(text)

		res = self.db.keywordIndices.find({
				"word":{
					"$in":tokens
				}
			})

		found_docs = map(lambda x:x['word'], res)	#	docs exist in the db
		docs_list = list(set(tokens) - set(found_docs))		# list of words not stored in the db

		##	sorting words are not stored in the db with necessary information
		docs_detail = map(lambda x:{
				"word":x,
				"docs":[{
					"doc_id":doc_id,
					"count":tokens.count(x)
				}]
			}, docs_list)

		found_docs_detail = map(lambda x:{
				"word":x,
				"count":tokens.count(x)
			}, found_docs)

		## none of docs exist
		if not found_docs:
			## create new documents 
			res = self.db.keywordIndices.insert(docs_detail)

		## some docs are not existing in the database
		## match all the elements from the two lists
		## or use reduce(lambda x,y: x and y, map(lambda x2: x2 in docs_list, tokens):
		## instead of all(map(lambda v: v in a, b)
		elif not all(map(lambda d: d in docs_list, tokens)) and docs_list:

			## create new documents 
			res = self.db.keywordIndices.insert(docs_detail)

			## link to existing documents
			for doc in self.db.keywordIndices.find({"word":{"$in":found_docs}}):
				res = self.db.keywordIndices.update(
					{
						"word":doc['word']
					},
					{
						"$push":{
							"docs":{
								"doc_id":doc_id,
								"count":tokens.count(doc['word'])
							}

						}
					})

		## all words are in the db
		elif not docs_list:
			for doc in self.db.keywordIndices.find({"word":{"$in":found_docs}}):
				res = self.db.keywordIndices.update(
					{
						"word":doc['word']
					},
					{
						"$push":{
							"docs":{
								"doc_id":doc_id,
								"count":tokens.count(doc['word'])
							}

						}
					})

	def _store_metadata_requests(self, **req):
		return self.db.requestHistory.insert_one(req).inserted_id 	# move the about-to-delete item to the history 


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

