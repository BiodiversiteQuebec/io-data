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



catalog = pystac.Catalog.from_file(os.path.join("/bqio/stac9/","catalog.json"))
spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])

temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("2000-01-01"),datetime.fromisoformat("2000-01-31")]])
collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
collection_id = 'gfw-treecover2000'
collection = pystac.Collection(id=collection_id,
							   title='Global Forest Watch - Tree cover 2000',
                               description='Global Forest Watch - Tree cover 2000',
                               extent=collection_extent,
                               license='CC-BY-SA-4.0',
                               href=collection_id)

file1 = open('/bqio/datasets/treecover2000.txt', 'r')
filelist = file1.readlines()

for file in filelist:
	try:
		file=file.strip('\n').strip(' ')
		url_parts = urlparse(file)
		filename=os.path.basename(url_parts.path)
		temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
		temp_output_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
		temptif = urllib.request.urlretrieve(file, temp_input_path)
		tif2cog.tif2cog([temp_input_path], temp_output_path, "raw")
		tif_url = upload_tiff_to_io(str(temp_output_path), filename, "GFW/treecover2000")
		var=filename.replace('Hansen_GFC-2020-v1.8_treecover2000_','').replace('.tif','')
		properties = {
			'full_filename': filename,
			'description': 'Global Forest Watch - Tree cover 2000 - '+var,
			'grid': var,
		}
		item = stac_item.stac_create_item(str(temp_output_path), tif_url, var, datetime.fromisoformat("2000-01-01"),collection, properties)
		collection.add_item(item)
		print(file +' successfully processed!')
		os.remove(temp_output_path) 
		os.remove(temp_input_path) 
	except (RuntimeError, TypeError, NameError) as err:
		print("Oops!  There was an error creating the COG" + format(err))


catalog.add_child(collection)

catalog.normalize_hrefs(root_href="https://io.biodiversite-quebec.ca/stac/")
catalog.save(dest_href='/bqio/stac10/',catalog_type=pystac.CatalogType.SELF_CONTAINED)
