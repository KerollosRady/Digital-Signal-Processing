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
from utils import browse_file, save_file, Compare_Signals

FilterType, labels_names, label, entry, tab, isConv, x_input = 0, 0, 0, 0, 0, 0, [0]
fig, ax1, ax2, canvas = 0, 0, 0, 0


def convolution(idx_x, x, idx_h, h):
    x_dic = {}
    h_dic = {}
    res_dic = {}
    for i in range(len(idx_x)):
        x_dic[idx_x[i]] = x[i]
    for i in range(len(idx_h)):
        h_dic[idx_h[i]] = h[i]

    min1, min2 = int(min(x_dic)), int(min(h_dic))
    max1, max2 = int(max(x_dic)), int(max(x_dic))
    mn, mx = min(min1, min2), max(max1, max2)

    for i in range(min1+min2, max1+max2 + 1):
        res_dic[i] = 0.0
        for k in range(mn, mx+1):
            if k > max1 or i-min2 < k:
                break
            res_dic[i] += x_dic.get(k, 0.0) * h_dic.get(i-k, 0.0)

    idx = list(res_dic.keys())
    res = list(res_dic.values())

    while res[-1] == 0:
        idx.pop(-1), res.pop(-1)
    while res[0] == 0:
        idx.pop(0), res.pop(0)
    return idx, res


def get_filter_name(StopBandAttenuation):
    if StopBandAttenuation <= 21:
        return 'Rectangular'
    if StopBandAttenuation <= 44:
        return 'Hanning'
    if StopBandAttenuation <= 53:
        return 'Hamming'
    if StopBandAttenuation <= 74:
        return 'Blackman'


def get_C(filter_name):
    if filter_name == 'Rectangular':
        return 0.9
    if filter_name == 'Hanning':
        return 3.1
    if filter_name == 'Hamming':
        return 3.3
    if filter_name == 'Blackman':
        return 5.5

def test_output(filter_type, idx, res, conv):
    if not conv:
        if filter_type == 'Low pass':
            Compare_Signals('LPFCoefficients.txt', idx, res)
        elif filter_type == 'High pass':
            Compare_Signals('HPFCoefficients.txt', idx, res)
        elif filter_type == 'Band pass':
            Compare_Signals('BPFCoefficients.txt', idx, res)
        elif filter_type == 'Band stop':
            Compare_Signals('BSFCoefficients.txt', idx, res)
    else:
        if filter_type == 'Low pass':
            Compare_Signals('ecg_low_pass_filtered.txt', idx, res)
        elif filter_type == 'High pass':
            Compare_Signals('ecg_high_pass_filtered.txt', idx, res)
        elif filter_type == 'Band pass':
            Compare_Signals('ecg_band_pass_filtered.txt', idx, res)
        elif filter_type == 'Band stop':
            Compare_Signals('ecg_band_stop_filtered.txt', idx, res)


def get_W(filter_name, n, N):
    if filter_name == 'Rectangular':
        return 1
    if filter_name == 'Hanning':
        return 0.5 + 0.5*np.cos(2*np.pi * n / N)
    if filter_name == 'Hamming':
        return 0.54 + 0.46*np.cos(2*np.pi * n / N)
    if filter_name == 'Blackman':
        return 0.42 + 0.5*np.cos(2*np.pi*n/(N - 1)) + 0.08*np.cos(4*np.pi*n/(N - 1))


def get_hD(filter_type, _FC1, _FC2, n):
    nwc1 = n * 2*np.pi*_FC1
    nwc2 = n * 2*np.pi*_FC2
    if filter_type == 'Low pass':
        if n == 0:
            return 2 * _FC1
        return 2 * _FC1 * np.sin(nwc1)/nwc1
    if filter_type == 'High pass':
        if n == 0:
            return 1 - 2*_FC1
        return -2*_FC1*np.sin(nwc1)/nwc1
    if filter_type == 'Band pass':
        if n == 0:
            return 2*(_FC2 - _FC1)
        return 2 * _FC2 * np.sin(nwc2)/nwc2 - 2 *_FC1*np.sin(nwc1)/nwc1
    if filter_type == 'Band stop':
        if n == 0:
            return 1 - 2 * (_FC2 - _FC1)
        return 2 * _FC1 * np.sin(nwc1)/nwc1 - 2 * _FC2 * np.sin(nwc2)/nwc2


