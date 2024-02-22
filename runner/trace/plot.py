import os
import re
from pathlib import Path
import matplotlib.pyplot as plt


def time_series_plot(filename: str, seq_list: list[int], rtt_list: list[float]) -> None:
    assert(len(seq_list) == len(rtt_list))

    fig = plt.figure(figsize =(21, 7))
    ax = fig.add_subplot(111)

    ax.plot(seq_list, rtt_list, '.')
    plt.title(filename)
    plt.tight_layout()
    plt.savefig(str(filename) + ".png")
    plt.close()


def plot(filename: str):
    if Path(filename).is_file() == False:
        print("{} doesn't exist".format(filename))
        exit(1)

    print(filename)
    with open(filename, "r") as f:
        count = 0
        seq_list = []
        rtt_list = []
        for line in f.readlines():
            match = re.search(r"\[(\d+\.\d+)\].*icmp_seq=(\d+).*time=(\d+(\.\d+)?)", line)
            if match:
                count += 1
                timestamp = float(match.group(1))
                seq = int(match.group(2))
                rtt = float(match.group(3))
                seq_list.append(seq)
                rtt_list.append(rtt)

        assert(len(seq_list) == len(rtt_list))
        print(len(seq_list))
        time_series_plot(filename, seq_list, rtt_list)


if __name__ == "__main__":
    path = Path("/home/clarkzjw/test/")
    for dirpath, dirnames, files in os.walk(path):
        if len(files) != 0:
            for f in files:
                if f.startswith("ping-") and f.endswith(".txt"):
                    plot(path.joinpath(f))
