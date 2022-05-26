import pystac
import os
from urllib.parse import urlparse
from datetime import datetime
import tempfile
from pathlib import Path
import urllib.request
import requests
import sys
sys.path.append('/bqio/')
import tif2cog
import stac_item
from s3io import upload_tiff_to_io
from s3io import upload_stac_to_io



catalog = pystac.Catalog.from_file(os.path.join("/bqio/stac6/","catalog.json"))

#variables=["tas","tasmax","tasmin","clt","cmi","hurs","pet","pr","sfcWind","vpd"]
variables=["pet"]
spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])
temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("1980-01-01"),datetime.fromisoformat("2019-12-31")]])
collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
collection_id = 'chelsa-monthly'
collection = pystac.Collection(id=collection_id,
							   title='CHELSA monthly timeseries',
                               description='CHELSA monthly timeseries',
                               extent=collection_extent,
                               license='CC-BY-SA-4.0',
                               href=collection_id)

for v in variables:
	for m in range(1,13):
		for y in range(1979,2020):
				folder="https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V2/GLOBAL/monthly/"+v+"/"
				if(v=='pet'):
					name="pet_penman_"+str(m).zfill(2)+"_"+str(y)
				else:
					name=v+"_"+str(m).zfill(2)+"_"+str(y)
				filename="CHELSA_"+name+"_V.2.1.tif"
				uri=folder+filename
				print(uri)
				try:
					temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
					temp_output_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
					r = requests.head(uri)
					cloud_uri = 'https://object-arbutus.cloud.computecanada.ca/bq-io/io/CHELSA/monthly/'+filename
					r2 = requests.head(cloud_uri)
					print(cloud_uri)
					if((r.status_code == 200) & (r2.status_code != 200)):
						temptif = urllib.request.urlretrieve(uri, temp_input_path)
						tif2cog.tif2cog([temp_input_path], temp_output_path, "raw")
						tif_url = upload_tiff_to_io(str(temp_output_path), filename, "CHELSA/monthly")
						os.remove(temp_input_path) 
					elif((r.status_code == 200) & (r2.status_code == 200)):
						temptif = urllib.request.urlretrieve(cloud_uri, temp_output_path)
						r2 = requests.head(cloud_uri)
						if(r2.status_code == 200):
							properties = {
								'full_filename': filename,
								'description': 'CHELSA Monthly - '+str(y)+'-'+str(m),
								'variable': v,
								'version': 2.1,
								'year': y,
								'month': m
							}
							item = stac_item.stac_create_item(str(temp_output_path), cloud_uri, name, datetime.fromisoformat(str(y)+'-'+str(m).zfill(2)+'-01'),collection, properties)
							collection.add_item(item)
							print(filename +' successfully processed!')
							os.remove(temp_output_path) 
					else:
						print(filename +' not available!')
						continue
				except (RuntimeError, TypeError, NameError) as err:
					pass
					print("Oops!  There was an error creating the COG" + format(err))


catalog.add_child(collection)

catalog.normalize_hrefs(root_href="https://io.biodiversite-quebec.ca/stac/")
catalog.save(dest_href='/bqio/stac7/',catalog_type=pystac.CatalogType.SELF_CONTAINED)

#upload_stac_to_io("/bqio/stac/")