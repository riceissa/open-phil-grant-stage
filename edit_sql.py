#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import csv
import re


def main():
    d = {}
    with open("data.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            d[row['grant_url']] = (row['grant_stage'], row['grant_review_process'])

    with open("open-phil-grants.sql", "r") as f:
        for line in f:
            m = re.match(r"[^:]*'(https?:\/\/www\.openphilanthropy\.org[^']+)'", line)
            if m:
                for ending in ["),", ");"]:
                    if line.rstrip().endswith(ending):
                        stage, process = d[m.group(1)]
                        print(line.rstrip()[:-2] + ",'" + stage + "'" +
                              ",'" + process + "'" + ending)
            elif line.rstrip().endswith(") values"):
                l = line.rstrip()
                print(l[:-len(") values")] + ", grant_stage, grant_review_process) values")
            else:
                print(line, end="")


if __name__ == "__main__":
    main()
