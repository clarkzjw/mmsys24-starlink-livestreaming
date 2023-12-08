import docker
from config import VIDEO_CONTAINER_IMAGE, CHROME_CONTAINER_IP, DOCKER_NETWORK_NAME
import os


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
