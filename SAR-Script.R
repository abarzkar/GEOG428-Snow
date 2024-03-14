library(terra)
library(dplyr)

#Call in data
Lidar <- rast("D:/422/LiDAR_derived_snow_depth_ACO_CHRL_2021_P1.tif")
RCM <- rast("D:/422/HV.HH-Clipped-20210308.tif")

#Reproject the Lidar to RCM projection
Lidar <- project(Lidar, RCM)

#Resample the Lidar to match the RCM res. (50m)
Lidar50 <- resample(Lidar, RCM, method="bilinear")

#Save raster to a directory
#writeRaster(Lidar50, "D:/422/LiDAR_50.tif", overwrite=TRUE)

#Call in points for sampling values from Lidar and RCM
points <- vect("D:/422/SAR-Points/SAR-Points3.shp")

#Extract snowdepth
sd <- as.data.frame(extract(Lidar50, points))
names(sd) <- c("ID", "Snowdepth")

#Extract backscatter
bs <- as.data.frame(extract(RCM, points))
names(bs) <- c("ID", "Backscatter")

#Megere the dataframes and clean them to only have SAR-Lidar values
df <- bind_cols(sd, bs)
SAR_Snow <- dplyr::select(df, "Snowdepth", "Backscatter")

#Filter the values to remove noise (preliminary)
SAR_Snow <- dplyr::filter(SAR_Snow, Backscatter<25)
SAR_Snow <- dplyr::filter(SAR_Snow, Backscatter>0)
SAR_Snow <- dplyr::filter(SAR_Snow, Snowdepth>0.3)
SAR_Snow <- dplyr::filter(SAR_Snow, Snowdepth<10)

#Plot
plot(SAR_Snow$Snowdepth, SAR_Snow$Backscatter)
