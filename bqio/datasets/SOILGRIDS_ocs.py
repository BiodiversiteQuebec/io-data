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



#var=['bdod','cec','cfvo','clay','nitrogen','ocd','phh2o','sand','silt','soc','wv0010','wv0033','wv1500']
base_url='https://files.isric.org/soilgrids/latest/data_aggregated/1000m/'


v='ocs'
d='0-30cm'
try:
	filename=v+'_'+d+'_mean_1000.tif'
	fileurl=base_url+'/'+v+'/'+filename
	temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
	temptif = urllib.request.urlretrieve(fileurl, temp_input_path)
	print("Downloaded " + str(temp_input_path))
	tif_url = upload_tiff_to_io(str(temp_input_path), filename, "soilgrids")
	properties = {
		'description': 'SoilGrids aggregated mean -'+v+' - '+d,
		'version': '1',
		'variable': v,
		'depth': d,
	}
	collection.add_item(item)
	print(filename +' successfully processed!')
	os.remove(temp_input_path) 
except (RuntimeError, TypeError, NameError) as err:
	print("Oops!  There was an error creating the COG" + format(err))
