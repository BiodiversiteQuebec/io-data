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
		collection_id = 'earthenv_habitat_heterogeneity'
		collection_title = "EarthEnv - Habitat heterogeneity"
		collection_description = 'The datasets contain 14 metrics quantifying spatial heterogeneity of global habitat at multiple resolutions based on the textural features of Enhanced Vegetation Index (EVI) imagery acquired by the Moderate Resolution Imaging Spectroradiometer (MODIS).'
		collection_license = 'CC-BY-NC-4.0'
		collection_folder = 'earthenv/habitat_heterogeneity'
		collection = self.createCollectionFromParams(collection_title=collection_title, collection_description=collection_description, collection_license = collection_license, spatial_extent=spatial_extent,temporal_extent=temporal_extent,collection_extent=collection_extent, collection_id=collection_id, collection_folder=collection_folder)
        
		return collection

	def createItemList(self):
        vars = [{"short":"cv",
                "long":"Coefficient of variation",
                "dtype":"uint16",
                "desc":"Normalized dispersion of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"evenness",
                "long":"Evenness",
                "dtype":"uint16",
                "desc":"Evenness of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"range",
                "long":"Range",
                "dtype":"uint16",
                "desc":"Range of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"shannon",
                "long":"Shannon",
                "dtype":"uint16",
                "desc":"Diversity of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"shannon",
                "long":"Shannon",
                "dtype":"uint16",
                "desc":"Diversity of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"simpson",
                "long":"Shannon",
                "dtype":"uint16",
                "desc":"Diversity of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"std",
                "long":"Standard deviation",
                "dtype":"uint16",
                "desc":"Dispersion of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"Contrast",
                "long":"Contrast",
                "dtype":"uint32",
                "desc":"Exponentially weighted difference in EVI between adjacent pixels",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"Correlation",
                "long":"Correlation",
                "dtype":"uint32",
                "desc":"Linear dependency of EVI on adjacent pixels",
                "relation_with_heterogeneity": "Nonlinear",
                },
                {"short":"Dissimilarity",
                "long":"Dissimilarity",
                "dtype":"uint32",
                "desc":"Difference in EVI between adjacent pixels",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"Entropy",
                "long":"Entropy",
                "dtype":"uint16",
                "desc":"Disorderliness of EVI",
                "relation_with_heterogeneity": "Positive",
                },
                {"short":"Homogeneity",
                "long":"Homogeneity",
                "dtype":"uint16",
                "desc":"Similarity of EVI between adjacent pixels",
                "relation_with_heterogeneity": "Negative",
                },
                {"short":"Maximum",
                "long":"Maximum",
                "dtype":"uint16",
                "desc":"Dominance of EVI combinations between adjacent pixels",
                "relation_with_heterogeneity": "Negative",
                },
                {"short":"Uniformity",
                "long":"Uniformity",
                "dtype":"uint16",
                "desc":"Orderliness of EVI",
                "relation_with_heterogeneity": "Negative",
                },
                {"short":"Variance",
                "long":"Variance",
                "dtype":"uint32",
                "desc":"Dispersion of EVI combinations between adjacent pixels",
                "relation_with_heterogeneity": "Positive",
                },
            ]
		for v in vars:
            filename=v['short']+'_01_05_1km_'+v['dtype']+'.tif'
            name=v['long']
            path='https://data.earthenv.org/habitat_heterogeneity/1km/'+filename
            folder="https://object-arbutus.cloud.computecanada.ca/bq-io/io/earthenv/habitat_heterogeneity/"
			properties = {
				'full_filename': filename,
                'variable': v['long'],
				'description': v['desc'] + ' - 1 km',
				'relation_with_heterogeneity': v['relation_with_heterogeneity'],
			}
			newItem: ThisStacItem = ThisStacItem(name, filename, datetime.fromisoformat('2015-01-01'), properties, path, "raw", False)
			self.getItemList().append(newItem)

		return


thisCollection:ThisCollection = ThisCollection()

# params to create links of stac items for this collection
host:str = "https://object-arbutus.cloud.computecanada.ca" # host name of the server stac will be located
#stac_api_host = "http://localhost:8082" # host where stac api is running
stac_api_host = "https://io.biodiversite-quebec.ca/stac/" # host where stac api is running

pipeline: BqIoStacPipeline = BqIoStacPipeline()
pipeline.setS3UploadFunc(upload_file_bq_io)
pipeline.setPushToApiFunc(push_to_api,stac_api_host)
pipeline.run(thisCollection,host)





	
