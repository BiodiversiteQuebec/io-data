FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.0
RUN apt update && apt install python-is-python3 python3-pip -y r-base 
#RUN apt  add --no-cache gdal-python py3-boto3 py3-rasterio gdal-dev py3-numpy py3-gdal-pyc
#RUN apk add geos gcc geos-dev
RUN pip install shapely python-decouple pystac --break-system-packages 
RUN pip install requests rasterio numpy boto3 --break-system-packages
#RUN apk add --no-cache git
#RUN apk add sqlite-libs
RUN apt install libcurl4-openssl-dev
RUN R -e "install.packages(c('pak'))"
RUN R -e "pak::pak(c('gdalcubes','rstac','sf','terra','dplyr','ggplot2'))"
