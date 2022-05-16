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


###
it_obj <- s |>
  stac_search(bbox=c(-120,30,-40,68), collections=c('esacci-lc'),limit=5000) |> get_request()

assets=unlist(lapply(it_obj$features,function(x){names(x$assets)}))

lc2020 = stac_image_collection(it_obj$features,asset_names=assets)
#,                                   property_filter = function(x) { x[["year"]] == '2020'})

lc2020
v = cube_view(srs = "EPSG:32198",  extent = list(t0 = "2020-01-01", t1 = "2020-01-01",
                                                 left = -2009488, right = 1401061,  top = 2597757, bottom = -715776),
              dx = 2000, dy = 2000, dt = "P1D",aggregation = "mean", resampling = "near")

gdalcubes_options(threads = 4)

raster_cube(lc2020, v) |> plot()


it_obj=rstac::stac("http://io.biodiversite-quebec.ca/stac/") |> rstac::stac_search(bbox = c(-73,45,-60,60), collections = c('soilgrids'),limit = 1000) |> rstac::get_request()


st<-gdalcubes::stac_image_collection(it_obj$features,asset_names=c("cec_5-15cm"))
st

v = cube_view(srs = "EPSG:32198",  extent = list(t0 = "2016-07-04", t1 = "2016-07-04",
                                                 left = -2009488, right = 1401061,  top = 2597757, bottom = -715776),
              dx = 1000, dy = 1000, dt = "P1D")

gdalcubes_options(parallel = TRUE)

raster_cube(st, v) |> plot()



it_obj=rstac::stac("https://io.biodiversite-quebec.ca/stac/") |> rstac::stac_search(bbox = c(-73,45,-60,60), collections = c('chelsa-monthly'),limit = 5000) |> rstac::get_request()

assets=unlist(lapply(it_obj$features,function(x){names(x$assets)}))

tas = gdalcubes::stac_image_collection(it_obj$features,asset_names=assets,property_filter = function(x) { x[["variable"]] == 'tas'})



v = gdalcubes::cube_view(srs = "EPSG:32198",  extent = list(t0 = "2016-07-01", t1 = "2016-07-31",
                                                 left = -2009488, right = 1401061,  top = 2597757, bottom = -715776),
              dx = 1000, dy = 1000, dt = "P1M",aggregation = "mean", resampling = "near")

gdalcubes::gdalcubes_options(parallel = TRUE)

gdalcubes::raster_cube(tas, v) |> plot()


