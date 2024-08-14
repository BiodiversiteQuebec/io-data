import pystac
from datetime import datetime
import tempfile
from pathlib import Path
import urllib.request
import traceback
import csv
import sys
sys.path.append('/bqio/')
from lib.utils import upload_file_bq_io, push_to_api
from lib.pipelinelib import StacItem, Collection, BqIoStacPipeline
from pathlib import Path

class ThisStacItem(StacItem):

	# example of getting source tiff file from local path
	def getItemFile(self):

		try:
			self._tiff_local_file_location = Path(self._file_source_location)
		except Exception as err:
			print("Oops!  There was an error downloading the file: " + format(err)+'\n'+ traceback.format_exc())
			pass

		return
	

class ThisCollection(Collection):

	def createCollection(self):
		"""Overrides the implementation of createCollection from Parent class (Collection)"""
		
		spatial_extent = pystac.SpatialExtent(bboxes=[[-1397345, -54360.14, 1451336, 2357523]])
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("2024-01-01"),datetime.fromisoformat("2024-01-01")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id = 'species_richness_from_ebird'
		collection_title = "Raster of bird species richness derived from ebird range maps."
		collection_description = 'Rasters at 9500 m. resolution derived from ebird range maps for the Quebec breeding bird species list. See https://ebird.org/home. This map serves as inputs for EBV cubes.'
		collection_license = 'CC-0'
		collection_folder = 'acer/SR_ebird'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
        
		return collection

	def createItemList(self):

		item = {
			'id':'SR_ebird',
			'file':'rs_ebird.tif',
			'description':'Rasters at 9500 m. resolution derived from ebird range maps for the Quebec breeding bird species list.'
			}		
		# for c in items:
		filename=item['file']
		folder="/bqio/data/"
		name=item['id']
		uri=folder+filename
		properties = {
			'full_filename': filename,
			'description': item['description'],
			'year': 2024,
			'units': 'meters'	
		}
		newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat("2024-01-01"), properties, uri, "raw", False)
		self.getItemList().append(newItem)

		# return


thisCollection:ThisCollection = ThisCollection()

# params to create links of stac items for this collection
host:str = "https://object-arbutus.cloud.computecanada.ca/bq-io/" # host name of the server stac will be located
#stac_api_host = "http://localhost:8082" # host where stac api is running
stac_api_host = "https://acer.biodiversite-quebec.ca/stac/" # host where stac api is running

pipeline: BqIoStacPipeline = BqIoStacPipeline()
pipeline.setS3UploadFunc(upload_file_bq_io)
pipeline.setPushToApiFunc(push_to_api,stac_api_host)
pipeline.run(thisCollection,host)





	
