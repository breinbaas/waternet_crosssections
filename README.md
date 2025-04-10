### What it is

This script creates crosssections based on AHN5 data and polylines defining the line of (for example) a levee. It generates two kind of csv files, one with the l,z coordinates and one with the l,x,y,z coordinates. It also generates a plot of the crosssection. This data can then be used in other scripts or software.

### Needed files

The AHN5 tiles (*.tif) need to be downloaded before using this script and placed in a directory defined as AHN5_PATH in the script. 

You will need a shapefile that defines the location of the object. In this case we use a shapefile defined as ROUTEGEOMETRIE_SHAPE in the script. Note that you will need to adjust the script based on your shp metadata. In this case the shapefile contains polyline geometries and fields called TRAJECT (name of the levee), VAN (start chainage), TOT (end chainage). This is used to define the location of the crosssection. 

### Other required input

* OUTPUT_PATH, where to write the output files (needs to be available beforehand)
* HOH_AFSTAND, the distance between the crosssections
* LENGTE_POLDER, the length of the crosssection towards the polder
* LENGTE_BOEZEM, the length of the crosssection towards the river
* INTERVAL, the distance between the points on the crosssection (the AHN data has a 0.5m resolution in x and y direction)




### Disclaimer

* Use at your own risk, I accept no responsibility for any errors or misuse 
* No AI has been harmed in the process

### Contact

Need a serious non vibe coder? Contact me at breinbaas@pm.me



