# io-data

Basic pipeline for creating STAC catalog for IO repository of geospatial data in Biodiversité Québec

#### stacItem Pipeline API

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

`ARBUTUS_OBJECT_ACCESS_ID=...`
`ARBUTUS_OBJECT_ACCESS_KEY=....`
`API_PORT=...`
`API_HOST=0.0.0.0`
`STAC_API_HOST=..url..`

note: if the container is running in the same network as the STAC API server container, you might need to use the api address in the `STAC_API_HOST` variable ex:
`STAC_API_HOST=STAC_API_HOST=http://172.21.0.3:8082`.
To get the IP addres of your container run this command:

`docker inspect -f '{{.NetworkSettings.Networks.[network].IPAddress}}' [container name]`

run in the cmd:

- `docker-compose -f docker-compose-api.yml up --build` only first time to build the image.
- `docker-compose -f docker-compose-api.yml up gdal-api-python`

note: ake sure the stac api server is running and accesible.
