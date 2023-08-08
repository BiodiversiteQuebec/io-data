# io-data

Basic tools for creating STAC items and catalogs for IO repository of geospatial data in Biodiversité Québec

This repository contains:

1. A Python library in /bqio for loading raster data into the STAC catalog
2. An experimental stacItem Pipeline API for sending rasters directly to an API endpoint for automated ingestion into the STAC catalog.

#### STAC-FASTAPI

At the moment, the STAC API is generated from the generic STAC-FASTAPI/PGSTAC Docker image https://github.com/ReseauBiodiversiteQuebec/stac-fastapi. A functioning nginx configuration section is in nginx-stac-endpoint.txt

The db-backup.sh file contains the script to backup the database through regular CRON jobs.

#### Python STAC ingestion library

The Python library located in /bqio is used to

1. Take local or remote files and convert them into Cloud optimized Geotiffs using gdalwarp.
2. Send the COGs to the Digital Research Alliance object storage using S3 tools.
3. Extract information from the COGs to populate the information for the STAC items.
4. Create collections and items using the pystac Python library and send them through POST requests to STAC FASTAPI.

There are a number of example ingestion scripts located in /bqio/datasets/. Note that older scripts were using an older version of the library. These scripts were run in a Docker container on a VM with sufficient resources for the COG conversion and data download/upload to proceed. Some of theses scripts take several days to run.

#### EXPERIMENTAL stacItem Pipeline API

`StacItemPipeline` API allows user to send new stac items to an existing stac collection.
A simple flask api has been used to expose some endpoints that make the injection possible.

#### endpoints:

`{api_url}/newitem` : POST request that allows to inject the new item.
`body`: a json object with the following format:

```javascript
{ "collection_id":"id of the collection where item will be inserted",
"date":"2018-01-01",
"name":"name of the item",
"filename":"filename.tif",
"stac_api_server":"<url_stac_api>",
"file_source_host":"<url_to_save_cog_file>",
"properties" : { "full_filename": "full_filename.tif",
		"description": "Description of the item",
		"otherparams...."
		}
}
```

return : json object with id of the process of your item and a message (received means that the server already have your item in the queue waiting to be processed).

```javascript
{
  "id": "c1705f50-029c-4502-a2b6-9ffd1e8876d4",
  "msg": "received"
}
```

`{url}/status?id=c1705f50-029c-4502-a2b6-9ffd1e8876d4`: GET request to verify the status of the process with the given `id`.

return: json

case where process finished properly:

```javascript
 {
    "_description": "description of diferent steps of the process",
    "_id": "c1705f50-029c-4502-a2b6-9ffd1e8876d4",
    "_operation": "PROCESS FINISHED",
    "_param": {
      "collection_id": "collection_id",
      "date": "2018-01-01",
      "file_source_host": "url(location of the source .tiff file)",
      "filename": "filename.tif",
      "name": "item name",
      "properties": {
        "datetime": "2018-01-01T00:00:00Z",
        "description": "TTT Other Hansen 2020",
        "full_filename": "full_filename.tif",
       "other propertis...."
      },

      "other propertis...."
    },
    "_status": "ok"
  }
```

case of failure:

```javascript
{
    "_description": "Unable to read collection: \"chelsa-clim\" from server, error \n: <urlopen error [Errno 111] Connection refused>. \n Please check your conexion or congif.",
   "_id": "c1705f50-029c-4502-a2b6-9ffd1e8876d4",
    "_operation": "GETCOLLECTION",
    "_param": {
      "collection_id": "collection_id",
      "date": "2018-01-01",
      "file_source_host": "url(location of the source .tiff file)",
      "filename": "filename.tif",
      "name": "item name",
      "properties": {
        "datetime": "2018-01-01T00:00:00Z",
        "description": "TTT Other Hansen 2020",
        "full_filename": "full_filename.tif",
       "other propertis...."
      },

      "other propertis...."
    },
    "_status": "error"
  }
```

`{api_url}/status/all`: GET request that return a list of all item sent to the API.

return: list of json object with the same format of the preview ones.

#### Docker config for stacItem Pipeline

Create first an environment variable file (.env) with the following variables:

- `ARBUTUS_OBJECT_ACCESS_ID=...`
- `ARBUTUS_OBJECT_ACCESS_KEY=....`
- `API_PORT=...`
- `API_HOST=0.0.0.0`
- `STAC_API_HOST=..url..`

note: if the container is running in the same network as the STAC API server container, you might need to use the api address in the `STAC_API_HOST` variable ex:
`STAC_API_HOST=STAC_API_HOST=http://172.21.0.3:8082`.
To get the IP addres of your container run this command:

`docker inspect -f '{{.NetworkSettings.Networks.[network].IPAddress}}' [container name]`

run in the cmd:

- `docker-compose -f docker-compose-api.yml up --build` only first time to build the image.
- `docker-compose -f docker-compose-api.yml up gdal-api-python`

note: ake sure the stac api server is running and accesible.

### Database Backup

Every day for the last 30 days a catalogdb database's backup is created and stored in cloud server. This process is automatically triggered once a day.

### Restore a Backup

Our backups are store in the cloud server (s3). In order to restore a database you need to do the following steps:

- Download the backup file from the cloud server ( since it is S3 in our case make sure your computer is configured so it can connect to the S3)
- unzip the backup file.
- copy the file `docker-compose-io.yml` inside the stac-fastapi repo folder in the server.
- Run the command `docker-compose -f docker-compose-io.yml up` inside the stac-fastapi repo folder in the server.
- move backup file to the backup folder inside the docker container.
- run `docker exec -it stac-db psql` in the server to run the postgresql in the container.
- Create a new database ` create database newDB`;
- Restore the backup file in the newDB by : `psql -d newBD < backupfile.sql`.
- Drop the catalogdb databse inside the container (there are conflicts if we restore directly in catalogdb) by: `drop database catalogdb`.
- Rename the database `newDB` to `catalogdb`;
- Restart containers one more time by: `docker-compose -f docker-compose-io.yml up`.
