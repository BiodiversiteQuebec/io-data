import os
import pystac
from datetime import datetime
import tempfile
from pathlib import Path
from typing import List  
import json
import traceback
import urllib.request
import sys
sys.path.append('./bqio/')
import tif2cog
import stac_item


# class to model the status 
class Status:

	_ok = True
	_message = ""

	def __init__(self,ok=True, msg=""):
		self._ok = ok
		self._message = msg

# class to model the stac catalog item
class StacItem:

	# stac item propertis
	_properties = None 

	# status of the item process with messages
	_status: Status = Status() 

	# name of the COG file that will be created
	_filename:str = None  

	# name passed to the """stac_item.stac_create_item(...,name,..)""" function
	_name:str = None 

	# the path to the file source location (it could be remote or locally)
	_file_source_location:str = None 

 	# the path where the file is created after source is downloaded 
	# in case file is retreived locally, make sure to create a Path(..._file_source_location,..) for this 
	# variable in getItemFile function since it is used to delete temporal files created 
	_tiff_local_file_location:Path = None  


    # temporal location path for the COG file generated in """transformToCog""" function, 
	# the created file could be deleted by using """deleteItemFile""" function
	_cog_local_file_location:str = None

	# datetime of the pystac item
	_datetime: datetime = None
	
	# parameter for COG transformation
	_type: str = "raw"

    # define whether to delete _tiff_local_file_location or not, 
	# user might not want to remove the file when source """_file_source_location""" is local
	_delete_tiff_local_file:bool = False

	_item = None

	def __init__(self, name, filename, datetime=None, properties=None, file_source_location = None, cog_type = "raw", deleteItemFiles=False):
		self._name = name
		self._filename = filename
		self._datetime = datetime
		self._properties = properties
		self._file_source_location = file_source_location
		self._delete_tiff_local_file = deleteItemFiles
		self._type = cog_type
		self._status._message += '\n'+ "Item name : " + name
    
	def status(self) -> Status:
		"""Returns the status of the item, it could change after an  opertation is perform"""
		return self._status

	def getItemFile(self):
		print("getting file from source at: "+ self._file_source_location)
		try:
			self._tiff_local_file_location = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
			fpath = urllib.request.urlretrieve(self._file_source_location, self._tiff_local_file_location)
			print("file downloaded to: "+str(fpath))
		except Exception as err:
			print("Oops!  There was an error downloading the file: " + format(err)+'\n'+ traceback.format_exc())
			pass
		return

	def transformToCog(self):
		try:
			self._cog_local_file_location = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
			"""Transform the tiff file to COG and returns the the file location"""
			tif2cog.tif2cog([self._tiff_local_file_location], self._cog_local_file_location, self._type)
			self._cog_local_file_location = str(self._cog_local_file_location)
			self._status._message = '\n'+ " Transform: Cog file created at: "+ self._cog_local_file_location
		except Exception as err:
			self._status._ok = False
			self._status._message += '\n'+ " Transform:  There was an error creating the COG file: " + format(err) + '\n'+ traceback.format_exc()
			print(self._status._message)
			pass

		return
	
	def createPystacItem(self,collection, tiff_url=""):
		"""create a stac catalog item using pystac library""" 
		try:
			self._item = stac_item.stac_create_item(str(self._cog_local_file_location), tiff_url+"/"+self._filename, self._name, self._datetime, collection, self._properties)
			self._status._message += '\n'+ " Create Catalog Item:   Catalog item created "
		    
		except Exception as err:
			self._status._ok = False
			self._status._message += '\n'+ " Create Catalog Item:  There was an error creating the Catalog item : " + format(err) + '\n'+ traceback.format_exc()
			print(self._status._message)
			pass

		return self._item

	def getCogFilePath(self):
		return self._cog_local_file_location

	def getFileName(self):
		return self._filename

	def deleteItemFile(self):
		"""delete the temporal file """
		try:
			os.remove(self._cog_local_file_location)

			if self._delete_tiff_local_file:
				os.remove(self._tiff_local_file_location)
		except Exception as err:
			self._status._ok = False
			self._status._message += '\n'+ " Delete file:  There was an error deleting the COG item file : " + format(err)+ '\n'+ traceback.format_exc()
			print(self._status._message)
			pass

		return

	def loggingStatus(self):
		print(json.dumps(self._status.__dict__))
		return
    
	def getItem(self):
		return self._item

