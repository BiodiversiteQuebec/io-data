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
		
		spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -60, 180, 85]])
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("2015-01-01"),datetime.fromisoformat("2015-12-31")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id ='accessibility_to_cities'
		collection_title = "Accessibility - Time to access cities"
		collection_description = 'This global accessibility map enumerates land-based travel time to the nearest densely-populated area for all areas between 85 degrees north and 60 degrees south for a nominal year 2015. Densely-populated areas are defined as contiguous areas with 1,500 or more inhabitants per square kilometer or a majority of built-up land cover types coincident with a population centre of at least 50,000 inhabitants.'
		collection_license = 'CC-BY-NC-4.0'
		collection_folder = 'accessibility'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
		
		return collection

	def createItemList(self):
		filename='2015_accessibility_to_cities_v1.0.tif'
		name='accessibility'
		properties = {
			'full_filename': filename,
			'description': 'Accessibility - Time to access cities in minutes',
		}
		path='/bqio/accessibility/'+filename
		newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat('2015-01-01'), properties, path, "raw", False)
		self.getItemList().append(newItem)

		return


thisCollection:ThisCollection = ThisCollection()

# params to create links of stac items for this collection
host:str = "https://object-arbutus.cloud.computecanada.ca/bq-io/io" # host name of the server stac will be located
#stac_api_host = "http://localhost:8082" # host where stac api is running
stac_api_host = "https://io.biodiversite-quebec.ca/stac/" # host where stac api is running

pipeline: BqIoStacPipeline = BqIoStacPipeline()
pipeline.setS3UploadFunc(upload_file_bq_io)
pipeline.setPushToApiFunc(push_to_api,stac_api_host)
pipeline.run(thisCollection,host)





	
