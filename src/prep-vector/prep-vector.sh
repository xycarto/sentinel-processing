#!/bin/bash

# bash src/prep/prep-vector.sh

vdir="data/geo-data/vector/kx-new-zealand-3layers-GPKG"
outdir="data/geo-data/vector"

vlist=$( find $vdir -name "*.gpkg" )

for v in ${vlist[@]}
do
    base=$( basename $v )
    ogr2ogr -overwrite ${outdir}/2193/2193-${base} $v
    ogr2ogr -overwrite -t_srs EPSG:4326 ${outdir}/4326/4326-${base} $v
done