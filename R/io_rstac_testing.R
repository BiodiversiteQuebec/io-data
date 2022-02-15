library("gdalcubes")
library("rstac")
library("tibble")

s = stac("http://io.biodiversite-quebec.ca/stac/")

it_obj <- s |>
  stac_search(bbox=c(-120,30,-40,68), collections=c('chelsa-clim-proj'),limit=5000) |> get_request()

assets=unlist(lapply(it_obj$features,function(x){names(x$assets)}))

bio12_4170 = stac_image_collection(it_obj$features,asset_names=assets,
                                 property_filter = function(x) {x[["variable"]] == 'bio12' & x[["time_span"]] == '2041-2070'  & x[["rcp"]] == 'ssp585'})

bio12_4170

v = cube_view(srs = "EPSG:32198",  extent = list(t0 = "2041-01-01", t1 = "2041-01-01",
                                                 left = -2009488, right = 1401061,  top = 2597757, bottom = -715776),
              dx = 2000, dy = 2000, dt = "P1Y",aggregation = "mean", resampling = "near")

gdalcubes_options(threads = 4)

raster_cube(bio19_4170, v) |> plot()



###
it_obj <- s |>
  stac_search(bbox=c(-120,30,-40,68), collections=c('chelsa-clim'),limit=5000) |> get_request()

st<-stac_image_collection(it_obj$features,asset_names=c("bio1"))
st

v = cube_view(srs = "EPSG:32198",  extent = list(t0 = "1981-01-01", t1 = "1981-01-31",
                                                 left = -2009488, right = 1401061,  top = 2597757, bottom = -715776),
              dx = 2000, dy = 2000, dt = "P1Y",aggregation = "mean", resampling = "near")

gdalcubes_options(threads = 4)

raster_cube(st, v) |> plot()

