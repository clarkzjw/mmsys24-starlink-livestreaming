FROM --platform=$BUILDPLATFORM python:3
ARG TARGETPLATFORM
ARG BUILDPLATFORM

RUN apt-get update && apt-get install iputils-ping net-tools vim iproute2 -y

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt

ADD *.py /app

RUN mkdir -p /figures

VOLUME /figures

ENV PYTHONUNBUFFERED=1

CMD ["python", "batch_runner.py"]
