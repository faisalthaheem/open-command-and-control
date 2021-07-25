FROM ubuntu:20.04

WORKDIR /setup

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive && apt install -y \
    wget && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod +x Miniconda3-latest-Linux-x86_64.sh && \
    sh Miniconda3-latest-Linux-x86_64.sh -b && \
    eval "$(/root/miniconda3/bin/conda shell.bash hook)" && \
    conda init

WORKDIR /code

ADD ["src/","conda-env.yaml","/code/"]

RUN eval "$(/root/miniconda3/bin/conda shell.bash hook)" && \
    conda env create -f conda-env.yaml

ADD ["src/","conda-env.yaml","shell/run-open-c2.sh","/code/"]
#CMD "/code/run-open-c2.sh"