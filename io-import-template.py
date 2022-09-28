#!pip install boto3
#!pip install rasterio
#!pip install shapely

import pystac
import os
from pystac.extensions.rasters import RasterBand
from pystac.extensions.rasters import RasterExtension
from pystac.extensions.projection import ProjectionExtension
import boto3
from datetime import datetime
import rasterio
from shapely.geometry import Polygon, mapping

img_path = os.path.join('/media/glaroc/GDrive/GIS/Occupation_territoire/utilisation_territoire_2018/utilisation_territoire_2018_cog.tif')

catalog = pystac.Catalog(id='stac-bq-io', description='Biodiversité Québec - IO catalog of geospatial data')

def get_bbox_and_footprint(raster_uri):
    with rasterio.open(raster_uri) as ds:
        bounds = ds.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        
        return (bbox, mapping(footprint))



bbox, footprint = get_bbox_and_footprint(img_path)

raster_bands = [RasterBand.create(
		spatial_resolution=30,
		unit='m',
		data_type='int16'
	)
]

item = pystac.Item(id='utilisation-territoire-2018',
			geometry=footprint,
			bbox=bbox,
			datetime=datetime.utcnow(),
			properties={}
		)

asset=pystac.Asset(
    href="https://object-arbutus.cloud.computecanada.ca/bq-io/utilisation_territoire_2018_cog.tif", 
    media_type=pystac.MediaType.GEOTIFF
)
raster_ext=RasterExtension.ext(asset)

raster_ext.bands=raster_bands

assets=item.add_asset(
    key='utilisation-territoire-2018', 
    asset=asset
)

ProjectionExtension.add_to(item)
proj_ext=ProjectionExtension.ext(item)
proj_ext.epsg=32198

catalog.add_item(item)

catalog.normalize_hrefs(os.path.join('.', 'stac'))
catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)



session = boto3.session.Session()

s3_res = boto3.client(
    service_name='s3',
    aws_access_key_id='NJBPPQZX7PFUBP1LH8B0',
    aws_secret_access_key=os.getenv('ARBUTUS_S3_SECRET'),
    endpoint_url='https://object-arbutus.cloud.computecanada.ca',
    use_ssl=True,
)