# class to model stac catalog collection
class Collection:

	_items: List[StacItem] = []

	_spatial_extent = None
	_temporal_extent = None
	_collection_extent = None
	_collection_id = None
	_collection = None
	_collection_title = None
	_collection_description = None
	_collection_license = None
	_collection_folder = None

	def createCollection(self):
		"""Return a pystac.Collection"""
		print("creating collection")
		return self._collection

	def createCollectionFromParams(self, **kwargs):
		"""Return a pystac.Collection"""
		self._spatial_extent = kwargs["spatial_extent"]
		self._temporal_extent = kwargs["temporal_extent"]
		self._collection_extent = kwargs["collection_extent"]
		self._collection_id = kwargs["collection_id"]
		self._collection_title = kwargs["collection_title"]
		self._collection_description = kwargs["collection_description"]
		self._collection_license = kwargs["collection_license"]
		self._collection_folder = kwargs["collection_folder"]
		self._collection = pystac.Collection(id=self._collection_id,
									title=self._collection_title,
									description=self._collection_description,
									extent=self._collection_extent,
									license=self._collection_license,
									href=self._collection_id)
		return self._collection

	def createItemList(self):
		"""Return a list of pystac items"""
		print("creating item list")
		return self._items

	def getItemList(self):
		"""Returns the item list"""
		return self._items

	def getCollection(self):
		return self._collection

	def print(self):
		print("***collection***")
		print(self._collection.to_dict())
		for item in self._items:
			print(json.dumps(item.__dict__))

# class to model pipeline
class BqIoStacPipeline:

	_s3_upload_func = None
	_api_push_func = None
	_api_host = None

	# status of the item process with messages
	_status: Status = Status()

	
	def _createCollection(self, collection:Collection):
		collection.createCollection()
		collection.createItemList()
		return collection

	def _pushCollectionToApi(self, collection:pystac.Collection):
		if self._api_push_func is not None:
			print("pushing Collection")
			self._api_push_func(collection, self._api_host)
		return

	def _pushItemToApi(self, item:pystac.Item):
		if self._api_push_func is not None:
			print("pushing item")
			self._api_push_func(item, self._api_host)
			
		return
    
	def _save_COG_file(self, item: StacItem, collection: Collection):	
		res = self._s3_upload_func(item, collection)
		print(json.dumps(res.__dict__))

		return

	def _COG_Pystac_Push(self, collection:Collection, host:str):
		"""
		:params Collection collection: 
		:params str host: collection location,  exemple: https://object-arbutus.cloud.computecanada.ca
		:params str folder: collection folder location in host, exemple: bq-io/io/CHELSA/climatologies	
		
		"""

		for item in collection.getItemList():
				item.getItemFile()
				item.transformToCog()
				item.createPystacItem(collection.getCollection(), host+"/"+collection._collection_folder)
				self._save_COG_file(item, collection)
				self._pushItemToApi(item.getItem())
				item.deleteItemFile()
		
		for item in collection.getItemList():
			item.loggingStatus()

    #---
	def setPushToApiFunc(self,fn, api_host):
		self._api_push_func = fn
		self._api_host = api_host
		return

	def setS3UploadFunc(self,fn):
		self._s3_upload_func = fn
		return
		
	def run(self,collection:Collection, host:str):
		collection_update: Collection = self._createCollection(collection)
		self._pushCollectionToApi(collection_update.getCollection())
		self._COG_Pystac_Push(collection,host)

		return


