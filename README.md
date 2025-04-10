### Disclaimer

* Use at your own risk, I accept no responsibility for any errors or misuse 
* No AI has been harmed in the process

### Contact

Need a serious non vibe / AI only coder? Contact me at breinbaas@pm.me

### What it is

This script creates crosssections based on AHN5 data and polylines defining the line of (for example) a levee. It generates two kind of csv files, one with the l,z coordinates and one with the l,x,y,z coordinates. It also generates a plot of the crosssection. This data can then be used in other scripts or software.

### Needed files

The AHN5 tiles (*.tif) need to be downloaded before using this script and placed in a directory defined as AHN5_PATH in the script. 

You will need a shapefile that defines the location of the object. In this case we use a shapefile defined as ROUTEGEOMETRIE_SHAPE in the script. Note that you will need to adjust the script based on your shp metadata. In this case the shapefile contains polyline geometries and fields called TRAJECT (name of the levee), VAN (start chainage), TOT (end chainage). This is used to define the location of the crosssection. 

### TIP

It is easy to download AHN files, it is a little harder to get the names of the files you need to download. I use the AHN overview to find the names like '2023_M_24FN2' and simply write them in a texteditor. I then generate a batch script to download the files using **wget**.

Here is a sample of how to create a line in a batch script that downloads 2 raster files:

```
wget https://ns_hwh.fundaments.nl/hwh-ahn/AHN5/02a_DTM_50cm/2023_M_24FN2.TIF
wget https://ns_hwh.fundaments.nl/hwh-ahn/AHN5/02a_DTM_50cm/2023_M_25AN1.TIF
```

Note that you need to make a choice to use the DTM (terrain model) or DSM model.

### Other required input

* OUTPUT_PATH, where to write the output files (needs to be available beforehand)
* HOH_AFSTAND, the distance between the crosssections
* LENGTE_POLDER, the length of the crosssection towards the polder
* LENGTE_BOEZEM, the length of the crosssection towards the river
* INTERVAL, the distance between the points on the crosssection (the AHN data has a 0.5m resolution in x and y direction)

### Sample

* lz csv files

```
l,z
-20.0,0.205
-19.5,0.235
-19.0,0.211
-18.5,0.286
-18.0,0.334
```

* lxyz files

```
l,x,y,z
-20.0,127038.72,482981.98,0.205
-19.5,127039.11,482982.30,0.235
-19.0,127039.49,482982.62,0.211
-18.5,127039.88,482982.94,0.286
-18.0,127040.26,482983.26,0.334
...
```

* plot

![sample image](https://github.com/breinbaas/waternet_crosssections/blob/master/img/sample.png)






