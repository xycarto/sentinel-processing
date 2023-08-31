# ESA SNAP 9 Running on Ubuntu 20.04 and Python 3.8

Docker images of ESA Sentinel Application Platform (SNAP) from http://step.esa.int/main/toolboxes/snap/

Installation is using:

- Ubuntu 20.04
- Python 3.8
- GDAL 3.2.1 (for snappy)
- GDAL 3.4.3 (for shell)

Added Packages from `pip3`:

```
geopandas 
pandas 
matplotlib 
numpy 
boto3 
sentinelsat
```

Additional:

```
GRASSGIS 8.2.0
```

## Installation

Installed using set from: https://github.com/mundialis/esa-snap/tree/ubuntu

Install/Build: `make docker-local`

Pull the Ubuntu Linux based image (all SNAP toolboxes included):

```
make docker-pull
```

## Tutorial

We recommend the following tutorial for BASH commands:

http://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf

### Usage examples

#### Tests

Check snappy install: `make tests`

