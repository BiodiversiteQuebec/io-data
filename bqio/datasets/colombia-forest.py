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
		
		spatial_extent = pystac.SpatialExtent(bboxes=[[-81.68, -4.24 -66.55, 12.9]])
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("1990-01-01"),datetime.fromisoformat("2020-12-31")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id = 'colombia_forests'
		collection_title = "Time series of the presence of forests in Colombia"
		collection_description = 'Yearly time series of binary forest cover in Colombia'
		collection_license = 'CC-BY-SA-4.0'
		collection_folder = 'colombia/forests'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
        
		return collection

	def createItemList(self):
		years = ["1990_2000","2000_2005","2005_2010","2010_2012","2012_2013","2013_2014","2014_2015","2015_2016","2016_2017","2017_2018","2018_2019","2019_2020"]
		for y in years:
			filename='DCCB_SMBYC_CBBQ_'+y+'.tif'
			folder="/bqio/colombia-lc/forest/IDEAM_ForestChange/"
			name='forests_'+y
			uri=folder+filename
			properties = {
				'full_filename': filename,
				'description': 'Forest cover for Colombia for year(s) ' + y,
				'years': y,
			}
			syear=y.split('_')[0]
			newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat(syear+'-01-01'), properties, uri, "raw", False)
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





	
