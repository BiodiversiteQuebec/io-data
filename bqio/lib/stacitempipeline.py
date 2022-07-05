# pip install python-decouple

import pystac
from datetime import datetime
import traceback
import sys
import uuid
import logging
sys.path.append('/bqio/')
from lib.pipelinelib import StacItem
from threading import  Lock


class StacLog:

	
	def __init__(self,  param = {"uuid":0}):
		self._id = param["uuid"]
		self._operation:str =""
		self._param = param
		self._status:str = "ok"
		self._description:str = ""
		pass


class ItemsPipeline:

	def __init__(self):
		self.params_list = []
		self.isRunning = False
		self.logs = []
		self.deleted_logs = []
		self.current_item_index = 0
		self.lock = Lock()
		logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
		pass

	# 
	def add_item_to_collection(self,params):
		params["uuid"] = str(uuid.uuid4())
		self.params_list.append(params)
		log = StacLog(params)
		log._operation = "**pending**"
		self.logs.append(log)
		response = {
			"id":params["uuid"],
			"msg":"received"
		}
		return response	

	# uses pystac to retreive the collection by using the given id
	def get_collection_by_id(self,params, operation_log):
		
		try:
			operation_log._operation = "GETCOLLECTION"
			operation_log._status = "ok"
			collection_id = params["collection_id"]
			stac_host_server = params["stac_api_server"]
			#collection = pystac.read_file(f'https://io.biodiversite-quebec.ca/stac/collections/{collection_id}')	
			collection = pystac.read_file(f'{stac_host_server}/collections/{collection_id}')	
			operation_log._description += f' \n Collection: "{collection_id}" retrevided succefuly from server.'	
			logging.debug(operation_log._description)
			return collection
		except Exception as err:
			operation_log._description = f'Unable to read collection: "{collection_id}" from server, error \n: {err}. \n Please check your conexion or congif.'	
			operation_log._status = "error"
			logging.debug(operation_log._description)
			return None

    # returns StacItem object from params
	# StacItem object: contains the info needed to create a pystac item
	def create_item(self, params):

		name:str = params["name"]
		filename:str = params["filename"]
		date:str = params['date']
		properties = params["properties"]
		uri =  f'{params["file_source_host"]}/{filename}'
		
		item:StacItem = StacItem(name, filename, datetime.fromisoformat(date), properties, uri, "raw", True, False)
		return item

	def run(self):
		self.isRunning = True
		self.process()
    
	def process(self):
		
		logging.debug("****process started*****")
		while self.isRunning == True:
			
			if len(self.params_list) > self.current_item_index:
                  
				param = self.params_list[self.current_item_index]
				log = self.logs[self.current_item_index]
				logging.debug(f'processing item: {param["uuid"]}')
				
				#avoid race condition over current_item_index variable
				self.lock.acquire()
				if self.current_item_index < len(self.params_list):
					self.current_item_index += 1
				self.lock.release()
				
				file_source_host = param["file_source_host"]
				stac_host_server = param["stac_api_server"]
				collection_folder = param["collection_id"]

				# retreive collection by id
				collection = self.get_collection_by_id(param, log)
				item = None

				if collection is not None:
					# create  StacItem from param
					item  = self.create_item(param)
						
					# get item file from source
					self.get_item_file(item, log)

					# transform file to COG
					self.transform_COG(item, log)
					
					# create pystac 
					self.create_pystac_item(item, collection, file_source_host, log)

					# sending item to api server
					self.push_to_api(item, stac_host_server)

					# upload the cog file to backup server (ex: S3)
					self.upload_COG_to_server(item, collection_folder, log)

					# removing temporal files
					self.delete_item_file(item, log)

					#
				
				self.finish_process(item, log)

				# print
				# print(self.logs[0].__dict__)
				# self.deleted_logs.append(log)
		
					#del self.params_list[0]
					#del self.logs[0]		

	# create Pystac Item from StacItem					
	def create_pystac_item(self, item, collection, host, log):
       
		if item.status()._ok:
			"""create pystac""" 
			log._operation = "CREATEPYSTACITEM"
			item.createPystacItem(collection, host)
			self.update_log(log, item)

	def delete_item_file(self, item, log):
		if item.status()._ok:
			"""delete item file from source"""
			log._operation = "DELETEITEMFILE"
			item.deleteItemFile()
			self.update_log(log, item)

	def finish_process(self,item, log):
			
			if item is not None: 	
				log._operation = "PROCESS FINISHED" if item.status()._ok else log._operation 
				log._status = "ok" if item.status()._ok else "error" 
			else:
				log._status = "error" 

			logging.debug(f"*****PROCESS {log._id}********")
			logging.debug(f'Status: {log._status}')
			logging.debug(f'Operation:{log._operation}')
			logging.debug(f'Description: {log._description}')

	def get_item_file(self, item, log):
		"""get item file from source"""
		log._operation = "GETITEMFILE"
		if item.status()._ok:
			item.getItemFile()
		self.update_log(log, item)

	def transform_COG(self, item, log):
		if item.status()._ok:
			""" transform file to COG"""
			log._operation = "TRANF_COG"
			item.transformToCog()
			self.update_log(log, item)
		
	def update_log(self, log, item):
		"""update current log info"""
		if item is not None: 
			log._description += f' \n {item.status()._message}'	
			log._status = "ok" if item.status()._ok else "error" 

	def setPushItemToApiFn(self, fn):
		""" set function used to push items """
		self.push_to_api_fn = fn

	def setPushCOGToServerFn(self, fn):
		self.push_COG_to_server_fn = fn

	def push_to_api(self, item, stac_host_server:str):
		""" push item to api server"""
		if self.push_to_api_fn is not None:
			self.push_to_api_fn(item.getItem(), stac_host_server)		
 
	def upload_COG_to_server(self, item, collection_folder:str, log=None ):
		""" upload COG file to a server"""
		if item.status()._ok:
			status = self.push_COG_to_server_fn(item, collection_folder)
			if log is not None:
				""" transform file to COG"""
				log._operation = "UPLOAD_COG_TO_SERVER"
				log._status = "ok" if status._ok else "error"
				log._description += f' \n {status._message}'

	def get_log_by_id(self, id):
		filtered = list(filter(lambda log: log._id == id, self.logs ))
		return filtered[0] if len(filtered) > 0 else {}

	def getlogs(self):
		return [ log.__dict__ for log in self.logs]

	def resume(self, log_id, params):

		return "ok"

	def _clear(self):
		self.lock.acquire()
		self.params_list = []
		self.logs = []
		self.deleted_logs = []