def get_FC(filter_type, FC1, FC2, FS, TransitionBand):
    _FC1, _FC2 = 0, 0
    if filter_type == 'Low pass':
        _FC1 = FC1 + TransitionBand / 2
    elif filter_type == 'High pass':
        _FC1 = FC1 - TransitionBand / 2
    elif filter_type == 'Band pass':
        _FC1 = FC1 - TransitionBand / 2
        _FC2 = FC2 + TransitionBand / 2
    elif filter_type == 'Band stop':
        _FC1 = FC1 + TransitionBand / 2
        _FC2 = FC2 - TransitionBand / 2
    _FC1 /= FS
    _FC2 /= FS
    return _FC1, _FC2


def calc_h(filter_type, StopBandAttenuation, FS, FC1, FC2, TransitionBand):
    filter_name = get_filter_name(StopBandAttenuation)
    N = get_C(filter_name) * FS / TransitionBand
    N = int(math.ceil(N))
    if N % 2 == 0:
        N += 1
    idx = [i for i in range(- (N//2), N//2 + 1)]
    h = []
    _FC1, _FC2 = get_FC(filter_type, FC1, FC2, FS, TransitionBand)

    for n in range(N//2 + 1):
        hD = get_hD(filter_type, _FC1, _FC2, n)
        w = get_W(filter_name, n, N)
        h.append(hD * w)
    h = h[1:][::-1] + h
    return idx, h

def display():
    type = FilterType.get()
    conv = isConv.get()
    FS = float(entry[0].get())
    FC1 = float(entry[1].get())
    FC2 = float(entry[2].get())
    StopBandAttenuation = float(entry[3].get())
    TransitionBand = float(entry[4].get())
    idx, res = calc_h(type, StopBandAttenuation, FS, FC1, FC2, TransitionBand)
    ax1.cla()
    ax2.cla()
    if conv:
        ax1.plot(x_input[0][0], x_input[0][1])
        idx_ = copy.deepcopy(idx)
        res_ = copy.deepcopy(res)
        idx, res = convolution(x_input[0][0], x_input[0][1], idx_, res_)

    ax2.plot(idx, res)
    canvas.draw()
    save_file(f'{type}_filter_out', idx, res)
    # test_output(type, idx, res, conv)

def Filtering(tabs):
    global FilterType, labels_names, label, entry, tab, isConv, x_input, \
        fig, ax1, ax2, canvas

    tab = ttk.Frame(tabs)
    tabs.add(tab, text="Filtering")
    tabs.pack(fill="both", expand=True)

    filter_types = ['Low pass', 'High pass', 'Band pass', 'Band stop']
    FilterType = ttk.Combobox(tab, values=filter_types, state="readonly")
    FilterType.set("Select Filter Type")
    FilterType.pack(pady=10)
    FilterType.bind("<<ComboboxSelected>>")
    labels_names = ['Sampling frequency (FS): ', 'Cut of frequency (FC1):', 'Cut of frequency (FC2):', 'StopBandAttenuation:', 'TransitionBand:']
    label = [0] * len(labels_names)
    entry = [0] * len(labels_names)
    for i in range(len(label)):
        label[i] = ttk.Label(tab, text=labels_names[i])
        label[i].pack()
        entry[i] = ttk.Spinbox(tab, from_=0, to=(74 if i == 3 else 10000))
        entry[i].pack()
        entry[i].insert(0, 50)

    isConv = tk.BooleanVar()
    checkbox = tk.Checkbutton(tab, text="Convolve with signal", variable=isConv)
    checkbox.pack()
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
