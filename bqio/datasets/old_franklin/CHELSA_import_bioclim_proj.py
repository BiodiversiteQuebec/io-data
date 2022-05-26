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



catalog = pystac.Catalog.from_file(os.path.join("/bqio/stac/","catalog.json"))

variables=["bio1","bio2","bio3","bio4","bio5","bio6","bio7","bio8","bio9","bio10","bio11","bio12","bio13","bio14","bio15","bio16","bio17","bio18","bio19"]
models=["gfdl-esm4","ipsl-cm6a-lr","mpi-esm1-2-hr","mri-esm2-0","ukesm1-0-ll"]
rcps=["ssp126","ssp370","ssp585"]
times=["2011-2040","2041-2070","2071-2100"]


spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])
temporal_extent = pystac.TemporalExtent(intervals=[[datetime.fromisoformat("1981-01-01"),datetime.fromisoformat("2100-01-01")]])
collection_extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
collection_id = 'chelsa-clim-proj'
collection = pystac.Collection(id=collection_id,
							   title='CHELSA Climatologies Projections',
                               description='CHELSA Climatologies Projections',
                               extent=collection_extent,
                               license='CC-BY-SA-4.0',
                               href=collection_id)

for v in variables:
	for m in models:
		for r in rcps:
			for t in times:
				folder="https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V2/GLOBAL/climatologies/"+t+"/"+m.upper()+"/"+r+"/bio/"
				name=v+"_"+t+"_"+m+"_"+r
				filename="CHELSA_"+name+"_V.2.1.tif"
				uri=folder+filename
				print(uri)
				try:
					temp_input_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
					temp_output_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".tif")
					temptif = urllib.request.urlretrieve(uri, temp_input_path)
					tif2cog.tif2cog([temp_input_path], temp_output_path, "raw")
					tif_url = upload_tiff_to_io(str(temp_output_path), filename, "CHELSA/climatologies")
					properties = {
						'full_filename': filename,
						'description': 'CHELSA Climatologies projections - '+v,
						'variable': v,
						'version': 2.1,
						'model': m,
						'rcp': r,
						'time_span': t
					}
					item = stac_item.stac_create_item(str(temp_output_path), tif_url, name, datetime.fromisoformat(t.split('-')[0]+'-01-01'),collection, properties)
					collection.add_item(item)
					print(filename +' successfully processed!')
					os.remove(temp_output_path) 
					os.remove(temp_input_path) 
				except (RuntimeError, TypeError, NameError) as err:
					print("Oops!  There was an error creating the COG" + format(err))


catalog.add_child(collection)

catalog.normalize_hrefs(root_href="https://io.biodiversite-quebec.ca/stac/")
catalog.save(dest_href='/bqio/stac2/',catalog_type=pystac.CatalogType.SELF_CONTAINED)

#upload_stac_to_io("/bqio/stac/")