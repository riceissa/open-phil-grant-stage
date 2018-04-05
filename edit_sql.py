#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import csv
import re


def main():
    d = {}
    with open("grant_stage_data.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            d[row['grant_url']] = row['grant_stage']

    with open("open-phil-grants.sql", "r") as f:
        for line in f:
            m = re.match(r"[^:]*'(https?:\/\/www\.openphilanthropy\.org[^']+)'", line)
            if m:
                for ending in ["),", ");"]:
                    if line.strip().endswith(ending):
                        print(line.strip()[:-2] + ",'" + d[m.group(1)] + "'" +
                              ending)
            else:
                print(line, end="")


if __name__ == "__main__":
    main()
