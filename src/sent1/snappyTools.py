import os
import sys
sys.path.append('/root/.snap/snap-python')
from snappy import ProductIO
import jpy
import snappy
from snappy import GPF, HashMap
from snappy import PixelPos
from osgeo.osr import SpatialReference
import json
from shapely.geometry import shape
from shapely.wkt import dumps


## Extract mode, product type, and polarizations from filename
def getPols(sentFile):    
    modestamp = sentFile.split("_")[1]
    productstamp = sentFile.split("_")[2]
    polstamp = sentFile.split("_")[3]
      
    polarization = polstamp[2:4]
    if polarization == 'DV':
        pols = 'VH,VV'
    elif polarization == 'DH':
        pols = 'HH,HV'
    elif polarization == 'SH' or polarization == 'HH':
        pols = 'HH'
    elif polarization == 'SV':
        pols = 'VV'
    else:
        print("Polarization error!")
        
    return polarization, pols, modestamp, productstamp, polstamp

# perform Apply-Orbit-File
def ApplyOrbitFile(input_product):
    parameters = HashMap()
    parameters.put("orbitType", "Sentinel Restituted (Auto Download)")
    parameters.put("continueOnFail", False)
    parameters.put("polyDegree", 3)
    output_product = GPF.createProduct(
        "Apply-Orbit-File", parameters, input_product
    )
    return output_product


# perform ThermalNoiseRemoval
def ThermalNoiseRemoval(input_product):
    parameters = HashMap()
    parameters.put("selectedPolarisations", "VV,VH")
    parameters.put("reIntroduceThermalNoise", False)
    parameters.put("removeThermalNoise", True)
    output_product = GPF.createProduct(
        "ThermalNoiseRemoval", parameters, input_product
    )
    return output_product


# perform radiometric Calibration
def RCalibration(input_product, cal_measure):
    parameters = HashMap()
    parameters.put("sourceBands", "")
    if cal_measure == "Sigma0":
        parameters.put("outputSigmaBand", True)
        parameters.put("outputBetaBand", False)
    elif cal_measure == "Beta0":
        parameters.put("outputSigmaBand", False)
        parameters.put("outputBetaBand", True)
    parameters.put("outputImageScaleInDb", False)
    parameters.put("createGammaBand", False)
    parameters.put("selectedPolarisations", "")
    parameters.put("outputGammaBand", False)
    parameters.put("outputImageInComplex", False)
    parameters.put("externalAuxFile", "")
    parameters.put("auxFile", "Product Auxiliary File")
    parameters.put("createBetaBand", False)
    output_product = GPF.createProduct(
        "Calibration", parameters, input_product
    )
    return output_product

def MakeSubset(input_product, wktPoly):
    parameters = HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('geoRegion', wktPoly)
    output_product = GPF.createProduct('Subset', parameters, input_product)
    return output_product

def TerrainCorrection(input_product, crsWkt, downsample, dem):
    parameters = HashMap()
    parameters.put('externalDEMFile', dem)
    parameters.put("externalDEMNoDataValue", "-32767")
    parameters.put("demResamplingMethod", "BILINEAR_INTERPOLATION")
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('mapProjection', crsWkt)       # comment this line if no need to convert to UTM/WGS84, default is WGS84
    parameters.put('saveProjectedLocalIncidenceAngle', True)
    parameters.put('saveSelectedSourceBand', True)
    if downsample == 1:                      # downsample: 1 -- need downsample to 40m, 0 -- no need to downsample
        parameters.put('pixelSpacingInMeter', 40.0)
    output_product = GPF.createProduct('Terrain-Correction', parameters, input_product)
    return output_product

