import os
import time
import subprocess

from datetime import datetime
from pprint import pprint

ETHERNET = "eth0"
INTERVAL = os.getenv("INTERVAL", 0.01)


def set_static_delay(rtt: int):
    loss = 1
    if rtt == 0 or rtt == -1:
        rtt = 100
        loss = 100

    # tc class add dev eth0 parent 1: classid 1:1 htb rate 100mbit ceil 10mbit
    subprocess.check_output(["tc", "class", "change", "dev", ETHERNET, "parent", "1:", "classid", "1:1", "htb", "rate", "100mbit", "ceil", "20mbit"])
            
    # tc qdisc add dev eth0 parent 1:1 handle 10: netem delay 100ms
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "{}ms".format(rtt), "loss", "{}%".format(loss)])


def tc_reset():
    subprocess.check_output(["tc", "class", "change", "dev", ETHERNET, "parent", "1:", "classid", "1:1", "htb", "rate", "100mbit", "ceil", "50mbit"])
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "40ms", "loss", "0.1%"])
    

def tc_init():
    subprocess.check_output(["tc", "class", "add", "dev", ETHERNET, "parent", "1:", "classid", "1:1", "htb", "rate", "100mbit", "ceil", "50mbit"])
    subprocess.check_output(["tc", "qdisc", "add", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "40ms", "loss", "0.1%"])
    

def tc_del():
    subprocess.check_output(["tc", "qdisc", "del", "dev", ETHERNET, "root"])

        
if __name__ == "__main__":
    tc_init()

    # read the entire latency trace into memory
    latency_trace = {}
    with open("/trace/trace.csv", "r") as f:
        count = 0
        for line in f:
            if count == 0:
                count += 1
                continue
            since, relative, rtt = line.strip("\n").split(",")
            latency_trace[since] = int(float(rtt))
            count += 1
            
    # get init time
    init = datetime.now()

    while True:
        time.sleep(float(INTERVAL))

        # get the current time
        now = datetime.now()
        
        # get the relative time
        relative = now - init
        
        # get the latency trace with the closest time from the trace
        closest = min(latency_trace, key=lambda x: abs(float(x) - relative.total_seconds()))
        rtt = latency_trace[closest]  
        print(closest, rtt)     
        
        set_static_delay(rtt)
