import pystac
import os
from urllib.parse import urlparse
from datetime import datetime
import tempfile
from pathlib import Path
import urllib.request
import sys
sys.path.append('/bqio/')
import tif2cog
import stac_item
from s3io import upload_tiff_to_io
from s3io import upload_stac_to_io


var=['bdod','cec','cfvo','clay','nitrogen','ocd','phh2o','sand','silt','soc','wv0010','wv0033','wv1500']
depths=['0-5cm','5-15cm','15-30cm','30-60cm','60-100cm','100-200cm']
base_url='https://object-arbutus.cloud.computecanada.ca/bq-io/io/soilgrids/'


		
catalog = pystac.Catalog.from_file(os.path.join("/bqio/stac8/","catalog.json"))
spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])         
temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("1905-03-31"),datetime.fromisoformat("2016-07-04")]])
collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
collection_id = 'soilgrids'
collection = pystac.Collection(id=collection_id,
							   title='Soil Grids datasets',
                               description='SoilGrids aggregated datasets at 1km resolution',
                               extent=collection_extent,
                               license='CC-BY-SA-4.0',
                               href=collection_id)

for v in var:
	for d in depths:
		filename=v+'_'+d+'_mean_1000.tif'
		fileurl=base_url+filename
		print("Processing " + fileurl)
		try:
			temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
			temptif = urllib.request.urlretrieve(fileurl, temp_input_path)
			print("Downloaded " + str(temp_input_path))
			properties = {
				'description': 'SoilGrids aggregated mean -'+v+' - '+d,
				'version': '1',
				'variable': v,
				'depth': d,
			}
			item = stac_item.stac_create_item(str(temp_input_path), fileurl, v+'_'+d , datetime.fromisoformat('2016-07-04'),collection, properties)
			collection.add_item(item)
			print(filename +' successfully processed!') 
			os.remove(temp_input_path) 
		except (RuntimeError, TypeError, NameError) as err:
			print("Oops!  There was an error creating the COG" + format(err))

v='ocs'
d='0-30cm'
try:
	filename=v+'_'+d+'_mean_1000.tif'
	fileurl=base_url+filename
	print("Downloaded " + str(temp_input_path))
	temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
	temptif = urllib.request.urlretrieve(fileurl, temp_input_path)
	properties = {
		'description': 'SoilGrids aggregated mean -'+v+' - '+d,
		'version': '1',
		'variable': v,
		'depth': d,
	}
	item = stac_item.stac_create_item(str(temp_input_path), fileurl, v+'_'+d , datetime.fromisoformat('2016-07-04'),collection, properties)
	collection.add_item(item)
	print(filename +' successfully processed!')
	os.remove(temp_input_path) 
except (RuntimeError, TypeError, NameError) as err:
	print("Oops!  There was an error creating the COG" + format(err))

catalog.add_child(collection)
catalog.normalize_hrefs(root_href="https://io.biodiversite-quebec.ca/stac/")
catalog.save(dest_href='/bqio/stac9/',catalog_type=pystac.CatalogType.SELF_CONTAINED)