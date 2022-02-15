library("gdalcubes")
library("rstac")
library("tibble")

s = stac("http://io.biodiversite-quebec.ca/stac/")

it_obj <- s |>
  stac_search(bbox=c(-120,30,-40,68), collections=c('chelsa-clim'),limit=5000) |> get_request()

st<-stac_image_collection(it_obj$features,asset_names=c("bio2"))
st

v = cube_view(srs = "EPSG:32198",  extent = list(t0 = "1981-01-01", t1 = "1981-01-31",
                                                 left = -2009488, right = 1401061,  top = 2597757, bottom = -715776),
              dx = 2000, dy = 2000, dt = "P1Y",aggregation = "mean", resampling = "near")

gdalcubes_options(threads = 4)

raster_cube(st, v, chunking = c(1, 500, 500)) |> plot()

