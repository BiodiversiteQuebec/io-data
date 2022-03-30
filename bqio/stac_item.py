import pystac
import os
from pystac.extensions.raster import RasterBand
from pystac.extensions.raster import RasterExtension
from pystac.extensions.projection import ProjectionExtension
from datetime import datetime
import rasterio
from shapely.geometry import Polygon, mapping



def stac_create_item(file_path, file_url, name, datetime, collection, properties={}, units=''):
	
	bbox, footprint, crs, resolution, dtype = get_raster_metadata(file_path)
	asset=pystac.Asset(
	    href=file_url, 
	    media_type=pystac.MediaType.COG
	)
	raster_bands = [RasterBand.create(
			spatial_resolution=resolution,
			unit=units,
			data_type=dtype
		)
	]
	raster_ext=RasterExtension.ext(asset)
	raster_ext.bands=raster_bands

	item = pystac.Item(id=name,
				geometry=footprint,
				bbox=bbox,
				datetime=datetime,
				properties=properties,
				collection=collection,
			)

	assets=item.add_asset(
	    key=name, 
	    asset=asset
	)

	ProjectionExtension.add_to(item)
	proj_ext=ProjectionExtension.ext(item)
	if(crs.isnumeric()):
		proj_ext.epsg=crs
	else:
		proj_ext.epsg=None
		proj_ext.wkt2=crs
	item.set_self_href('./'+collection.id+'/'+name+'.json')
	return item


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
        if (ds.meta['crs'].to_epsg() == None):
        	crs=ds.meta['crs'].to_string()
        else:
        	crs=ds.meta['crs'].to_epsg()

        pixelSizeX, pixelSizeY  = ds.res
        return (bbox, mapping(footprint), crs, pixelSizeX, ds.meta['dtype'])





