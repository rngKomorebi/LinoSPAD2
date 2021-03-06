# =============================================================================
# Unpack data from .txt files; return 2D matrix (256 x 512*#ofcycles) of
# timestamps
# =============================================================================
import numpy as np

# The .txt output of the LinoSPAD2 is a single column of data, where first 512lines are
# the data from the 1st pixel collected during the first cycle of the data acquisition,
# next 512 lines (2*512:2*512+512) - 2nd pixel and so on. Lines 256*512:256*512+512 are
# the data from the 1st pixel collected during the 2nd cycle.


def unpack(filename):

    Data = np.genfromtxt(filename)
    Data_matrix = np.zeros((256, int(len(Data)/256)))  # rows=#pixels, cols=#cycles

    noc = len(Data)/512/256  # number of cycles, 512 data lines per pixel per cycle,
    # 256 pixels

    # =========================================================================
    # Unpack data from the txt, which is a Nx1 array, into a 256x#cycles matrix
    # using two counters. When i (number of the pixel) reaches the 255
    # (256th pixel), move k one step further - second data acquisition cycle,
    # when the algorithm goes back to the 1st pixel and writes the data right
    # next to the data from previous cycle.
    # =========================================================================
    k = 0
    while k != noc:
        i = 0
        while i < 256:
            Data_matrix[i][k*512:k*512+512] = Data[(i+256*k)*512:
                                                   (i+256*k)*512+512]-2**31
            i = i+1
        k = k+1

    Data_matrix = Data_matrix*17.857  # 2.5 ns from TDC 400 MHz clock read
    # out 140 bins from 35 elements of the delay line - average bin size
    # is 17.857 ps

    # Cut the nonscence and insert -1 where there is no timestamp
    for i in range(len(Data_matrix)):
        Data_matrix[i][np.where(Data_matrix[i] < 0)[0]] = -1

    return Data_matrix
