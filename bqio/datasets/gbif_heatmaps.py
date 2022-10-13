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
		
		spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 84]])
		temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("1900-01-01"),datetime.fromisoformat("2022-06-01")]])
		collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
		collection_id = 'gbif_heatmaps'
		collection_title = "Occurrence density maps created from GBIF data"
		collection_description = 'Density maps of all occurrences in GBIF, organized by taxonomic group at an approximately 1 km resolution.'
		collection_license = 'CC-BY-NC-4.0'
		collection_folder = 'gbif_heatmaps'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
		
		return collection

	def createItemList(self):
		vars = [{"short":"all",
				"long":"All GBIF occurrences",
				},
				{"short":"arthropods",
				"long":"All GBIF arhtropod occurrences(phylum='Arthropoda')",
				},
				{"short":"birds",
				"long":"All GBIF bird occurrences (class='Aves')",
				},
				{"short":"mammals",
				"long":"All GBIF mammal occurrences (class='Mammalia')",
				},
				{"short":"plants",
				'long':"All GBIF plant occurrences (kingdom='Plantae')",
				},
			]
		for v in vars:
			filename='gbif_'+v['short']+'_density_06-2022.tif'
			name=v['short']+'-heatmap'
			path='https://object-arbutus.cloud.computecanada.ca/bq-io/io/gbif-heatmaps/'+filename
			properties = {
				'full_filename': filename,
                'taxa': v['short'],
				'description': v['long'],
			}
			newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat('2006-01-01'), properties, path, "raw", False)
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





	
