import os
import re
import csv
import matplotlib.pyplot as plt
from pathlib import Path


def time_series_plot(filename: str, seq_list: list[int], rtt_list: list[float]) -> None:
    assert(len(seq_list) == len(rtt_list))

    fig = plt.figure(figsize =(21, 7))
    ax = fig.add_subplot(111)

    ax.plot(seq_list, rtt_list, '.')
    # ax.set_xlim(0, len(seq_list))
    plt.title(filename)
    plt.tight_layout()
    plt.savefig(str(filename) + ".png")
    plt.close()


def plot(filename: str):
    if Path(filename).is_file() == False:
        print("{} doesn't exist".format(filename))
        exit(1)

    print(filename)
    count = 0
    with open(filename, "r") as csvreader:
        reader = csv.reader(csvreader)
        count = 0
        seq_list = []
        rtt_list = []
        for row in reader:
            if count == 0:
                count += 1
                continue
            count += 1
            seq_list.append(float(row[0]))
            rtt_list.append(float(row[2]))

        assert(len(seq_list) == len(rtt_list))
        print(len(seq_list))
        time_series_plot(filename, seq_list, rtt_list)


if __name__ == "__main__":
    plot("./trace.csv")
