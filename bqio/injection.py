import sys
sys.path.append('./bqio/')

from lib import utils

#make sure to change to the real catalog  path configgit
folder_parent_path = "......./io-data"
folder_name = "catalogs/stac13/stac"
api_host = "https://io.biodiversite-quebec.ca/stac-fast-api"
utils.push_json_to_api(folder_parent_path,folder_name, api_host)

