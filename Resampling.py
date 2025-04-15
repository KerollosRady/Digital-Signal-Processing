import math
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import copy
from Filtering import *
from utils import Compare_Signals

FilterType, labels_names, label, entry, tab, isConv, x_input = 0, 0, 0, 0, 0, 0, [0]
fig, ax1, ax2, canvas = 0, 0, 0, 0

def resample(x_idx_, x_val_, FS, FC1, StopBandAttenuation, TransitionBand, L, M):
    type = 'Low pass'
    x_idx = copy.deepcopy(x_idx_)
    x_val = copy.deepcopy(x_val_)
    if L != int(L) or M != int(M):
        print('L & M should be integers.')
        return
    L, M = int(L), int(M)
    if L == 0 and M == 0:
        print('L & M can\'t equal 0 together.')
        return

    if L != 0:
        st = x_idx[0]
        N = len(x_idx)
        x_tmp = [copy.deepcopy(x_idx), copy.deepcopy(x_val)]
        x_idx = []
        x_val = []
        for n in range(N * L):
            x_idx.append(st + n)
            x_val.append(x_tmp[1][n//L] if n % L == 0 else 0)

    idx, res = calc_h(type, StopBandAttenuation, FS, FC1, FC1, TransitionBand)
    idx_ = copy.deepcopy(idx)
    res_ = copy.deepcopy(res)
    idx, res = convolution(x_idx, x_val, idx_, res_)

    if M != 0:
        st = idx[0]
        N = len(res)
        x_res = copy.deepcopy(res)
        res = []
        idx = []
        for n in range(int(N // M)):
            idx.append(st + n)
            res.append(x_res[n*M])

    return x_idx, x_val, idx, res

def display():
    conv = True
    FS = float(entry[0].get())
    FC1 = float(entry[1].get())
    StopBandAttenuation = float(entry[2].get())
    TransitionBand = float(entry[3].get())
    L, M = float(entry[4].get()), float(entry[5].get())
    ax1.clear()
    ax2.clear()
    ax1.plot(x_input[0][0], x_input[0][1])

    idx_fltr, res_fltr, idx, res = resample(x_input[0][0], x_input[0][1], FS, FC1, StopBandAttenuation, TransitionBand, L, M)

    ax2.plot(idx, res)
    canvas.draw()
    print(idx)
    print(res)
    save_file('resampling_out', idx, res)
    # Compare_Signals('Sampling_Up.txt', idx, res)
    # Compare_Signals('Sampling_Down.txt', idx, res)
    # Compare_Signals('Sampling_Up_Down.txt', idx, res)

def Resampling(tabs):
    global FilterType, labels_names, label, entry, tab, isConv, x_input, \
        fig, ax1, ax2, canvas

    tab = ttk.Frame(tabs)
    tabs.add(tab, text="Resampling")
    tabs.pack(fill="both", expand=True)

    labels_names = ['Sampling frequency (FS): ', 'Cut of frequency (FC):',
                    'StopBandAttenuation:', 'TransitionBand:', 'Interpolation factor (L):', 'Decimation factor (M):']
    label = [0] * len(labels_names)
    entry = [0] * len(labels_names)
    for i in range(len(label)):
        label[i] = ttk.Label(tab, text=labels_names[i])
        label[i].pack()
        entry[i] = ttk.Spinbox(tab, from_=0, to=(74 if i == 3 else 10000))
        entry[i].pack()
        entry[i].insert(0, 50)

    # isConv = tk.BooleanVar()
    # checkbox = tk.Checkbutton(tab, text="Convolve with signal", variable=isConv)
    # checkbox.pack()
    file_label = ttk.Label(tab, text='')
    browse_button = ttk.Button(tab, text='Browse', command=lambda: browse_file(file_label, x_input, 0, readBoth=True))
    file_label.pack()
    browse_button.pack()
    display_button = ttk.Button(tab, text='Display', command=display)
    display_button.pack()

    fig = Figure(figsize=(5, 4), dpi=100)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()
