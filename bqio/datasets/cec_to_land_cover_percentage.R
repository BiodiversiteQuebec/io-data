library(gdalcubes)
library(rstac)
s_obj <- stac("https://io.biodiversite-quebec.ca/stac/")
it_obj <- s_obj |>
  collections("cec_land_cover") |>
  items("cec_land_cover_2020") |> get_request()
it_obj
coll <- stac_image_collection(list(it_obj),asset_names='data')
bbox <- it_obj$bbox
v = cube_view(extent=list(left=bbox[1], right=bbox[3], 
                          bottom=bbox[2], top=bbox[4], t0="2020-01-01", t1="2020-01-01"),
              srs=it_obj$properties$`proj:wkt2`, dx = 30, dy=30, dt="P1D", resampling="mode")

CEC.cube = raster_cube(coll, v) 
gdalcubes_options(parallel=TRUE)
classes<-list("1"=c(1,2),"2"=c(3,4,5),"3"=c(6),"4"=c(7,8),"5"=c(9,10),"6"=c(11,12,13),"7"=c(14),"8"=c(15),"9"=c(16),"10"=c(17),"11"=c(18),"12"=c(19))
for (c in seq(14,19)){
  CEC_c <- apply_pixel(CEC.cube,FUN=function(x) {
       x["data"] %in% c 
   },load_env=TRUE) |> aggregate_space(300,300,method="mean")
  CEC_c |> write_tif('/bqio/CEC/',paste0('CEC_land_cover_percent_class',c,'_'),COG=TRUE,creation_options=list('COMPRESS'='DEFLATE'))
}
