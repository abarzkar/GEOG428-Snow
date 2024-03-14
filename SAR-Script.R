library(terra)
library(dplyr)


Lidar <- rast("D:/422/LiDAR_derived_snow_depth_ACO_CHRL_2021_P1.tif")

RCM <- rast("D:/422/HV.HH-Clipped-20210308.tif")

Lidar <- project(Lidar, RCM)


Lidar50 <- resample(Lidar, RCM, method="bilinear")
plot(Lidar50)
writeRaster(Lidar50, "D:/422/LiDAR_50.tif", overwrite=TRUE)
points <- vect("D:/422/SAR-Points/SAR-Points3.shp")

sd <- as.data.frame(extract(Lidar50, points))
names(sd) <- c("ID", "Snowdepth")
head(sd)


bs <- as.data.frame(extract(RCM, points))
names(bs) <- c("ID", "Backscatter")
head(bs)

df <- bind_cols(sd, bs)
SAR_Snow <- dplyr::select(df, "Snowdepth", "Backscatter")

SAR_Snow <- dplyr::filter(SAR_Snow, Backscatter<25)
SAR_Snow <- dplyr::filter(SAR_Snow, Backscatter>0)
SAR_Snow <- dplyr::filter(SAR_Snow, Snowdepth>0.3)
SAR_Snow <- dplyr::filter(SAR_Snow, Snowdepth<10)

plot(SAR_Snow$Snowdepth, SAR_Snow$Backscatter)
