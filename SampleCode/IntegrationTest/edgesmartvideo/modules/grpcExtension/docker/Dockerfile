FROM tensorflow/tensorflow:2.7.0 as base

RUN apt-get update && apt-get install -y --no-install-recommends 
RUN apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev
# RUN python3-pip python3-dev libglib2.0-0 libsm6 libxext6 libxrender-dev
# RUN cd /usr/local/bin
# RUN ln -s /usr/bin/python3 python
RUN pip install --upgrade pip
RUN pip install numpy pillow opencv-python
RUN pip install requests protobuf grpcio
RUN pip install numpy scipy matplotlib
RUN pip install azure-iot-device~=2.7.0
RUN apt-get install -y libgl1-mesa-dev && apt-get clean

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# FROM ubuntu:18.04 as base

# RUN apt update \
#     && apt install -y software-properties-common python3.8 python3-pip python3-dev libglib2.0-0 libsm6 libxext6 libxrender-dev \
#     && cd /usr/local/bin \
#     && ln -s /usr/bin/python3.8 python \
#     && pip3 install --upgrade pip \
#     && pip3 install numpy pillow opencv-python \
#     && pip3 install requests protobuf grpcio \
#     && pip3 install numpy scipy matplotlib \
#     && pip3 install tensorflow==2.2.0 \
#     && apt-get install -y libgl1-mesa-dev && apt-get clean

# Install python
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     python3-pip python3-dev libglib2.0-0 libsm6 libxext6 libxrender-dev\
#     && cd /usr/local/bin \
#     && ln -s /usr/bin/python3 python \
#     && pip3 install --upgrade pip \
#     && pip3 install numpy pillow opencv-python \
#     && pip3 install requests protobuf grpcio \
#     && pip3 install numpy scipy matplotlib \
#     && apt-get install -y libgl1-mesa-dev && apt-get clean

# RUN python3.7 -m pip install -U pip
# RUN python3.8 -m pip install tensorflow==2.2.0

# Copy AVA extension specific files
RUN mkdir /app
COPY ./app/*.py /app/
COPY ./app/grpc-proto/*.py /app/

# Starts the AVA gRPC extension server
FROM base as final
WORKDIR /app/
CMD ["python3", "main.py"]
