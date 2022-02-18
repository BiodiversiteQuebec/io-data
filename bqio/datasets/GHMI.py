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


catalog = pystac.Catalog.from_file(os.path.join("/bqio/stac3/","catalog.json"))
spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])
temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("2016-01-01"),datetime.fromisoformat("2016-12-31")]])
collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
collection_id = 'ghmts'
collection = pystac.Collection(id=collection_id,
							   title='Global Human Modification of Terrestrial Systems',
                               description='The Global Human Modification of Terrestrial Systems data set provides a cumulative measure of the human modification of terrestrial lands across the globe at a 1-km resolution. It is a continuous 0-1 metric that reflects the proportion of a landscape modified, based on modeling the physical extents of 13 anthropogenic stressors and their estimated impacts using spatially-explicit global data sets with a median year of 2016.',
                               extent=collection_extent,
                               license='CC-BY-SA-4.0',
                               href=collection_id)

for y in years:
	filename="ESACCI-LC-L4-LCCS-Map-300m-P1Y-"+str(y)+"-v2.0.7.tif"
	uri="ftp://geo10.elie.ucl.ac.be/CCI/LandCover/byYear/"+filename
	try:
		temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
		temp_output_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
		temptif = urllib.request.urlretrieve(uri, temp_input_path)
		tif2cog.tif2cog([temp_input_path], temp_output_path, "raw")
		tif_url = upload_tiff_to_io(str(temp_output_path), filename, "ESACCI-LC")
		properties = {
			'description': 'ESA Land cover time series',
			'version': '2.0.7',
			'year':y,
		}
		item = stac_item.stac_create_item(str(temp_output_path), tif_url, 'ESA CCI land cover'+str(y), datetime.fromisoformat(str(y)+'-01-01'),collection, properties)
		collection.add_item(item)
		print(filename +' successfully processed!')
		os.remove(temp_output_path) 
		os.remove(temp_input_path) 
	except (RuntimeError, TypeError, NameError) as err:
		print("Oops!  There was an error creating the COG" + format(err))

years=list(range(2016,2021,1))

#Already converted from NetCDF TO COG
#docker exec -it --env HDF5_DISABLE_VERSION_CHECK=1 gp gdalwarp -of COG -co COMPRESS=DEFLATE -co TILED=YES -co NUM_THREADS=ALL_CPUS -wo NUM_THREADS=ALL_CPUS -multi -ot Byte -te -180.0000000 -90.0000000 180.0000000 90.0000000 -tr 0.002777777777778 0.002777777777778 -t_srs EPSG:4326 NETCDF:/bqio/C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc:lccs_class /bqio/C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.tif

for y in years:
	filename="C3S-LC-L4-LCCS-Map-300m-P1Y-"+str(y)+"-v2.1.1.tif"
	path='/bqio/'+filename
	tif_url = upload_tiff_to_io(path, filename, "ESACCI-LC")
	properties = {
			'description': 'ESA Land cover time series',
			'version': '2.1.1',
			'year':y,
	}
	item = stac_item.stac_create_item(str(path), tif_url, 'ESA CCI land cover'+str(y), datetime.fromisoformat(str(y)+'-01-01'),collection, properties)
	collection.add_item(item)

catalog.add_child(collection)
catalog.normalize_hrefs(root_href="https://io.biodiversite-quebec.ca/stac/")
catalog.save(dest_href='/bqio/stac4/',catalog_type=pystac.CatalogType.SELF_CONTAINED)