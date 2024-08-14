import boto3
import os
from lib import utils

def create_s3_res():
	
	return boto3.client(
	    service_name='s3',
	    aws_access_key_id=utils.getenv('ARBUTUS_OBJECT_ACCESS_ID'),
	    aws_secret_access_key=utils.getenv('ARBUTUS_OBJECT_ACCESS_KEY'),
	    endpoint_url='https://object-arbutus.cloud.computecanada.ca',
	    use_ssl=True,
	)

def upload_tiff_to_io(file_path, file_name, folder):
	s3_client = create_s3_res()
	dest = folder+'/'+file_name.strip(' ')
	try:
		response = s3_client.upload_file(file_path, 'bq-io', dest, ExtraArgs={'ACL': 'public-read'})
	except:
		print('There was an error uploading to IO.')
		return False
	print('Uploaded to IO!')
	return 'https://object-arbutus.cloud.computecanada.ca/bq-io/'+dest

def upload_stac_to_io(stac_path):
	s3_client = create_s3_res()
	try:
		for root,dirs,files in os.walk(stac_path):
			for file in files:
				response = s3_client.upload_file(os.path.join(root,file),'bq-io','stac/'+root, ExtraArgs={'ACL': 'public-read'})
	except:
		print('There was an error uploading to IO.')
		return False
	print('STAC catalog updated in cloud!')

