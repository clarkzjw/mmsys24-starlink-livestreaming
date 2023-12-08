from pprint import pprint
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from dataclasses import dataclass
import subprocess
import os
import re
import time
import threading
import schedule
import sys
# from typing import List
import socket


app = Flask(__name__)
methods = ["POST"]

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Access-Control-Allow-Origin'

client = MongoClient("mongodb://starlink:starlink@mongo:27017/")
db = client["starlink"]


@dataclass
class PingMetric:
    timestamp: float
    seq_no: float
    rtt: float = 0.0

INTERFACE = os.getenv("INTERFACE")
PING_INTERVAL = os.getenv("LATENCY_TEST_INTERVAL_SECONDS", "1")


ping_metric = list[PingMetric]()
count = 0
ping_thread = None
last_value = -1
current_experiment_id = None


def py_ping(hostname: str) -> None:
    global count
    global last_value
    count += 1

    try:
        if not INTERFACE:
            output = subprocess.check_output(["ping", "-W", "1", "-c", "1", hostname])
        else:
            output = subprocess.check_output(["ping", "-I", INTERFACE, "-W", "1", "-c", "1", hostname])
        line = output.decode("utf-8")
        match = re.search(r"icmp_seq=(\d+).*time=(\d+\.\d+)", line)
        if match:
            rtt = float(match.group(2))
            pm = PingMetric(time.time(), count, rtt)
            last_value = rtt
            ping_metric.append(pm)
    
    except subprocess.CalledProcessError as e:
        print(e.output)
        pm = PingMetric(time.time(), count, last_value)
        ping_metric.append(pm)


@app.route("/qoe/", methods=methods)
@cross_origin()
def qoe():
    event = request.get_json()
    collection = "qoe-{}".format(current_experiment_id)
    db[collection].insert_one(event)

    return jsonify("Succeed")


@app.route("/event/<experimentID>", methods=methods)
@cross_origin()
def playback_event(experimentID):
    global current_experiment_id

    event = request.get_json()
    collection = "events-{}".format(experimentID)
    db[collection].insert_one(event)
    current_experiment_id = experimentID

    return jsonify("Succeed")


@app.route("/metric/<experimentID>", methods=methods)
@cross_origin()
def playback_metric(experimentID):
    global current_experiment_id
    
    metric = request.get_json()
    collection = "metric-{}".format(experimentID)
    db[collection].insert_one(metric)
    current_experiment_id = experimentID

    return jsonify("Succeed")


class StoppableThread(threading.Thread):
    def __init__(self, hostname):
        super().__init__()
        self.hostname = hostname
        self.stop_flag = False

    def run(self):
        addrs = [ str(i[4][0]) for i in socket.getaddrinfo(self.hostname, 80) ]
        if len(addrs) > 0:
            HOST = addrs[0]
        else:
            HOST = self.hostname

        while not self.stop_flag:
            py_ping(hostname=HOST)
            time.sleep(0.1)

    def stop(self):
        self.stop_flag = True


@app.route("/ping/<hostname>", methods=methods)
@cross_origin()
def start_ping(hostname):
    global ping_thread
    ping_thread = StoppableThread(hostname)
    ping_thread.start()
    return jsonify("Succeed")


@app.route("/ping/stop", methods=methods)
@cross_origin()
def stop_ping():
    global ping_metric
    global count
    if ping_thread:
        ping_thread.stop()
        ping_thread.join()
        ping_metric.clear()
        count = 0
        print("stopped")
    
    return jsonify("Succeed")


@app.route("/ping", methods=["GET"])
@cross_origin()
def get_ping_stats():
    if len(ping_metric) > 0:
        return jsonify(ping_metric[-1].rtt)
    else:
        return jsonify(0)
    

def print_ping_stats():
    print("Latest 10 latency tests results:")
    pprint(ping_metric[-10:])


schedule.every(10).seconds.do(print_ping_stats)


def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(0.1)


if __name__ == "__main__":
    if not INTERFACE:
        print("Environment variable INTERFACE is empty, default interface will be used for latency tests")

    print("Latency tests interval: {}s".format(PING_INTERVAL))

    p = threading.Thread(target=schedule_thread)
    p.start()

    app.run(host="0.0.0.0", port=8000)
