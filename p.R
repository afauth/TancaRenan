library(dplyr)
library(pmetar)

dm <- metar_get_historical("SBKP", start_date = "2018-01-01", end_date = "2018-12-31", from = "iastate")
table <- metar_decode(dm)

x <- subset(table, select=c("METAR_Date", "Pressure", "Temperature","Elevation"))
x$Time <- as.numeric(as.POSIXct(x$METAR_Date))

g <- 9.80665
M <- 0.0289644
R <- 8.31432
T0 <- 288.16 

x$pressure <- x$Pressure*exp(-g*M*x$Elevation/(R*T0))
x2 <- subset(x, select=c("Time", "pressure"))
write.csv(x2, file="pressure2018.csv")