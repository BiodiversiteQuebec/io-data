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
		
		spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -56, 180, 90]])
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("2000-01-01"),datetime.fromisoformat("2000-01-01")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id = 'earthenv_landcover'
		collection_title = "EarthEnv - Consensus Land Cover - Full version"
		collection_description = 'Consensus land cover dataset containing 12 data layers, each of which provides consensus information on the prevalence of one land-cover class. All data layers contain unsigned 8-bit values and the valid values range from 0-100, representing the consensus prevalence in percentage. All data layers have a spatial extent from 90ºN - 56ºS and from 180ºW - 180ºE, and have a spatial resolution of 30 arc-second per pixel (~1 km per pixel at the equator).'
		collection_license = 'CC-BY-NC-4.0'
		collection_folder = 'earthenv/landcover'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
		
		return collection

	def createItemList(self):
		vars = [{"short":"class_1",
				'class':'1',
				"long":"Evergreen/Deciduous Needleleaf Trees",
				},
				{"short":"class_2",
				'class':'2',
				"long":"Evergreen Broadleaf Trees",
				},
				{"short":"class_3",
				'class':'3',
				"long":"Deciduous Broadleaf Trees",
				},
				{"short":"class_4",
				'class':'4',
				"long":"Mixed/Other Trees",
				},
				{"short":"class_5",
				'class':'5',
				"long":"Shrubs",
				},
				{"short":"class_6",
				'class':'6',
				"long":"Herbaceous Vegetation",
				},
				{"short":"class_7",
				'class':'7',
				"long":"Cultivated and Managed Vegetation",
				},
				{"short":"class_8",
				'class':'8',
				"long":"Regularly Flooded Vegetation",
				},
				{"short":"class_9",
				'class':'9',
				"long":"Urban/Built-up",
				},
				{"short":"class_10",
				'class':'10',
				"long":"Snow/Ice",
				},
				{"short":"class_11",
				'class':'11',
				"long":"Barren",
				},
				{"short":"class_12",
				'class':'12',
				"long":"Open Water",
				}
			]
		for v in vars:
			filename='consensus_full_'+v['short']+'.tif'
			name=v['short']
			path='https://data.earthenv.org/consensus_landcover/with_DISCover/'+filename
			properties = {
				'full_filename': filename,
				'class': v['class'],
				'description': v['long'],
			}
			newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat('2000-01-01'), properties, path, "raw", False)
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





	
