library(terra)
r <- terra::rast("C:/Users/abarzkar/Downloads/LiDAR_derived_snow_depth_ACO_CHRL_2021_P1(1).tif")
plot(r, xlim=c(383000,390000), ylim=c(5451000,5456000))

##round
maker = function(x,y){rast("C:/Users/abarzkar/Downloads/LiDAR_derived_snow_depth_ACO_CHRL_2021_P1(1).tif")}
r2 = round(maker(14073,13096)/3)
plot(r2, xlim=c(383000,390000), ylim=c(5451000,5456000))

#polygonize
p2 = as.polygons(r2)
plot(p2)
plot(p2,col=1:4)

## from-to-becomes
# classify the values into three groups 
# all values >= 0 and <= 2 become 1, etc.
m <- c(0, 2, 2,
       2, 4, 4,
       4, 6, 6,
       6, 8, 8,
       8, 10, 10,
       10, 12, 12)
rclmat <- matrix(m, ncol=3, byrow=TRUE)
rc1 <- classify(r, rclmat, include.lowest=TRUE)
plot(rc1)
