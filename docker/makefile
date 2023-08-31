include ../.creds

BASEIMAGE := xycarto/snap-v9-geo
IMAGE := $(BASEIMAGE):2023-09-01

RUN ?= docker run -it --rm --net=host --user=$$(id -u):$$(id -g) -e DISPLAY=$$DISPLAY --env-file=../.creds -e RUN= -v$$(pwd)/..:/work -w /work -e HOME=/work $(IMAGE) 

tests:
	$(RUN) gdalinfo --version
	$(RUN) python3 --version
	$(RUN) python3 -c 'from snappy import ProductIO'
	$(RUN) grass --version
	$(RUN) python3 docker/snap/about.py

test-local: Dockerfile
	$(RUN) bash

docker: Dockerfile
	echo $(DOCKER_PW) | docker login --username xycarto --password-stdin
	docker build --rm --tag $(BASEIMAGE) . && \
	docker tag $(BASEIMAGE) $(IMAGE) && \
	docker push $(IMAGE) 

docker-local: Dockerfile
	docker build --rm --tag $(BASEIMAGE) . && \
	docker tag $(BASEIMAGE) $(IMAGE)

docker-pull:
	docker pull $(IMAGE)