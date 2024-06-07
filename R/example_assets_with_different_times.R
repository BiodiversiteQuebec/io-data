library(gdalcubes)
library(rstac)
library(stringr)

# THIS EXAMPLE SHOWS HOW TO CALCULATE THE DIFFERENCE BETWEEN
# TWO RASTERS THAT HAVE THE SAME ASSET NAME, BUT DIFFERENT DATETIMES

s_obj <- stac("https://io.biodiversite-quebec.ca/stac/")
it_obj <- s_obj |>
  stac_search(collections = "fragmentation-rmf") |>
  post_request()

v <- cube_view(srs = "EPSG:4326", extent = list(t0 = "1992-01-01", t1 = "1998-01-01",
                                                left = -180, right =180, top = 90, bottom = -90),
               dx=0.25, dy=0.25, dt="P1Y",
               aggregation = "mean",
               resampling = "near")

st <-stac_image_collection(it_obj$features,asset_names=c('data'),property_filter=function(s){s[['year']]==1992})
r_cube_1992 <- raster_cube(st, v)

st <-stac_image_collection(it_obj$features,asset_names=c('data'),property_filter=function(s){s[['year']]==1998})
r_cube_1998 <- raster_cube(st, v)

s1992 <- r_cube_1992 |> reduce_time('mean(data)')

s1998 <- r_cube_1998 |> reduce_time('mean(data)')

jb<-join_bands(c(s1992,s1998))

jb<-jb |> rename_bands(X1.data_mean="y1992", X2.data_mean="y1998")

diff <- jb |> apply_pixel("y1998-y1992")

plot(diff)
