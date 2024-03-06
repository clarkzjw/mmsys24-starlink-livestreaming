import os
import time
import logging
from config import VIDEO_CONTAINER_IMAGE, CHROME_CONTAINER_IP, DOCKER_NETWORK_NAME

import docker


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger("util")


def pull_ffmpeg_image() -> None:
    client = docker.from_env()
    client.images.pull(VIDEO_CONTAINER_IMAGE)
    


def create_ffmpeg_container(exp_id: str) -> docker.models.containers.Container:
    client = docker.from_env()
    workdir = os.getenv("WORKDIR")

    container = client.containers.run(VIDEO_CONTAINER_IMAGE,
                                        detach=True,
                                        environment=[
                                            "DISPLAY_CONTAINER_NAME={}".format(CHROME_CONTAINER_IP),
                                            "FILE_NAME={}.mp4".format(exp_id),
                                            ],
                                        network=DOCKER_NETWORK_NAME,
                                        volumes=["{}/videos:/videos".format(workdir)])
    return container


def restart_nginx() -> None:
    logger.info("restarting nginx")
    client = docker.from_env()
    nginx = client.containers.get("dashjs-nginx")
    nginx.restart()
    while True:
        try:
            nginx = client.containers.get("dashjs-nginx")
            if nginx.status == "running":
                break
        except:
            logger.info("waiting for nginx to restart")
            time.sleep(1)
            continue
