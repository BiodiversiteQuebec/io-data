# Franklin Docker environment for the IO Stac catalog

To run: 

````{bash}
docker-compose run franklin import-catalog --catalog-root /opt/franklin/stac/catalog.json
docker-compose up -d franklin 
````