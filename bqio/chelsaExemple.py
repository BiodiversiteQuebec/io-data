import pystac
from datetime import datetime
import tempfile
from pathlib import Path
import urllib.request
import traceback
from lib.utils import upload_file_bq_sql_backup, push_to_api

from lib.pipelinelib import StacItem, Collection, BqIoStacPipeline


class ChelsaStacItem(StacItem):

	# example of getting source tiff file from local path
	def getItemFile(self):

		"""try:
			self._tiff_local_file_location = Path(.._file_source_location..)
		except Exception as err:
			print("Oops!  There was an error downloading the file: " + format(err)+'\n'+ traceback.format_exc())
			pass"""					

		return

class ChelsaCollection(Collection):

	def createCollection(self):
		"""Overrides the implementation of createCollection from Parent class (Collection)"""
		
		
		spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("1981-01-01"),datetime.fromisoformat("2100-01-01")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id = 'chelsa-clim-proj'
		collection = self.createCollectionFromParams(spatial_extent=spatial_extent,temporal_extent=temporal_extent, collection_extent=collection_extent, collection_id=collection_id )
        
		return collection

	def createItemList(self):

        
		#variables=["bio1","bio2","bio3","bio4","bio5","bio6","bio7","bio8","bio9","bio10","bio11","bio12","bio13","bio14","bio15","bio16","bio17","bio18","bio19"]
		variables=["bio1"]
		#models=["gfdl-esm4","ipsl-cm6a-lr","mpi-esm1-2-hr","mri-esm2-0","ukesm1-0-ll"]
		models=["gfdl-esm4"]
		#rcps=["ssp126","ssp370","ssp585"]
		rcps=["ssp126"]
		#times=["2011-2040","2041-2070","2071-2100"]
		times=["2011-2040"]

		for v in variables:
			for m in models:
				for r in rcps:
					for t in times:
						# create metada info for StacItem object

						folder="https://object-arbutus.cloud.computecanada.ca/bq-io/io/CHELSA/climatologies/"
						name=v+"_"+t+"_"+m+"_"+r
						filename="CHELSA_"+name+"_V.2.1.tif"
						uri=folder+filename

						properties = {
						'full_filename': filename,
						'description': 'CHELSA Climatologies projections - '+v,
						'variable': v,
						'version': 2.1,
						'model': m,
						'rcp': r,
						'time_span': t
					    }

						newItem: StacItem = StacItem(name, filename, datetime.fromisoformat(t.split('-')[0]+'-01-01'), properties, uri, "raw", True)
						# newItem: ChelsaStacItem = ChelsaStacItem(name, filename, datetime.fromisoformat(t.split('-')[0]+'-01-01'), properties, uri, "raw", False)
						self.getItemList().append(newItem)

		return


chelsaCollection:ChelsaCollection = ChelsaCollection()

# params to create links of stac items for this collection
host:str = "https://object-arbutus.cloud.computecanada.ca" # host name of the server stac will be located
folder:str = "bq-sql-backup/io/CHELSA/climatologies"       # destination folder in server
#stac_api_host = "http://localhost:8082" # host where stac api is running
stac_api_host = "https://io.biodiversite-quebec.ca/stac-fast-api" # host where stac api is running

pipeline: BqIoStacPipeline = BqIoStacPipeline()
pipeline.setS3UploadFunc(upload_file_bq_sql_backup)
pipeline.setPushToApiFunc(push_to_api,stac_api_host)
pipeline.run(chelsaCollection,host,folder)





	
