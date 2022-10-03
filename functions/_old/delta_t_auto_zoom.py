"""Script for plotting separate plots for specific pairs of pixels.

Works with a single data file.

This script utilizes an unpacking module used specifically for the LinoSPAD2
data output.

The output is saved in the `results/delta_t` directory, in the case there is
no such folder, it is created where the data are stored.

This file can also be imported as a module and contains the following
functions:

    * plot_delta_separate - plots delta t for each pair of pixels in
    the range of 251-255

"""

import os
import glob
from tqdm import tqdm
import numpy as np
from matplotlib import pyplot as plt
from functions import unpack as f_up


def plot_delta_auto_zoom(path, pix, lines_of_data: int = 512):
    '''Plots delta t for each pair of pixels in the given range.

    Parameters
    ----------
    path : str
        Path to data file.
    pix : array-like
        Array of indices of 5 pixels for analysis.
    lines_of_data : int
        Number of data points per acq cycle per pixel in the file. The default
        is 512.

    Returns
    -------
    None.

    '''

    os.chdir(path)

    filename = glob.glob('*.dat*')[0]

    print("\nWorking on {}, plotting a zoom on delta t peaks\n"
          .format(filename))

    data = f_up.unpack_binary_flex(filename, lines_of_data)

    data_1 = data[pix[0]]  # 1st pixel
    data_2 = data[pix[1]]  # 2nd pixel
    data_3 = data[pix[2]]  # 3d pixel
    data_4 = data[pix[3]]  # 4th pixel
    data_5 = data[pix[4]]  # 5th pixel

    pixel_numbers = np.arange(pix[0], pix[-1]+1, 1)

    all_data = np.vstack((data_1, data_2, data_3, data_4, data_5))

    plt.rcParams.update({'font.size': 20})
    plt.ioff()

    for q in range(5):
        for w in range(5):
            if w <= q:
                continue

            data_pair = np.vstack((all_data[q], all_data[w]))

            minuend = len(data_pair)-1  # i=255
            lines_of_data = len(data_pair[0])
            subtrahend = len(data_pair)  # k=254
            timestamps = 512  # lines of data in the acq cycle

            output = []

            for i in tqdm(range(minuend)):
                acq = 0  # number of acq cycle
                for j in range(lines_of_data):
                    if data_pair[i][j] == -1:
                        continue
                    if j % 512 == 0:
                        acq = acq + 1  # next acq cycle
                    for k in range(subtrahend):
                        if k <= i:
                            continue  # to avoid repetition: 2-1, 153-45 etc.
                        for p in range(timestamps):
                            n = 512*(acq-1) + p
                            if data_pair[k][n] == -1:
                                continue
                            elif data_pair[i][j] - data_pair[k][n] > 2e3:
                                continue
                            elif data_pair[i][j] - data_pair[k][n] < -1e5:
                                continue
                            else:
                                output.append(data_pair[i][j]
                                              - data_pair[k][n])
            try:
                bins = np.arange(np.min(output), np.max(output), 17.857*100)
            except Exception:
                continue

            n, b, p = plt.hist(output, bins=bins)
            plt.close()

            # find position of the histogram peak
            try:
                n_max = np.argmax(n)
                arg_max = (bins[n_max] + bins[n_max + 1]) / 2
            except Exception:
                arg_max = None
                pass

            output = []

            if arg_max is None:
                continue

            for i in tqdm(range(minuend), desc='Working on the zoom'):
                acq = 0  # number of acq cycle
                for j in range(lines_of_data):
                    if data_pair[i][j] == -1:
                        continue
                    if j % 512 == 0:
                        acq = acq + 1  # next acq cycle
                    for k in range(subtrahend):
                        if k <= i:
                            continue  # to avoid repetition: 2-1, 153-45 etc.
                        for p in range(timestamps):
                            n = 512*(acq-1) + p
                            if data_pair[k][n] == -1:
                                continue
                            elif data_pair[i][j] - data_pair[k][n] > (int(arg_max)
                                                                      + 1000):
                                continue
                            elif data_pair[i][j] - data_pair[k][n] < (int(arg_max)
                                                                      - 1000):
                                continue
                            else:
                                output.append(data_pair[i][j]
                                              - data_pair[k][n])

            if "Ne" and "540" in path:
                chosen_color = "seagreen"
            elif "Ne" and "656" in path:
                chosen_color = "orangered"
            elif "Ar" in path:
                chosen_color = "mediumslateblue"
            else:
                chosen_color = "salmon"

            try:
                bins = np.arange(np.min(output), np.max(output), 17.857)
            except Exception:
                continue

            plt.figure(figsize=(16, 10))
            plt.xlabel('\u0394t [ps]')
            plt.ylabel('Timestamps [-]')
            n, b, p = plt.hist(output, bins=bins, color=chosen_color)

            arg_max = format((bins[n_max] + bins[n_max + 1]) / 2, ".2f")

            plt.title('{filename}\nPeak position: {peak}\nPixels {p1}-{p2}'
                      .format(filename = filename, peak = arg_max,
                              p1=pixel_numbers[q], p2=pixel_numbers[w]))

            try:
                os.chdir("results/delta_t/zoom")
            except Exception:
                os.mkdir("results/delta_t/zoom")
                os.chdir("results/delta_t/zoom")
            plt.savefig("{name}_pixels {p1}-{p2}.png".format(name=filename,
                                                        p1=pixel_numbers[q],
                                                        p2=pixel_numbers[w]))
            plt.pause(0.1)
            plt.close()
            os.chdir("../../..")