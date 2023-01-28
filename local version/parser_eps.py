import re
from matplotlib import pyplot as plt
import os

def drawACC4season(parsed, stock):
    times = [p[4:8] for p in parsed]
    x = [i for i in range(3, len(parsed))]
    EPSs = [float(p[-5:]) for p in parsed]
    acc_ESPs = []
    tmp = sum(EPSs[:3])
    for i in range(3, len(EPSs)):
        tmp += EPSs[i]
        acc_ESPs.append(tmp)
        tmp -= EPSs[i - 3]
    plt.bar(x, acc_ESPs)
    plt.title(stock)
    plt.ylabel("accumulate 4 season ESP")
    plt.xlabel("time")
    plt.xticks(x, times[3:], rotation=90)
    ax = plt.gca()
    ax.xaxis.set_major_locator(plt.MultipleLocator(4))
    plt.savefig(f"EPS_figs/{stock}_EPS_image.jpg")
    plt.cla()

def parsing(stock):
    with open(f"EPS_files/{stock}_EPS.txt", "r") as f:
        data = f.read()
    parsed = re.findall(r"\(Q\d\s\d{4}\)\s-?\d\.\d\d", data)
    if len(parsed) == 0:
        return None, None
    parsed_set = set(parsed)
    if len(parsed) == len(parsed_set):
        parsed.reverse()
    else:
        parsed = sorted(parsed_set, key=lambda x: (int(x[4:8]), int(x[2])))
    return (parsed, stock)

for f in os.listdir("EPS_files"):
    parsed, stock = parsing(f[:-8])
    if parsed is not None:
        drawACC4season(parsed, stock)
