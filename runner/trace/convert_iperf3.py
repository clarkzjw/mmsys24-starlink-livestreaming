import os
import json
import itertools
from pprint import pprint
from pathlib import Path


def duplicate_object_pairs_hook(pairs):
    def _key(pair):
        (k, v) = pair
        return k
    def gpairs():
        for (k, group) in itertools.groupby(pairs, _key):
            ll = [v for (_, v) in group]
            (v, *extra) = ll
            yield (k, ll if extra else v)
    return dict(gpairs())


def convert_iperf3_csv(dir: str, f: str):
    iperf3_filename = Path(dir).joinpath(f)
    try:
        with open(iperf3_filename, "r") as f:
            with open(Path(dir).joinpath("iperf3-trace.csv"), "w") as outcsv:
                data = json.loads(f.read(), object_pairs_hook=duplicate_object_pairs_hook)
                for round in data["intervals"]:
                    stream = round["streams"]
                    for s in stream:
                        if s["sender"] == False:
                            recv_mbps = float(s["bits_per_second"])/1000000
                            since = float(s["start"])
                            outcsv.write("{},{}\n".format(since, recv_mbps))
            
    except json.decoder.JSONDecodeError:
        print("JSONDecodeError: ", iperf3_filename)
        return
    except OSError:
        print("FileNotFoundError: ", iperf3_filename)
        return


if __name__ == "__main__":
    path = Path("./test")
    for dirpath, dirnames, files in os.walk(path):
        print(dirpath)
        if len(files) != 0:
            for f in files:
                if f.endswith(".json") and f.startswith("iperf3"):
                        convert_iperf3_csv(dirpath, f)
