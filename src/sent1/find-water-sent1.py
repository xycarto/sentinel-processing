import os
import sys
sys.path.append('/root/.snap/snap-python')
from snappy import ProductIO
import jpy
from sentinelsat import SentinelAPI
from snappy import HashMap, GPF
import glob
from pyproj import CRS
from pyproj.enums import WktVersion
from shapely.geometry import box
import rasterio as rio
import geopandas as gp
import numpy as np
from snappyTools import *


def getPoly(sentFile):
    dem = f"{OUTPUTS}/dem-{os.path.basename(sentFile).split('.')[0]}.tif"
    coast = gp.read_file(COASTLINE)
    rioDem = rio.open(dem)
    bounds = rioDem.bounds
    polyClip = box(*bounds)
    wktPoly = str(coast.clip(polyClip).dissolve().geometry.values[0])
    # wktPoly = coast.clip(polyClip).dissolve().geometry.values[0]
    
    # gp.GeoDataFrame(geometry=[polyClip], crs=4326).to_file(f"{OUTPUTS}/poly-test.gpkg", driver="GPKG")
    # gp.GeoDataFrame(geometry=[wktPoly], crs=4326).to_file(f"{OUTPUTS}/poly-clip-test.gpkg", driver="GPKG")
    
    return wktPoly, dem

def main():    
    crsWKT = CRS.from_string("EPSG:4326").to_wkt(WktVersion.WKT1_GDAL)
    zip_array = glob.glob(f"{OUTPUTS}/*.zip")
    
    for sentFile in zip_array:        
        wktPoly, dem = getPoly(sentFile)    
        source = ProductIO.readProduct(sentFile)                
        
        polarization, pols, modestamp, productstamp, polstamp = getPols(sentFile)
        applyOrbit = ApplyOrbitFile(source)        
        thermal = ThermalNoiseRemoval(applyOrbit)               
        calibrated = RCalibration(thermal, CAL_MEASURE)        
        speckle = SpeckleFilter(calibrated, calibrated.getBandNames(), SFILTER)  
        terrain= TerrainCorrection(speckle, crsWKT, 0, dem)  
        
        subset = MakeSubset(terrain, wktPoly) 
        print(list(subset.getBandNames())) 
        
        parameters = HashMap()
        parameters.put('sourceBandNames', subset.getBandNames()[1])
        band = GPF.createProduct('BandsExtractorOp', parameters, subset)
        
        # ProductIO.writeProduct(band, f"{OUTPUTS}/terrain", 'GeoTIFF')
         
        parameters = HashMap()
        # parameters.put("sourceBands", f"{subset.getBandNames()[1]}")
        lineartodb = GPF.createProduct('linearToFromdB', parameters, band)        
        ProductIO.writeProduct(lineartodb, f"{OUTPUTS}/linear", 'GeoTIFF')
    
        # parameters = HashMap()
        # parameters.put('clusterCount', 14)
        # parameters.put('iterationCount', 30)
        # parameters.put('MaskName', wktPoly)
        # target = GPF.createProduct('KMeansClusterAnalysis', parameters, lineartodb)
        # ProductIO.writeProduct(target, f"{OUTPUTS}/kcluster-test", 'GeoTIFF')    
    
    

if __name__ == "__main__":
        
    REGION = f"{sys.argv[1]} Region"
    START = sys.argv[2]
    END = sys.argv[3]
    USER = os.environ.get("ESAUSER")
    PW = os.environ.get("ESAPW")
    URL = "https://scihub.copernicus.eu/dhus/"
    SENT_DIR = "data/sent1"
    OUTPUTS = f"{SENT_DIR}/{sys.argv[1]}-{START}-{END}"
    CAL_MEASURE = "Sigma0"
    SFILTER = 'Lee'
    COASTLINE = "data/geo-data/vector/4326/4326-nz-coastlines-and-islands-polygons-topo-150k.gpkg"
    
    for d in [SENT_DIR, OUTPUTS]:
        os.makedirs(d, exist_ok=True)
    
    main()