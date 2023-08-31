#!/bin/bash

nztm_intif="data/geo-data/raster/2193/dem_clip_nztm"
wgs_tif="data/geo-data/raster/4326/dem_clip_wgs"

mkdir -p $wgs_tif

nztm_tifs=$( find ${nztm_intif} -name "*.tif" )
for tif in ${nztm_tifs[@]}
do
    base=$( basename $tif )
    gdaladdo -clean $tif
    gdalwarp -s_srs EPSG:2193 -t_srs EPSG:4326 $tif ${wgs_tif}/$base
done

gdaltindex ${wgs_tif}/dem-index.gpkg ${wgs_tif}/*.tif