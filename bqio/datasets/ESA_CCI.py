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

years=list(range(1992,2016,1))

spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])
temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("1992-01-01"),datetime.fromisoformat("2019-01-01")]])
collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
collection_id = 'esa-cci'
collection = pystac.Collection(id=collection_id,
							   title='ESA Land cover time series',
                               description='ESA Land cover time series',
                               extent=collection_extent,
                               license='CC-BY-SA-4.0',
                               href=collection_id)

for y in years:
	uri="ftp://geo10.elie.ucl.ac.be/CCI/LandCover/byYear/ESACCI-LC-L4-LCCS-Map-300m-P1Y-"+y+"-v2.0.7.tif"
	try:
		temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
		temp_output_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
		temptif = urllib.request.urlretrieve(uri, temp_input_path)
		tif2cog.tif2cog([temp_input_path], temp_output_path, "raw")
		tif_url = upload_tiff_to_io(str(temp_output_path), filename, "ESA-CCI/")
		properties = {
			'description': 'ESA Land cover time series',
			'variable': v,
			'version': 2.1.1,
			'year':y,
		}
		item = stac_item.stac_create_item(str(temp_output_path), tif_url, name, datetime.fromisoformat(y+'-01-01'),collection, properties)
		collection.add_item(item)
		print(filename +' successfully processed!')
		os.remove(temp_output_path) 
		os.remove(temp_input_path) 
	except (RuntimeError, TypeError, NameError) as err:
		print("Oops!  There was an error creating the COG" + format(err))



catalog.add_child(collection)
catalog.normalize_hrefs(root_href="https://io.biodiversite-quebec.ca/stac/")
catalog.save(dest_href='/bqio/stac2/',catalog_type=pystac.CatalogType.SELF_CONTAINED)