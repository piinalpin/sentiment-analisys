from pymongo import MongoClient

class DBModel:

	client = MongoClient()

	def insert_data(self, database, collection, documents):
		db = self.client[database]
		db[collection].drop()
		results = db[collection].insert_many(documents.to_dict('records'))

		return results.inserted_ids

	def get_data_all(self, database, collection):
		db = self.client[database]
		cursor = db[collection].find({},{"_id":0})

		return cursor

	def insert_sentimenFakultas(self, database, collection, documents):
		db = self.client[database]
		results = db[collection].insert_many(documents.to_dict('records'))

		return results.inserted_ids

	def get_hasil(self, database, collection):
		db = self.client[database]
		cursor = db[collection].find({})

		return cursor