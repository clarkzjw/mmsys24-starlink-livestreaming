FROM --platform=$BUILDPLATFORM python:3.11.4
ARG TARGETPLATFORM
ARG BUILDPLATFORM

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y iputils-ping

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./app.py"]
