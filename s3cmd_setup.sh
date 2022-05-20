
s3cmd --configure

#use_https = True
#host_base = object-arbutus.cloud.computecanada.ca:443
#host_bucket = object-arbutus.cloud.computecanada.ca:443
#access_key = <YOUR KEY HERE>
#secret_key = <YOUR KEY HERE>
#signature_v2 = True

s3cmd mb s3://bq-io
s3cmd setacl s3://bq-io --acl-public
s3cmd setcors corsrules.xml s3://bq-io


#upload STAC 
s3cmd put --recursive stac s3://bq-io
s3cmd setacl --recursive s3://bq-io/stac --acl-public