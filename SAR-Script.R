library(terra)
library(raster)
library(sp)
library(dplyr)

#call in vv/vh SAR data with rast function
vv.vh <- rast("D:/422/VH_VV.tif")
ReSamp <- vv.vh
values(ReSamp) <- 0
#call in lidar
lidar.SD <- rast("D:/422/LiDAR_derived_snow_depth_ACO_CHRL_2021_P1.tif")

#call in points that represent the center of each SAR pixel 
p <- vect("D:/422/SAR-Points2.shp")

#extract the sAR values from under the points
backscatter<- as.data.frame(extract(vv.vh, p))

#resample the LiDAR snow depth to the res of the SAR data (10m)
r <- resample(lidar.SD, ReSamp)

#extract the snow depth values from under the sAR pixels via the points
snowdepth <- as.data.frame(extract(r, p))
names(snowdepth) <- c("ID", "snowdepth")


#join the backscatter and snow depth dataframes
SAR.Snow <- bind_cols(backscatter, snowdepth)
names(SAR.Snow) <- c("ID1", "VV_VH", "ID2", "SnowDepth")

SAR.Snow <- select(SAR.Snow, c("VV_VH", "SnowDepth"))

SAR.Snow <- na.omit(SAR.Snow)
