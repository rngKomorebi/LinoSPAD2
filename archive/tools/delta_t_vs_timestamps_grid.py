"""Script for plotting a grid 4x4 of delta t vs timestamps for different
pairs of pixels.

"""

import glob
import os

import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm

from functions import unpack as f_up

path = (
    "C:/Users/bruce/Documents/Quantum astrometry/LinoSPAD/Software/Data/"
    "Ar lamp/FW 2208"
)

os.chdir(path)

filename = glob.glob("*.dat*")[0]

data = f_up.unpack_binary_512(filename)

data_1 = data[156]
data_2 = data[157]
data_3 = data[158]
data_4 = data[159]
data_5 = data[160]

pixel_numbers = np.arange(156, 161, 1)

all_data = np.vstack((data_1, data_2, data_3, data_4, data_5))

plt.rcParams.update({"font.size": 20})
fig, axs = plt.subplots(4, 4, figsize=(24, 24))
plt.ioff()

y_max_all = 0

for q in range(5):
    for w in range(5):
        if w <= q:
            continue

        data_pair = np.vstack((all_data[q], all_data[w]))

        minuend = len(data_pair) - 1  # i=255
        lines_of_data = len(data_pair[0])
        subtrahend = len(data_pair)  # k=254
        timestamps = 512  # lines of data in the acq cycle

        output = []
        data_for_hist = []

        for i in tqdm(range(minuend)):
            acq = 0  # number of acq cycle
            for j in range(lines_of_data):
                if data_pair[i][j] == -1:
                    continue
                if j % 512 == 0:
                    acq = acq + 1  # next acq cycle
                    if acq > 1:
                        continue
                for k in range(subtrahend):
                    if k <= i:
                        continue  # to avoid repetition: 2-1, 153-45 etc.
                    for p in range(timestamps):
                        n = 512 * (acq - 1) + p
                        if data_pair[k][n] == -1:
                            continue
                        elif data_pair[i][j] - data_pair[k][n] > 3.5e3:
                            continue
                        elif data_pair[i][j] - data_pair[k][n] < -3.5e3:
                            continue
                        else:
                            output.append(data_pair[i][j] - data_pair[k][n])
                            # save the used timestamps
                            data_for_hist.append(data_pair[i][j])

        axs[q][w - 1].set_xlabel("Timestamp [ps]")
        axs[q][w - 1].set_ylabel("\u0394t [ps]")
        axs[q][w - 1].hist2d(data_for_hist, output, bins=(196, 196))

        axs[q][w - 1].set_title(
            "Pixels {p1}-{p2}".format(p1=pixel_numbers[q], p2=pixel_numbers[w])
        )
        axs[q][w - 1].set_ylim(-3.5e3, 3.5e3)

        try:
            os.chdir("results/delta_t vs timestamps")
        except Exception:
            os.mkdir("results/delta_t vs timestamps")
            os.chdir("results/delta_t vs timestamps")
        fig.tight_layout()  # for perfect spacing between the plots
        plt.savefig("{name}_delta_t_ts_grid.png".format(name=filename))
        os.chdir("../..")
