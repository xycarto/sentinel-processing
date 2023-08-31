FROM ubuntu:20.04

RUN echo "Making Snap and Snappy"
ENV TZ Pacific/Auckland

RUN apt-get update
RUN apt-get install -y tzdata
RUN echo "Pacific/Auckland" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

ENV DEBIAN_FRONTEND noninteractive

USER root

# Install dependencies and tools
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    libgfortran5 \
    locales \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    git \
    vim \
    wget \
    zip \
    && apt-get autoremove -y \
    && apt-get clean -y

# Set the locale
ENV LANG en_US.utf8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.utf8

# SNAP wants the current folder '.' included in LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH ".:$LD_LIBRARY_PATH"

# install SNAPPY
RUN apt-get install openjdk-8-jdk maven -y
ENV JAVA_HOME "/usr/lib/jvm/java-11-openjdk-amd64/"
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
COPY snap /src/snap
RUN bash /src/snap/install.sh
RUN update-alternatives --remove python /usr/bin/python3

# path
RUN echo "export PATH=\$PATH:/usr/local/snap/bin/:/root/.snap/auxdata/gdal/gdal-3-2-1/bin" >> /root/.bashrc

# Reduce the image size
RUN apt-get autoremove -y
RUN apt-get clean -y
RUN rm -rf /src

# Install addition Python libraries
RUN pip3 install matplotlib numpy sentinelsat boto3 pandas geopandas

# Install GDAL for use outside SNAP
RUN apt-get install -y software-properties-common 
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update && apt-get -y install libgdal-dev gdal-bin python3-gdal

# Install GRASS GIS
RUN apt-get update && apt-get -y install grass-core grass-dev

# Install awscli
RUN pip3 install awscli

RUN pip3 install rasterio

# # When using SNAP from Python, either do: sys.path.append('/root/.snap/snap-python')

RUN apt-get autoremove -y
RUN apt-get clean -y

# # increase the JAVA VM size to avoid NullPointer exception in Snappy during S-1 processing
# RUN cd /root/.snap/snap-python/snappy && sed -i "s/^java_max_mem:.*/java_max_mem: 40G/" snappy.ini

# # get minor python version
# RUN PYMINOR=$(python3 -c 'import platform; major, minor, patch = platform.python_version_tuple(); print(minor)') && cd /usr/local/lib/python3.$PYMINOR/dist-packages/snappy/ && sed -i "s/^java_max_mem:.*/java_max_mem: 40G/" snappy.ini