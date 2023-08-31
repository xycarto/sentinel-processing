include .creds

BASEIMAGE := xycarto/snap-v9-geo
IMAGE := $(BASEIMAGE):2023-09-01

RUN ?= docker run -it --rm --net=host --user=$$(id -u):$$(id -g) -e DISPLAY=$$DISPLAY --env-file=.creds -e RUN= -v$$(pwd):/work -w /work -e HOME=/work $(IMAGE) 


# make tool-info operator=KMeansClusterAnalysis
##### Tool Info
tool-info:
	$(RUN) python3 src/snappy-param-info.py $(operator)

##### Downloads

# make list-sent1 region="Waikato" start-date=20230801 end-date=20230831 prodtype='GRD' opmode='IW' orbdir='Ascending' arearel='Intersects' polmode='VV'
list-sent1:
	$(RUN) python3 src/sent1/list-sent1.py $(region) $(start-date) $(end-date) $(prodtype) $(opmode) $(orbdir) $(arearel) $(polmode)

# make download-sent1-query region="Waikato" start-date=20230801 end-date=20230831 quarry="S1A_IW_GRDH_1SDV_20230825T070809_20230825T070834_050028_0604E6_2521 S1A_IW_GRDH_1SDV_20230813T070808_20230813T070833_049853_05FEF4_C235"
download-sent1-query:
	$(RUN) python3 src/sent1/download-sent1.py $(region) $(start-date) $(end-date) "$(quarry)"

##### Process

# make preprocess region="Waikato" start-date=20230801 end-date=20230831
preprocess:
	$(RUN) python3 src/sent1/pre-process-sent1.py $(region) $(start-date) $(end-date)

# make find-water region="Waikato" start-date=20230801 end-date=20230831
find-water:
	$(RUN) python3 src/sent1/find-water-sent1.py $(region) $(start-date) $(end-date)

##### Cleaning/Prepping

repro-dem:
	$(RUN) bash src/prep-raster/repro-dem.sh


##### DOCKER
test-local:
	$(RUN) bash

docker-pull:
	docker pull $(IMAGE)