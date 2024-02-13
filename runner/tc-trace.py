import time
from datetime import datetime
import subprocess


ETHERNET = "eth0"


def set_delay():
    # https://stackoverflow.com/a/615757
    # https://www.baeldung.com/linux/throttle-bandwidth
    # https://gist.github.com/Lakshanz/19613830e5c6f233754e12b25408cc51
    # tc qdisc change dev eth0 root netem delay 100ms 1ms 25% loss 0%

    # Add root qdisc with a handle
    # tc qdisc change dev eth0 root handle 1: tbf rate 1kbit burst 16kbit latency 500ms
    # Add child qdisc with netem under the root
    # tc qdisc change dev eth0 parent 1:1 handle 10: netem delay 100ms 10ms 25% loss 50%

    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "root", "handle", "1:", "tbf", "rate", "50mbit", "burst", "16kbit", "latency", "100ms"])
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "100ms", "10ms", "25%", "loss", "1%"])


def set_static_delay(rtt: float):
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "root", "handle", "1:", "tbf", "rate", "50mbit", "burst", "16kbit", "latency", "100ms"])
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "100ms", "10ms", "25%", "loss", "1%"])


def tc_reset():
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "root", "handle", "1:", "tbf", "rate", "100mbit", "burst", "16kbit", "latency", "40ms"])
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "40ms", "1ms", "25%", "loss", "0.1%"])


def tc_init():
    subprocess.check_output(["tc", "qdisc", "add", "dev", ETHERNET, "root", "handle", "1:", "tbf", "rate", "100mbit", "burst", "16kbit", "latency", "40ms" ])
    subprocess.check_output(["tc", "qdisc", "add", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "40ms"])


def tc_del():
    subprocess.check_output(["tc", "qdisc", "del", "dev", ETHERNET, "root"])

        
if __name__ == "__main__":
    tc_init()

    # read the entire latency trace into memory

    # set the interval to 0.1 seconds
    INTERVAL = 0.1

    # get init time
    init = datetime.now()

    while True:
        time.sleep(INTERVAL)

        # get the current time
        now = datetime.now()
        
        # get the relative time
        relative = now - init
        
        # TODO
        # get the latency trace with the closest time from the trace
        rtt = 0

        set_static_delay(rtt)
