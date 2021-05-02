import csv
from collections import namedtuple
from pathlib import Path

RESULTS_PATH = Path("results/results.csv")

Result = namedtuple(
    "Result", ["name", "req", "lt50", "lt75", "lt90", "lt_avg", "es", "er", "et"]
)


def render():
    with open(RESULTS_PATH) as csvfile:
        results = [
            Result(name, round(int(req) / 15), *row)
            for name, req, *row in csv.reader(csvfile)
        ]

    with open("README.md", mode="w") as readmefile:
        readmefile.write("\n".join([str(result) for result in results]))


if __name__ == "__main__":
    render()
