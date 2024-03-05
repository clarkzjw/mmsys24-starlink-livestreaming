# MMSys'24 Artifact "Low-Latency Live Video Streaming over a Low-Earth-Orbit Satellite Network with DASH"

![Build](https://github.com/clarkzjw/mmsys24-starlink-livestreaming/actions/workflows/build.yaml/badge.svg)

**[WIP]** 

This repository contains the implementation and artifacts for the paper *Low-Latency Live Video Streaming over a Low-Earth-Orbit Satellite Network with DASH* accepted by ACM MMSys'24.

## Repository structure

```
├── batch.json.example
├── docker-compose-emulation.yaml
├── docker-compose-ingest.yaml
├── docker-compose.yaml
├── Dockerfile-dashjs
├── Dockerfile-livesim2
├── Dockerfile-nginx
├── Dockerfile-nginx-emulation
├── Dockerfile-runner
├── etc
├── experiments
├── poetry.lock
├── pyproject.toml
├── README.md
├── runner
├── shaper
├── stats-server
├── terraform
└── webassembly
```

---

## Prerequisites

Any system capable of running recent versions of [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/) should suffice. The results of this paper were produced on Debian 12.5 x86-64 with Docker version 25.0.3 and the built-in [Compose plugin](https://docs.docker.com/compose/install/linux/) version 2.24.5. However, the [Compose standalone](https://docs.docker.com/compose/install/standalone/) should also work.

To install Docker and Docker compose plugin on a recent Linux distribution, you can use the following script.

```bash
curl -fsSL https://get.docker.com | sh
```

---

This repository features three distinct levels of reproducibilities.

[Re-generate paper results](#re-generate-paper-results)

[Emulation](#emulation)

[Real world experiments](#real-world-experiments)

## Re-generate paper results

To re-generate the figures in the paper, please follow the following steps.


## Emulation

To conduct video streaming using our purpose-built network emulator, please follow the following steps.


## Real world experiments

To conduct video streaming over real networks, please follow the following steps.





### Install Terraform

https://developer.hashicorp.com/terraform/install


### Install gcloud CLI

https://cloud.google.com/sdk/docs/install

then run `gcloud init` to authenticate.

### Terraform Provision VM

edit `terraform.tfvars`

then `terraform init`, 

`gcloud auth application-default login`

`terraform plan` and `terraform apply`

SSH login to the new VM, wait until `/var/log/cloud-init-output.log` is finished.
```
[...]

Cloud-init v. 23.1.2-0ubuntu0~23.04.1 finished at Fri, 08 Dec 2023 23:20:04 +0000. Datasource DataSourceGCELocal.  Up 1117.00 seconds
```

apply File Watch Limit adjustment

```bash
echo fs.inotify.max_user_watches= 131070 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
```

apply UDP buffer size adjustments

https://github.com/quic-go/quic-go/wiki/UDP-Buffer-Sizes

```bash
sudo sysctl -w net.core.rmem_max=2500000
sudo sysctl -w net.core.wmem_max=2500000
```

For real world experiments, deploy live video streaming server on the cloud VM by

```bash
docker compose -f docker-compose-ingest.yaml up -d
```

after that, the MPD file can be retrieved at

`https://<cloud-vm-ip>/livesim2/vectors/switching_sets/12.5_25_50/ss1/2023-04-28/stream.mpd`

you might want to use the broswer to visit the URL once to acknowledge the insecure HTTPS warning.

update `experiment.json` with this new MPD_URL

and test it can be played back at dash.js sample player

https://reference.dashif.org/dash.js/latest/samples/low-latency/testplayer/testplayer.html

### DASH Video Source

+ https://dash.akamaized.net/WAVE/vectors/switching_sets/12.5_25_50/ss1/2023-04-28/stream.mpd from https://cta-wave.github.io/Test-Content/. 

+ https://us-west.gcp.clarkzjw.ca/livesim2/vectors/switching_sets/12.5_25_50/ss1/2023-04-28/stream.mpd

+ https://nginx/livesim2/vectors/switching_sets/12.5_25_50/ss1/2023-04-28/stream.mpd

+ https://cmafref.akamaized.net/cmaf/live-ull/2006350/akambr/out.mpd
