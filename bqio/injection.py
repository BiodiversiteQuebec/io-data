import sys
sys.path.append('./bqio/')

from lib import utils

folder_path = "......./io-data"
utils.push_json_to_api(folder_path,"catalogs/stac13/stac", "https://io.biodiversite-quebec.ca/stac-fast-api")

