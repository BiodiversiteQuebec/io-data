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

        spatial_extent = pystac.SpatialExtent(bboxes=[[-81.68, -4.24, -66.55, 12.90]])
        temporal_extent = pystac.TemporalExtent(
            intervals=[
                [
                    datetime.fromisoformat("2000-01-01"),
                    datetime.fromisoformat("2020-12-31"),
                ]
            ]
        )
        collection_extent = pystac.Extent(
            spatial=spatial_extent, temporal=temporal_extent
        )
        collection_id = "colombia-lc"
        collection_title = "Colombian land cover time series"
        collection_description = (
            "A raster representation of the Colombian land cover data"
        )
        collection_license = "CC-BY-NC-4.0"
        collection_folder = "colombia-lc"
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
                "layer_name": "colombia_cobertura_tierra_2000_2002",
                "description": "Colombia Land Cover - 30m - 2000-2002",
                "year": "2000-2002",
            },
            {
                "layer_name": "colombia_cobertura_tierra_2005_2009",
                "description": "Colombia Land Cover - 30m - 2005-2009",
                "year": "2005-2009",
            },
            {
                "layer_name": "colombia_cobertura_tierra_2010_2012",
                "description": "Colombia Land Cover - 30m - 2010-2012",
                "year": "2010-2012",
            },
            {
                "layer_name": "colombia_cobertura_tierra_2018",
                "description": "Colombia Land Cover - 30m - 2018",
                "year": "2018",
            },
        ]
        for v in vars:
            filename = v["layer_name"] + ".tif"
            name = v["layer_name"]
            path = "/bqio/colombia-lc/" + v["layer_name"] + ".tif"
            properties = {"description": v["description"], "year": v["year"]}
            newItem: ThisStacItem = ThisStacItem(
                name,
                filename,
                datetime.fromisoformat(v["year"].split("-")[0] + "-01-01"),
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
