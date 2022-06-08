FROM osgeo/gdal:alpine-normal-3.4.3
RUN apk add --no-cache gcc linux-headers python3 py3-pip musl-dev g++ python3-dev bash R R-dev proj-dev proj
RUN pip install pystac==1.3.0 boto3 rasterio shapely python-decouple flask