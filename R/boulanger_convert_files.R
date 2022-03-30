library(stars)
tools::file_path_as_absolute()
fi<-list.files('./','.RData',include.dirs=TRUE)
for (f in fi){
  fname_ext=basename(f)
  fname=tools::file_path_sans_ext(fname_ext)
  load(f)
  r3<-stars::st_transform(st_as_stars(MergedRasters), crs('EPSG:3857'))
  write_stars(r3,paste0(fname,'.tif'),driver='COG',options=c("COMPRESS=DEFLATE","NUM_THREADS=6"))
}
