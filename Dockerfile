From nvcr.io/nvidia/pytorch:19.04-py3

RUN apt-get -y update

RUN apt-get install -y python3-pip software-properties-common wget ffmpeg

RUN apt-get -y update

RUN mkdir -p /root/.torch/models

RUN mkdir /data/

ADD . /data/

WORKDIR /data

RUN pip install -r requirements.txt

RUN pip install Flask

RUN pip install Pillow

RUN pip install scikit-image

RUN pip install requests

RUN wget -O /root/.torch/models/vgg16_bn-6c64b313.pth https://download.pytorch.org/models/vgg16_bn-6c64b313.pth

RUN wget -O /root/.torch/models/resnet34-333f7ec4.pth https://download.pytorch.org/models/resnet34-333f7ec4.pth

RUN wget -O /root/.torch/models/resnet101-5d3b4d8f.pth https://download.pytorch.org/models/resnet101-5d3b4d8f.pth

EXPOSE 80

ENTRYPOINT ["python3"]

CMD ["app.py"]

