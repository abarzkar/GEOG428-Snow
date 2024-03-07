library(terra)
library(raster)
library(sp)
vv.vh <- rast("D:/422/VH_VV.tif")

lidar.SD <- rast("D:/422/LiDAR_derived_snow_depth_ACO_CHRL_2021_P1.tif")

r <- vv.vh
values(r) <- 0

p <- rasterToPoints(raster(r))


