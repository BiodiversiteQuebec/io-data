import pystac
from datetime import datetime
import tempfile
from pathlib import Path
import urllib.request
import traceback
import csv
import sys

sys.path.append("/bqio/")
from lib.utils import upload_file_bq_io, push_to_api
from lib.pipelinelib import StacItem, Collection, BqIoStacPipeline
from pathlib import Path


class ThisStacItem(StacItem):

    # example of getting source tiff file from local path
    def getItemFile(self):

        try:
            self._tiff_local_file_location = Path(self._file_source_location)
        except Exception as err:
            print(
                "Oops!  There was an error downloading the file: "
                + format(err)
                + "\n"
                + traceback.format_exc()
            )
            pass

        return


class ThisCollection(Collection):
    def createCollection(self):
        """Overrides the implementation of createCollection from Parent class (Collection)"""

        spatial_extent = pystac.SpatialExtent(bboxes=[[-84, 43.5, -53, 63.5]])
        temporal_extent = pystac.TemporalExtent(
            intervals=[
                [
                    datetime.fromisoformat("2022-10-01"),
                    datetime.fromisoformat("2022-10-01"),
                ]
            ]
        )
        collection_extent = pystac.Extent(
            spatial=spatial_extent, temporal=temporal_extent
        )
        collection_id = "qc_pilot_env"
        collection_title = (
            "Environmental layers for the Quebec pilot BON optimization project."
        )
        collection_description = (
            "Environmental layers for the Quebec pilot BON optimization project."
        )
        collection_license = "CC-BY-NC-4.0"
        collection_folder = "qc_pilot_env"
        collection = self.createCollectionFromParams(
            collection_title=collection_title,
            collection_description=collection_description,
            collection_license=collection_license,
            spatial_extent=spatial_extent,
            temporal_extent=temporal_extent,
            collection_extent=collection_extent,
            collection_id=collection_id,
            collection_folder=collection_folder,
        )

        return collection

    def createItemList(self):
        vars = [
            {
                "layer_name": "backward_velocity",
                "Description": "Backward_velocity: the distance from projected future climate cells back to analogous current climate locations, using methods from Carroll et. al. (2015) and Hamann et. al. (2014)",
            },
            {
                "layer_name": "climate_rarity",
                "Description": "Climate rarity: how rare is a pixel (e.g., mean temperature) compare to its surrounding pixels, using a moving window and a matching threshold",
            },
            {
                "layer_name": "forward_velocity",
                "Description": "Forward_velocity: he distance from current climate locations to the nearest site with an analogous future climate, using methods from Carroll et. al. (2015) and Hamann et. al. (2014)",
            },
            {
                "layer_name": "lc_prop_y2000_class0",
                "Description": "Land cover proportion (ESA, year 2000): class = 0 (No Data)",
            },
            {
                "layer_name": "lc_prop_y2000_class10",
                "Description": "Land cover proportion (ESA, year 2000): class = 10 (Cropland, rainfed)",
            },
            {
                "layer_name": "lc_prop_y2000_class20",
                "Description": "Land cover proportion (ESA, year 2000): class = 20 (Cropland, irrigated or pot-flooding)",
            },
            {
                "layer_name": "lc_prop_y2000_class30",
                "Description": "Land cover proportion (ESA, year 2000): class = 30 (Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (<50%))",
            },
            {
                "layer_name": "lc_prop_y2000_class40",
                "Description": "Land cover proportion (ESA, year 2000): class = 40 (Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (<50%))",
            },
            {
                "layer_name": "lc_prop_y2000_class50",
                "Description": "Land cover proportion (ESA, year 2000): class = 50 (Tree cover, broadleaved, evergreen, closed to open (>15%))",
            },
            {
                "layer_name": "lc_prop_y2000_class60",
                "Description": "Land cover proportion (ESA, year 2000): class = 60 (Tree cover, broadleaved, deciduous, closed to open (>15%) )",
            },
            {
                "layer_name": "lc_prop_y2000_class70",
                "Description": "Land cover proportion (ESA, year 2000): class = 70 (Tree cover, needleleaved, evergreen, closed to open (>15%))",
            },
            {
                "layer_name": "lc_prop_y2000_class80",
                "Description": "Land cover proportion (ESA, year 2000): class = 80 (Tree cover, needleleaved, deciduous, closed to open (>15%))",
            },
            {
                "layer_name": "lc_prop_y2000_class90",
                "Description": "Land cover proportion (ESA, year 2000): class = 90 (Tree cover, mixed leaf type (broadleaved and needleleaved))",
            },
            {
                "layer_name": "lc_prop_y2000_class100",
                "Description": "Land cover proportion (ESA, year 2000): class = 100 (Mosaic tree and shrub (>50%) / herbaceous cover (<50%))",
            },
            {
                "layer_name": "lc_prop_y2000_class110",
                "Description": "Land cover proportion (ESA, year 2000): class = 110 (Mosaic herbaceous cover (>50%) / tree and shrub (<50%))",
            },
            {
                "layer_name": "lc_prop_y2000_class120",
                "Description": "Land cover proportion (ESA, year 2000): class = 120 (Shrubland)",
            },
            {
                "layer_name": "lc_prop_y2000_class130",
                "Description": "Land cover proportion (ESA, year 2000): class = 130 (Grassland)",
            },
            {
                "layer_name": "lc_prop_y2000_class140",
                "Description": "Land cover proportion (ESA, year 2000): class = 140 (Lichens and mosses)",
            },
            {
                "layer_name": "lc_prop_y2000_class150",
                "Description": "Land cover proportion (ESA, year 2000): class = 150 (Sparse vegetation (tree, shrub, herbaceous cover) (<15%))",
            },
            {
                "layer_name": "lc_prop_y2000_class160",
                "Description": "Land cover proportion (ESA, year 2000): class = 160 (Tree cover, flooded, fresh or brakish water)",
            },
            {
                "layer_name": "lc_prop_y2000_class170",
                "Description": "Land cover proportion (ESA, year 2000): class = 170 (Tree cover, flooded, saline water)",
            },
            {
                "layer_name": "lc_prop_y2000_class180",
                "Description": "Land cover proportion (ESA, year 2000): class = 180 (Shrub or herbaceous cover, flooded, fresh/saline/brakish water)",
            },
            {
                "layer_name": "lc_prop_y2000_class190",
                "Description": "Land cover proportion (ESA, year 2000): class = 190 (Urban areas)",
            },
            {
                "layer_name": "lc_prop_y2000_class200",
                "Description": "Land cover proportion (ESA, year 2000): class = 200 (Bare areas)",
            },
            {
                "layer_name": "lc_prop_y2000_class210",
                "Description": "Land cover proportion (ESA, year 2000): class = 210 (Water bodies)",
            },
            {
                "layer_name": "lc_prop_y2000_class220",
                "Description": "Land cover proportion (ESA, year 2000): class = 220 (Permanent snow and ice)",
            },
            {
                "layer_name": "local_velocity",
                "Description": "Local velocity is a measure of the local rate of displacement of climatic conditions over Earth�s surface, using  Loarie et. al. (2009) and  Sandel et. al . (2011) appoaches",
            },
            {
                "layer_name": "water_binary_masktif",
                "Description": "Proportion of water bodies (250m pixels within 1000m pixel)",
            },
            {
                "layer_name":"wpda_QC_terr2022",
                "Description": "Proportion of Protected Areas -TERRESTRIAL within 1000 pixel, using exactextractr::coverage_fraction() function (Source: https://www.protectedplanet.net/en/thematic-areas/wdpa?tab=WDPA Accessed: Sep2022)",
            },
            {
                "layer_name":"accessibility",
                "Description": "Global travel time to cities  to nearest city to assess inequalities in accessibility in 2015 (Source: https://data.malariaatlas.org/maps)",
            },
        ]
        for v in vars:
            filename = v["layer_name"] + ".tif"
            name = v["layer_name"]
            path = "/bqio/qc_pilot_env/layers/" + v["layer_name"] + ".tif"
            properties = {
                "full_filename": filename,
                "layer": v["layer_name"],
                "description": v["Description"],
            }
            newItem: ThisStacItem = ThisStacItem(
                name,
                filename,
                datetime.fromisoformat("2022-10-01"),
                properties,
                path,
                "raw",
                False,
            )
            self.getItemList().append(newItem)

        return


thisCollection: ThisCollection = ThisCollection()

# params to create links of stac items for this collection
host: str = "https://object-arbutus.cloud.computecanada.ca/bq-io/io"  # host name of the server stac will be located
# stac_api_host = "http://localhost:8082" # host where stac api is running
stac_api_host = (
    "https://io.biodiversite-quebec.ca/stac/"  # host where stac api is running
)

pipeline: BqIoStacPipeline = BqIoStacPipeline()
pipeline.setS3UploadFunc(upload_file_bq_io)
pipeline.setPushToApiFunc(push_to_api, stac_api_host)
pipeline.run(thisCollection, host)
