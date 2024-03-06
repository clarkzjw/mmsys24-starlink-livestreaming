import csv
import math
from pathlib import Path


filename = "./irtt/seychelles-irtt-10ms-1h-2024-01-30-01-00-00.csv"
with open(filename, "r") as trace:
    reader = csv.reader(trace)
    count = 0
    init_time = 0
    previous_time = 0
    with open("trace.csv", "w", newline='') as outcsv: 
        writer = csv.DictWriter(outcsv, fieldnames = ["since", "relative_seconds", "rtt"])
        writer.writeheader()
        
        for row in reader:
            if count == 0:
                count += 1
                continue
            if count == 1:
                previous_time = int(row[0])
                init_time = int(row[0])
            count += 1
            relative = round((int(row[0]) - previous_time) / 1000000000, 3)
            since = round((int(row[0]) - init_time) / 1000000000, 3)
            writer.writerows([{"since": since, "relative_seconds": relative, "rtt": row[1]}])
            previous_time = int(row[0])
        print("Done")
