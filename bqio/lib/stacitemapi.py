import traceback
import sys
sys.path.append('./bqio/')

from lib.utils import upload_file_to_s3, push_to_api, getenv
from lib.stacitempipeline import ItemsPipeline
import flask, threading
from flask import request, jsonify

#stac_api_host = "https://io.biodiversite-quebec.ca/stac" # host where stac api is running

pipeline = ItemsPipeline()
pipeline.setPushItemToApiFn(push_to_api)
pipeline.setPushCOGToServerFn(upload_file_to_s3)

app = flask.Flask(__name__)
app.config["DEBUG"]

@app.route('/', methods=['GET'])
def home():
    return "<h1>SDM API for item injections</h1><p>Items</p>"

@app.route('/status', methods=['GET'])
def getstatus():
	params = request.args
	id = params["id"]
	log  = pipeline.get_log_by_id(id)
	return log.__dict__

@app.route('/resume', methods=['GET'])
def resume():
	params = request.get_json()
	id = params["id"]
	itemparams =  params["params"]
	#asyncio.run(pipeline.resume(id,params))
	return jsonify("sent")

@app.route('/status/all', methods=['GET'])	
def getStatusAll():
	logs = pipeline.getlogs()
	return jsonify(logs)

@app.route('/newitem', methods=['POST'])
def add_item_to_collections():
	params = request.get_json()
	res = pipeline.add_item_to_collection(params)
	return jsonify(res)

pipeline_thread = threading.Thread(target=pipeline.run, daemon=True)
#

try:
	pipeline_thread.start()
	
except Exception as err:
	print(traceback.format_exc()) 

port = getenv('API_PORT') 
host = getenv('API_HOST')
app.run(host=host, port=port )