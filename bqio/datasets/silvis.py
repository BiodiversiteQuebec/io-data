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
		
		spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("2013-01-01"),datetime.fromisoformat("2015-12-31")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id = 'silvis'
		collection_title = "Silvis Dynamic Habitat Indices"
		collection_description = 'The DHIs are designed for biodiversity assessments and to describe habitats of different species.'
		collection_license = 'CC-BY-SA-4.0'
		collection_folder = 'silvis'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
        
		return collection

	def createItemList(self):
		varlist=[
			{
				'filename':'dhi_ndviqa_f',
				'name':'NDVI16',
				'desc':'Normalized Difference Vegetation Index'
			},
			{
				'filename':'dhi_eviqa_f',
				'name':'EVI16',
				'desc':'Enhanced Vegetation Index'
			},
			{
				'filename':'dhi_fpar8qa_f',
				'name':'FPAR8',
				'desc':'Fraction absorbed Photosynthetically Active Radiation'
			},
			{
				'filename':'dhi_lai8qa_f',
				'name':'LAI8',
				'desc':'Leaf Area Index'
			},
			{
				'filename':'dhi_gppqa_f',
				'name':'GPP8',
				'desc':'Gross Primary Productivity'
			},
		]
		type=['cumulative','minimum','seasonality']
		for row in varlist:
			for t in type:
				folder="https://object-arbutus.cloud.computecanada.ca/bq-io/io/silvis/"
				name=row['name']+'_'+t
				filename=row['filename']+'_'+t+'.tif'
				uri=folder+name+'_'+t
				properties = {
					'full_filename': filename,
					'description': row['desc'] +' - '+t,
					'variable': row['name'],
					'index': t,
				}
				uri='/bqio/silvis/'+filename
				newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat('2003-01-01'), properties, uri, "raw", True)
				self.getItemList().append(newItem)

		return


thisCollection:ThisCollection = ThisCollection()

# params to create links of stac items for this collection
host:str = "https://object-arbutus.cloud.computecanada.ca/bq-io/io" # host name of the server stac will be located
#stac_api_host = "http://localhost:8082" # host where stac api is running
stac_api_host = "https://io.biodiversite-quebec.ca/stac" # host where stac api is running

pipeline: BqIoStacPipeline = BqIoStacPipeline()
pipeline.setS3UploadFunc(upload_file_bq_io)
pipeline.setPushToApiFunc(push_to_api,stac_api_host)
pipeline.run(thisCollection,host)





	
