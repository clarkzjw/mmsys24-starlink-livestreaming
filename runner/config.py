import os
from dataclasses import dataclass
import json
import pytz
from datetime import datetime
from pprint import pprint


URL = "http://pyodide/samples/starlink/testplayer/testplayer.html?"
VIDEO_CONTAINER_IMAGE = "selenium/video:ffmpeg-4.3.1-20230607"
CHROME_CONTAINER_IP = "192.167.0.102"
DOCKER_NETWORK_NAME = "dashjs"


def get_exp_date() -> str:
    PST = pytz.timezone("US/Pacific")
    return datetime.now().astimezone(PST).strftime('%m%d-%H%M')

"""
abrGeneral:
    abrDynamic
    abrBola
    abrThroughput
    abrL2A
    abrLoLP
    abrCMAB
"""

@dataclass
class Experiment:
    """single round experiment"""
    EXPERIMENT_ID: str
    TOTAL_ROUNDS: int
    ROUND_DURATION: int
    TARGET_LATENCY: int
    # http://cdn.dashjs.org/latest/jsdoc/module-Settings.html#~LiveCatchupSettings__anchor
    # we set MAX_DRIFT = 2 * TARGET_LATENCY to trigger an seeking to live edge event
    MAX_DRIFT: int
    CONSTANT_VIDEO_BITRATE: int
    MPD_URL: str
    ABR_ALGORITHM: str
    MIN_CATCHUP_PLAYBACK_RATE: float
    MAX_CATCHUP_PLAYBACK_RATE: float
    EMULATION: bool = False
    CMAB_ALPHA: float = 0.5

    
    def __init__(self, obj: dict):
        self.ROUND_DURATION = int(obj["ROUND_DURATION"])
        self.TOTAL_ROUNDS = int(obj["TOTAL_ROUNDS"])
        self.TARGET_LATENCY = int(obj["TARGET_LATENCY"])
        # from https://dl.acm.org/doi/10.1145/3587819.3590971
        self.MAX_DRIFT = 5
        self.CONSTANT_VIDEO_BITRATE = int(obj["CONSTANT_VIDEO_BITRATE"])
        self.MPD_URL = obj["MPD_URL"]
        self.ABR_ALGORITHM = obj["ABR_ALGORITHM"]
        self.EXPERIMENT_ID = "{}-{}-target-latency-{}s-duration-{}-bitrate-{}".format(self.ABR_ALGORITHM, get_exp_date(), self.TARGET_LATENCY, self.ROUND_DURATION, "variable" if self.CONSTANT_VIDEO_BITRATE == -1 else "constant-{}".format(self.CONSTANT_VIDEO_BITRATE))
        # from https://dl.acm.org/doi/10.1145/3587819.3590971
        self.MAX_CATCHUP_PLAYBACK_RATE = 0.17
        self.MIN_CATCHUP_PLAYBACK_RATE = -0.17
        if "EMULATION" in obj.keys():
            self.EMULATION = bool(obj["EMULATION"])
        if "CMAB_ALPHA" in obj.keys():
            self.CMAB_ALPHA = float(obj["CMAB_ALPHA"])


BATCH_JSON = "/batch.json"
ExperimentList = list()


def load_config() -> tuple[list[Experiment], int, int]:
    total_count = 0
    total_duration = 0

    if os.path.isfile(BATCH_JSON):
        with open(BATCH_JSON) as f:
            for exp in json.loads(f.read()):
                e = Experiment(exp)
                ExperimentList.append(e)
                total_count += e.TOTAL_ROUNDS
                total_duration += e.TOTAL_ROUNDS * e.ROUND_DURATION
                pprint(e)
        return ExperimentList, total_count, total_duration
    else:
        print("/batch.json doesn't exist")
        return None, 0, 0
