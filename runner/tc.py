import time
from datetime import datetime
import subprocess


HANDOVER_SECOND = [12, 27, 42, 57]
HANDOVER_DURATION = 1
ETHERNET = "eth0"


def get_handover_time() -> set:
    HANDOVER = []
    for t in HANDOVER_SECOND:
        for i in range(HANDOVER_DURATION + 1):
            HANDOVER.append(t - i if t - i >= 0 else t - i + 60)
            HANDOVER.append(t + i if t + i < 60 else t + i - 60)
    return set(HANDOVER)


def is_now_handover(now: int, handover: set) -> bool:
    if now in handover:
        return True
    return False


def set_delay():
    # https://stackoverflow.com/a/615757
    # https://www.baeldung.com/linux/throttle-bandwidth
    # https://gist.github.com/Lakshanz/19613830e5c6f233754e12b25408cc51
    # tc qdisc change dev eth0 root netem delay 100ms 1ms 25% loss 0%

    # Add root qdisc with a handle
    # tc qdisc change dev eth0 root handle 1: tbf rate 1kbit burst 16kbit latency 500ms
    # Add child qdisc with netem under the root
    # tc qdisc change dev eth0 parent 1:1 handle 10: netem delay 100ms 10ms 25% loss 50%

    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "root", "handle", "1:", "tbf", "rate", "1kbit", "burst", "16kbit", "latency", "500ms"])
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "100ms", "10ms", "25%", "loss", "50%"])


def tc_reset():
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "root", "handle", "1:", "tbf", "rate", "100mbit", "burst", "16kbit", "latency", "40ms"])
    subprocess.check_output(["tc", "qdisc", "change", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "40ms", "1ms", "25%", "loss", "0.1%"])


def tc_init():
    subprocess.check_output(["tc", "qdisc", "add", "dev", ETHERNET, "root", "handle", "1:", "tbf", "rate", "100mbit", "burst", "16kbit", "latency", "40ms" ])
    subprocess.check_output(["tc", "qdisc", "add", "dev", ETHERNET, "parent", "1:1", "handle", "10:", "netem", "delay", "40ms"])


def tc_del():
    subprocess.check_output(["tc", "qdisc", "del", "dev", ETHERNET, "root"])


def tc_thread():
    handover = get_handover_time()

    while True:
        now = datetime.now().second
        if is_now_handover(now, handover):
            set_delay()
        else:
            tc_reset()

        time.sleep(0.1)
        
if __name__ == "__main__":
    tc_init()
    handover = get_handover_time()

    while True:
        now = datetime.now().second
        if is_now_handover(now, handover):
            # print("now: {}, handover".format(now))
            set_delay()
        else:
            # print("now: {}, normal".format(now))
            tc_reset()

        time.sleep(0.1)
