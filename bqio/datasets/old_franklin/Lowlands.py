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


directory='/bqio/btsl/landcover/'
for filename in os.listdir(directory):
    print(filename)
    temp_output_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
    temp_output_path2 = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
    tif2cog.tif2cog([directory+filename], temp_output_path, "display")
    tif_url = upload_tiff_to_io(str(temp_output_path), filename, "btsl-connectivity")
