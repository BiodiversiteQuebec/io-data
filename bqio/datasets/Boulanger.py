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


for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    tif_url = upload_tiff_to_io(str(temp_output_path), filename, "FORETS-CC-LANDIS")
