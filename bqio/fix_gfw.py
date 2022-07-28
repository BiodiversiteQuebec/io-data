import pystac
import pystac_client
import sys
from lib.utils import push_to_api

catalog = pystac_client.Client.open("https://io.biodiversite-quebec.ca/stac/")
search = catalog.search(collections=["gfw-treecover2000"])
items=search.get_all_items()
for it in range(1,len(items)+1):
    items[it].assets['data']=items[it].assets[items[it].id]
    del items[it].assets[items[it].id]
    items[it].properties['proj:epsg']=4326
    del items[it].properties['proj:wkt2']
    push_to_api(items[it],'https://io.biodiversite-quebec.ca/stac/')
