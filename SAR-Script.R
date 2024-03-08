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
backscatter<- as.data.frame(extract(vv.vh, p, cells=TRUE, xy=TRUE))

#resample the LiDAR snow depth to the res of the SAR data (10m)
r <- resample(lidar.SD, ReSamp)

#extract the snow depth values from under the sAR pixels via the points
snowdepth <- as.data.frame(extract(r, p, cells=TRUE, xy=TRUE))



#join the backscatter and snow depth dataframes
SAR.Snow <- bind_cols(backscatter, snowdepth)
SAR.Snow <- merge(backscatter, snowdepth, by=c("x", "y"))

SAR.Snow <- select(SAR.Snow, c("VH_VV", "LiDAR_derived_snow_depth_ACO_CHRL_2021_P1"))
names(SAR.Snow) <- c("VH_VV", "SnowDepth")

plot(SAR.Snow$VH_VV, SAR.Snow$SnowDepth)
SAR.Snow <- na.omit(SAR.Snow)
SAR.Snow <- subset(SAR.Snow, SnowDepth > 0)

Snow10.20 <- subset(SAR.Snow, SnowDepth < 0.5)
plot(Snow10.20$VH_VV)
plot(Snow10.20$SnowDepth)

Snow10.20$VH_VV <- Snow10.20$VH_VV/(max(Snow10.20$VH_VV))
Snow10.20$SnowDepth <- Snow10.20$SnowDepth/(max(Snow10.20$SnowDepth))

T<- lm(VH_VV ~ SnowDepth, Snow10.20)
plot(Snow10.20)
