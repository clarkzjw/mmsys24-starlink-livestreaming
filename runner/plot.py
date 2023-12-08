from pprint import pprint
from textwrap import wrap
from pymongo import MongoClient
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, List
from collections import defaultdict
from enum import Enum
import pytz
import os
import json
import pathlib


PST = pytz.timezone("US/Pacific")

FIGURE_DIR = "/figures/"
MONGO_DB_ADDR = "mongo"
MONGO_DB_NAME = "starlink"
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID")

client = MongoClient("mongodb://starlink:starlink@{}:27017/".format(MONGO_DB_ADDR))
db = client[MONGO_DB_NAME]


BITRATE = "currentBitrate"
LATENCY = "currentLatency"
BUFFER = "currentBuffer"
PLAYBACK_RATE = "currentPlaybackRate"

MEDIA_TYPE_VIDEO = "video"
MEDIA_TYPE_AUDIO = "audio"
MEDIA_TYPE_STREAM = "stream"

METRIC_REP_SWITCH_LIST = "RepSwitchList"


def get_result_dir() -> pathlib.PosixPath:
    path = pathlib.Path(FIGURE_DIR).joinpath(EXPERIMENT_ID)
    os.makedirs(path, exist_ok=True)
    return path


def write_metric(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def write_metric_with_timestamp(timestamp, data, filename):
    assert(len(timestamp) == len(data))

    result = {}
    for i in range(len(timestamp)):
        # as long as dash.js stores milliseconds, this is fine
        result[timestamp[i].isoformat()] = data[i]

    with open(filename, "w") as f:
        json.dump(result, f, indent=4)


"""
mediaType: {'audio', 'video', 'stream'}
metric: {'HttpList', 'DVRInfo', 'DroppedFrames',
         'BufferState', 'BufferLevel', 'SchedulingInfo',
         'RequestsQueue', 'ManifestUpdate', 'RepSwitchList'}
"""

def get_event_data(mediaType, metric: str) -> list:
    cursor = db["events-{}".format(EXPERIMENT_ID)].find({})
    events = []
    for c in cursor:
        for m in c.get("type"):
            events.append(m)

    event_data = []
    for e in events:
        if "metric" in e.keys():
            if e["metric"] == metric and e["mediaType"] == mediaType:
                event_data.append(e["value"])

    return event_data


def get_metric_data(metricKey: str) -> Tuple[list[datetime], list[float]]:
    cursor = db["metric-{}".format(EXPERIMENT_ID)].find({})
    metrics = []
    for c in cursor:
        for m in c.get("type"):
            if m["experimentID"] == EXPERIMENT_ID:
                metrics.append(m)

    timestamp = []
    data = []
    
    for m in metrics:
        epoch = m["time"]
        date_obj = datetime.strptime(epoch, '%Y-%m-%d %H:%M:%S:%f')

        if m[metricKey] != "" and m[metricKey] != None:
            data.append(float(m[metricKey]))
            timestamp.append(date_obj)
        else:
            data.append(0.0)
            timestamp.append(date_obj)

    assert(len(timestamp) == len(data))
    return timestamp, data


def plot_bitrate_switch_temporal():
    timestamp, bitrates = get_metric_data(BITRATE)

    rep_switch_events = get_event_data(MEDIA_TYPE_VIDEO, METRIC_REP_SWITCH_LIST)
    timestamp2 = []
    events = []
    for e in rep_switch_events:
        date_obj = datetime.strptime(e["t"], '%Y-%m-%dT%H:%M:%S.%fZ').astimezone(PST).strftime('%Y-%m-%d %H:%M:%S.%f')
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S.%f')
        timestamp2.append(date_obj)
        events.append(1)

    plt.plot(timestamp2, events, label="Rep Switch", linestyle='None', marker="x")
    plt.plot(timestamp, bitrates, label="bitrate (Kbps)")
    plt.legend(loc="upper left")
    plt.xlabel("Seconds")
    plt.ylabel("Playback bitrate (Kbps)")
    plt.savefig(get_result_dir().joinpath("bitrate_switch.png"))
    plt.close()

    write_metric_with_timestamp(timestamp, bitrates, get_result_dir().joinpath("bitrates.json"))
    write_metric(rep_switch_events, get_result_dir().joinpath("bitrate_switch.json"))


# def plot_latency_temporal():
#     timestamp, latency = get_metric_data(LATENCY)

#     plt.plot(timestamp, latency, label="Latency to Live (second)")
#     plt.legend(loc="upper left")
#     plt.xlabel("Seconds")
#     plt.ylabel("Playback live latency to Live (second)")
#     plt.savefig(FIGURE_DIR + EXPERIMENT_ID + "-latency" + ".png")
#     plt.close()


def plot_buffer_temporal():
    timestamp, buffer = get_metric_data(BUFFER)

    plt.plot(timestamp, buffer, label="Buffer (second)")
    plt.legend(loc="upper left")
    plt.xlabel("Seconds")
    plt.ylabel("Playback buffer (second)")
    plt.savefig(get_result_dir().joinpath("buffer.png"))
    plt.close()

    write_metric_with_timestamp(timestamp, buffer, get_result_dir().joinpath("buffer.json"))


def plot_playback_rate_temporal():
    timestamp, playback_rate = get_metric_data(PLAYBACK_RATE)

    plt.plot(timestamp, playback_rate, label="Playback rate")
    plt.legend(loc="upper left")
    plt.xlabel("Seconds")
    plt.ylabel("Playback rate")
    plt.savefig(get_result_dir().joinpath("playback_rate.png"))
    plt.close()

    write_metric_with_timestamp(timestamp, playback_rate, get_result_dir().joinpath("playback_rate.json"))


def plot_buffer_latency():
    timestamp, buffer = get_metric_data(BUFFER)
    timestamp, latency = get_metric_data(LATENCY)

    plt.plot(timestamp, buffer, label="Buffer (second)")
    plt.plot(timestamp, latency, label="Latency to Live (second)")

    plt.legend(loc="upper left")
    plt.xlabel("Seconds")
    plt.savefig(get_result_dir().joinpath("buffer-latency.png"))
    plt.close()

    write_metric_with_timestamp(timestamp, latency, get_result_dir().joinpath("playback_latency.json"))


def plot_bitrate_by_second():
    timestamp, bitrate = get_metric_data(BITRATE)
    result = defaultdict(list[float])
    for i in range(len(timestamp)):
        t = timestamp[i]
        b = bitrate[i]
        result[t.isoformat()].append(b)

    averaged_bitrate_by_second = []
    for k in result:
        averaged_bitrate_by_second.append(np.average(result[k]))

    plt.plot(averaged_bitrate_by_second)
    plt.savefig(get_result_dir().joinpath("bitrate_by_second.png"))
    plt.close()

    write_metric(averaged_bitrate_by_second, get_result_dir().joinpath("bitrate_by_second.json"))


def write_qoe():
    cursor = db["qoe-{}".format(EXPERIMENT_ID)].find({})
    qoe = []
    arms = []
    live_latency = []
    for c in cursor:
        for m in c.get("type"):
            if m == "reward_qoe":
                qoe.append(c["type"]["reward_qoe"])
            elif m == "arm":
                arms.append(c["type"]["arm"])
            elif m == "currentLiveLatency":
                live_latency.append(c["type"]["currentLiveLatency"])

    write_metric(qoe, get_result_dir().joinpath("qoe.json"))
    write_metric(arms, get_result_dir().joinpath("arms.json"))
    write_metric(live_latency, get_result_dir().joinpath("currentLiveLatency.json"))


def generate_plots(EXP_ID: str, ROUND_DURATION, TARGET_LATENCY, CONSTANT_VIDEO_BITRATE: int):
    global EXPERIMENT_ID
    EXPERIMENT_ID = EXP_ID

    plot_buffer_temporal()
    plot_bitrate_by_second()
    plot_bitrate_switch_temporal()
    plot_playback_rate_temporal()
    plot_buffer_latency()
    write_qoe()


if __name__ == "__main__":
    plot_buffer_temporal()
    plot_bitrate_switch_temporal()
    plot_bitrate_by_second()
    plot_playback_rate_temporal()
    plot_buffer_latency()
    write_qoe()
