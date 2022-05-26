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


catalog = pystac.Catalog.from_file(os.path.join("/bqio/stac4/","catalog.json"))
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

try:
	temp_output_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
	tif2cog.tif2cog([Path('/bqio/lulc-human-modification-terrestrial-systems_geographic.tif')], temp_output_path, "raw")
	tif_url = upload_tiff_to_io(str(temp_output_path), 'lulc-human-modification-terrestrial-systems_geographic.tif', "GHMTS")
	properties = {
		'description': 'Global Human Modification of Terrestrial Systems',
		'version': '2016',
	}
	item = stac_item.stac_create_item(str(temp_output_path), tif_url, 'GHMTS', datetime.fromisoformat('2016-01-01'), collection, properties)
	collection.add_item(item)
	os.remove(temp_output_path)
except (RuntimeError, TypeError, NameError) as err:
	print("Oops!  There was an error creating the COG -" + format(err))

catalog.add_child(collection)
catalog.normalize_hrefs(root_href="https://io.biodiversite-quebec.ca/stac/")
catalog.save(dest_href='/bqio/stac5/',catalog_type=pystac.CatalogType.SELF_CONTAINED)