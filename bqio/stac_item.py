import pystac
import os
from pystac.extensions.rasters import RasterBand
from pystac.extensions.rasters import RasterExtension
from pystac.extensions.projection import ProjectionExtension
import boto3
from datetime import datetime
import rasterio
from shapely.geometry import Polygon, mapping



def stac_create_item(catalog, img_path, name):
	
	bbox, footprint, crs, resolution, dtype = get_raster_metadata(img_path)
	asset=pystac.Asset(
	    href="https://object-arbutus.cloud.computecanada.ca/bq-io/"+name+".tif", 
	    media_type=pystac.MediaType.GEOTIFF
	)
	raster_ext=RasterExtension.ext(asset)
	raster_ext.bands=raster_bands
	assets=item.add_asset(
	    key=name, 
	    asset=asset
	)

	ProjectionExtension.add_to(item)
	proj_ext=ProjectionExtension.ext(item)
	proj_ext.epsg=crs

	raster_bands = [RasterBand.create(
			spatial_resolution=resolution,
			unit='m',
			data_type=dtype
		)
	]

	item = pystac.Item(id=name,
				geometry=footprint,
				bbox=bbox,
				datetime=datetime.utcnow(),
				properties={}
			)



def get_raster_metadata(raster_uri):
    with rasterio.open(raster_uri) as ds:
        bounds = ds.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        pixelSizeX, pixelSizeY  = raster.res
        return (bbox, mapping(footprint), raster.meta.crs, pixelSizeX, raster.meta.dtype)





