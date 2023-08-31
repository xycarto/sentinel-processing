import os
import sys
sys.path.append('/root/.snap/snap-python')
from snappy import ProductIO
import jpy
import glob
from pyproj import CRS
from pyproj.enums import WktVersion
from shapely.geometry import box
import rasterio as rio
from snappyTools import *
import geopandas as gp


def getPoly(sentFile):
    dem = f"{OUTPUTS}/dem-{os.path.basename(sentFile).split('.')[0]}.tif"
    coast = gp.read_file(COASTLINE)
    rioDem = rio.open(dem)
    bounds = rioDem.bounds
    polyClip = box(*bounds)
    wktPoly = str(coast.clip(polyClip).dissolve().geometry.values[0])
    
    return wktPoly, dem

def outputName(input_product, subset):
    fname_i = input_product.split('/')[-1].split('_') ## extract just filename from the filepath and split the filename using '_'
    fname_join = "_".join(fname_i[:5])
    prodName = subset.getName().split('_') ## product name after all the processes are stored here
    diff = [wd for wd in prodName if wd not in fname_i]
    diff_alpha = [word for word in diff if word.isalpha()]
    sat_pass_i = subset.getMetadataRoot().getElement('Abstracted_Metadata').getAttributeString('PASS')
    output_product = fname_join + "_" +"-".join(diff_alpha[1:] + [diff_alpha[0]]) + '_' + sat_pass_i
    return output_product

def main(): 
    print("Mods Loaded")    
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
        
        # IW images are downsampled from 10m to 40m (the same resolution as EW images).
        if (modestamp == 'EW' and productstamp == 'GRDH'):
            downsample = 1
            tercorrected = TerrainCorrection(speckle, crsWKT, downsample, dem)            
            subset = MakeSubset(tercorrected, wktPoly)
        elif (modestamp == 'IW' and productstamp == 'GRDH') or (modestamp == 'EW' and productstamp == 'GRDM'):
            downsample = 0
            tercorrected = TerrainCorrection(speckle, crsWKT, downsample, dem)
            subset = MakeSubset(tercorrected, wktPoly)
        else:
            print("Different spatial resolution is found.")
            
        # Name of the output file
        outname = outputName(sentFile, subset)

        if downsample == 0:
            print("Writing the bands separately...")
            # print(subset)
            for band in subset.getBandNames():
                bname = outname + '_' + band ## adding bandname to the filename
                print("Writing %s band..." %(bname))
                out_band = ExtractBands(subset, band) ## Extraacting the bands before saving them
                ProductIO.writeProduct(out_band, f"{OUTPUTS}/{bname}", 'GeoTIFF')
        elif downsample == 1:
            print("Writing undersampled image...")
            for band in subset.getBandNames():
                bname = outname + '_' + band ## adding bandname to the filename
                out_band = ExtractBands(subset, band) ## Extraacting the bands before saving them
                ProductIO.writeProduct(out_band, f"{OUTPUTS}/{bname}_40m", 'GeoTIFF')
        else:
            print("Error.")
    

if __name__ == "__main__":
        
    REGION = f"{sys.argv[1]} Region"
    START = sys.argv[2]
    END = sys.argv[3]
    USER = os.environ.get("ESAUSER")
    PW = os.environ.get("ESAPW")
    URL = "https://scihub.copernicus.eu/dhus/"
    SENT_DIR = "data/sent1"
    OUTPUTS = f"{SENT_DIR}/{sys.argv[1]}-{START}-{END}"
    QUERY = f"{OUTPUTS}/{START}-{END}.gpkg"
    CAL_MEASURE = "Sigma0"
    SFILTER = 'Lee'
    COASTLINE = "data/geo-data/vector/4326/4326-nz-coastlines-and-islands-polygons-topo-150k.gpkg"
    
    for d in [SENT_DIR, OUTPUTS]:
        os.makedirs(d, exist_ok=True)
    
    main()