# def TerrainCorrection(input_product, crsWkt, sourceBands, dem):
#     parameters = HashMap()
#     parameters.put("saveLatLon", False)
#     parameters.put("saveIncidenceAngleFromEllipsoid", False)
#     parameters.put("nodataValueAtSea", True)
#     parameters.put("alignToStandardGrid", False)
#     parameters.put("pixelSpacingInMeter", 10.0)
#     crs = SpatialReference(crsWkt)
#     crs.AutoIdentifyEPSG()
#     code = crs.GetAuthorityName(None) + ":" + crs.GetAuthorityCode(None)
#     parameters.put("mapProjection", code)
#     parameters.put("saveBetaNought", False)
#     # if dem == "auto":
#     #     parameters.put("externalDEMFile", "")
#     #     parameters.put("demName", "SRTM 1Sec HGT")
#     #     parameters.put("externalDEMNoDataValue", 0.0)
#     # else:
#     #     parameters.put("demName", "External DEM")
#     #     parameters.put("externalDEMNoDataValue", "-32767")
#           parameters.put("externalDEMFile", dem)
#     parameters.put("demResamplingMethod", "BILINEAR_INTERPOLATION")
#     parameters.put("imgResamplingMethod", "BILINEAR_INTERPOLATION")
#     parameters.put("saveSigmaNought", False)
#     parameters.put(
#         "incidenceAngleForSigma0",
#         "Use projected local incidence angle from DEM",
#     )
#     parameters.put("sourceBands", sourceBands)
#     parameters.put("applyRadiometricNormalization", False)
#     parameters.put("externalDEMApplyEGM", True)
#     parameters.put("saveSelectedSourceBand", True)
#     parameters.put("outputComplex", False)
#     parameters.put("saveProjectedLocalIncidenceAngle", False)
#     parameters.put(
#         "incidenceAngleForGamma0",
#         "Use projected local incidence angle from DEM",
#     )
#     parameters.put("saveGammaNought", False)
#     parameters.put("saveLocalIncidenceAngle", False)
#     parameters.put("standardGridOriginX", 0.0)
#     parameters.put("saveDEM", False)
#     parameters.put("standardGridOriginY", 0.0)
#     parameters.put("pixelSpacingInDegree", "8.983152841195215E-5")
#     parameters.put("externalAuxFile", "")
#     parameters.put("auxFile", "Latest Auxiliary File")
#     output_product = GPF.createProduct(
#         "Terrain-Correction", parameters, input_product
#     )
#     return output_product

def ExtractBands(input_source, bandName):
    parameters = HashMap()
    parameters.put('sourceBandNames', bandName)
    output_product = GPF.createProduct('BandsExtractorOp', parameters, input_source)
    return output_product

def ImSubset(input_product, wkt):
    # geom = WKTReader().read(crsWkt)
    parameters = HashMap()
    parameters.put("sourceBands", "")
    parameters.put("fullSwath", False)
    # parameters.put('tiePointGridNames', '')
    parameters.put("geoRegion", wkt)
    parameters.put("copyMetadata", True)
    parameters.put("region", "0,0,0,0")
    # subsetting by number of pixels
    # subsampling
    parameters.put(
        "subSamplingX", 1
    )  # one pixel, increase or decrease (under or over sampling)
    parameters.put("subSamplingY", 1)  # one pixel, increase or decrease
    output_product = GPF.createProduct("Subset", parameters, input_product)
    return output_product


def ApplyBandMath(input_target_bands, targetBands):
    parameters = HashMap()
    parameters.put("unit", "")
    parameters.put("name", "bm_name")
    parameters.put("noDataValue", 0.0)
    parameters.put("description", "")
    parameters.put("targetBands", targetBands)
    output_product = GPF.createProduct(
        "BandMaths", parameters, input_target_bands
    )
    return output_product


def CreateLayerStack(input_n_dim_array):
    parameters = HashMap()
    parameters.put("extent", "Master")
    parameters.put("resamplingType", "NONE")
    parameters.put("initialOffsetMethod", "Orbit")
    output_product = GPF.createProduct(
        "CreateStack", parameters, input_n_dim_array
    )
    return output_product


def SpeckleFilter(input_product, sourceBands, filter):
    parameters = HashMap()
    parameters.put("sourceBands", sourceBands)
    parameters.put("filter", filter)
    parameters.put("windowSize", "5x5")
    parameters.put("sigma", 0.9)
    parameters.put("targetWindowSize", "3x3")
    parameters.put("enl", 1.0)
    parameters.put("anSize", 50)
    parameters.put("filterSizeY", 3)
    parameters.put("filterSizeX", 3)
    parameters.put("numLooksStr", "1")
    parameters.put("dampingFactor", 2)
    parameters.put("estimateENL", True)
    output_product = GPF.createProduct(
        "Speckle-Filter", parameters, input_product
    )
    return output_product


def TerrainFlattening(input_product, dem):
    parameters = HashMap()
    parameters.put("additionalOverlap", 0.1)
    parameters.put("outputSimulatedImage", False)
    parameters.put("externalDEMApplyEGM", False)
    parameters.put("oversamplingMultiple", 1.5)
    if dem == "auto":
        parameters.put("demName", "SRTM 1Sec HGT")
    else:
        parameters.put("demName", "External DEM")
        parameters.put("externalDEMNoDataValue", "-999")
        parameters.put("externalDEMFile", dem)
    parameters.put("demResamplingMethod", "BILINEAR_INTERPOLATION")
    parameters.put("externalDEMNoDataValue", 0.0)
    output_product = GPF.createProduct(
        "Terrain-Flattening", parameters, input_product
    )
    return output_product


def BorderNoiseRemoval(input_product):
    parameters = HashMap()
    parameters.put("trimThreshold", 0.5)
    parameters.put("borderLimit", 500)
    # parameters.put('borderLimit', 1000)
    output_product = GPF.createProduct(
        "Remove-GRD-Border-Noise", parameters, input_product
    )
    return output_product