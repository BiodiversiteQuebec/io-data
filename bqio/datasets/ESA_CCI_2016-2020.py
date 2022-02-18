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


years=list(range(2016,2021,1))

#Already converted from NetCDF TO COG
#docker exec -it --env HDF5_DISABLE_VERSION_CHECK=1 gp gdalwarp -of COG -co COMPRESS=DEFLATE -co TILED=YES -co NUM_THREADS=ALL_CPUS -wo NUM_THREADS=ALL_CPUS -multi -ot Byte -te -180.0000000 -90.0000000 180.0000000 90.0000000 -tr 0.002777777777778 0.002777777777778 -t_srs EPSG:4326 NETCDF:/bqio/C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc:lccs_class /bqio/C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.tif

for y in years:
	filename="C3S-LC-L4-LCCS-Map-300m-P1Y-"+y+"-v2.1.1.tif"
	path='/bqio/'+filename
	tif_url = upload_tiff_to_io(path, filename, "ESACCI-LC/")
	properties = {
			'description': 'ESA Land cover time series',
			'version': 2.1.1,
			'year':y,
		}
	item = stac_item.stac_create_item(str(temp_output_path), tif_url, name, datetime.fromisoformat(y+'-01-01'),collection, properties)
	collection.add_item(item)