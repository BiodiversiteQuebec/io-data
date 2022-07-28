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
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("2010-01-01"),datetime.fromisoformat("2010-12-31")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id = 'earthenv_topography'
		collection_title = "EarthEnv - Topography"
		collection_description = 'A fully standardized and global multivariate product of different terrain features to support many large-scale research applications. The product is based on the digital elevation model products of global 250 m GMTED2010. From https://www.earthenv.org/topography'
		collection_license = 'CC-BY-NC-4.0'
		collection_folder = 'earthenv/topography'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
		
		return collection

	def createItemList(self):
		vars = [{"short":"elevation",
				"long":"Mean elevation",
				"desc":"Mean elevation at 1 km resolution. From GMTED 1.0",
                "filename" : "elevation_1KMmn_GMTEDmn.tif"
				},
                {"short":"elevation_median",
				"long":"Median elevation",
				"desc":"Median elevation at 1 km resolution. From GMTED 1.0",
                "filename" : "elevation_1KMmd_GMTEDmd.tif"
				},
                {"short":"elevation_min",
				"long":"Minimum elevation",
				"desc":"Minimum elevation at 1 km resolution. From GMTED 1.0",
                "filename" : "elevation_1KMmi_GMTEDmi.tif"
				},
                {"short":"elevation_max",
				"long":"Maximum elevation",
				"desc":"Maximum elevation at 1 km resolution. From GMTED 1.0",
                "filename" : "elevation_1KMma_GMTEDma.tif"
				},
				{"short":"slope",
				"long":"Slope",
				"desc":"Mean slope 1 km resolution. From GMTED 1.0",
                "filename" : "slope_1KMmn_GMTEDmd.tif"
				},
                {"short":"roughness",
				"long":"Roughness",
				"desc":"Mean roughness index at 1 km resolution. From GMTED 1.0",
                "filename" : "roughness_1KMmn_GMTEDmd.tif"
				},
                {"short":"tpi",
				"long":"Topographic position index",
				"desc":"Mean topographic position index at 1 km resolution. From GMTED 1.0",
                "filename" : "tpi_1KMmn_GMTEDmd.tif"
				},
                {"short":"vrm",
				"long":"Vector ruggedness measure",
				"desc":"Mean vector ruggedness measure at 1 km resolution. From GMTED 1.0",
                "filename" : "vrm_1KMmn_GMTEDmd.tif"
				},                
			]
		for v in vars:
			filename=v['filename']
            
			name=v['short'].lower()
			path="https://data.earthenv.org/topography/"+v['filename']
			properties = {
				'full_filename': filename,
				'variable': v['long'],
				'description': v['desc'],
			}
			newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat('2010-01-01'), properties, path, "raw", False)
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





	
