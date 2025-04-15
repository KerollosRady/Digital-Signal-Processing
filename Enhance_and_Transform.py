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
from DFT_IDFT import calc_I_DFT, get_amp_phase_F
from utils import browse_file, Compare_Signals, ConvTest


fn_name = ['Smoothing',  # 0
           'Sharpening',  # 1
           'Folding & Delaying/Advancing',  # 2
           'Remove DC component in FD',  # 3
           'Convolve signal with Filter']  # 4

fn_cnt = len(fn_name)
x_input = [[], []] * fn_cnt
k_steps_entry = 0
k_smoothing_entry = 0
fold_bool = 0
canvas = [0] * fn_cnt
ax1, ax2 = [0] * fn_cnt, [0] * fn_cnt



def Fold_and_Shift(x, k, fold):
    res = x
    if fold:
        res[0].reverse()
        res[1].reverse()
    for i in range(len(res[0])):
        if fold:
            res[0][i] = -res[0][i]
        res[0][i] += k
    print(res[0])
    print(res[1])
    return res


def smoothing(x, k):
    print('Here')
    res = []
    pref = []
    for i in range(len(x)):
        z = (pref[i-1] if i > 0 else 0)
        pref.append(x[i] + z)

    for i in range(len(x) - k):
        mn = max(i - k//2 - 1, 0)
        mx = min(i + k//2, len(x) - 1)
        res.append(x[0] if mn == 0 else 0)
        res[i] += (pref[mx] - pref[mn])
        res[i] /= k
    print(res)
    return res


def convolution(x, h):
    res = [[], []]
    result_length = len(x[0]) + len(h[0]) - 1

    for n in range(result_length):
        res[0].append(x[0][0] + h[0][0] + n)
        res[1].append(0)
        for k in range(len(x[0])):
            if n - k >= 0 and n - k < len(h[0]):
                res[1][-1] += x[1][k] * h[1][n - k]
    return res
def convolution2(idx_x, x, idx_h, h):
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

def Derivative(x):
    d1 = [[], []]
    d2 = [[], []]
    for i in range(1, len(x[0])):
        d1[0].append(x[0][i])
        d1[1].append(x[1][i] - x[1][i-1])

        if i < len(x[0]) - 1:
            d2[0].append(x[0][i])
            d2[1].append(x[1][i+1] - 2*x[1][i] + x[1][i-1])
    return d1, d2


def update_plot(idx):
    x = copy.deepcopy(x_input[idx])
    print('Start', fn_name[idx])
    ax1[idx].cla()
    ax2[idx].cla()


    if idx == 0:
        k = int(k_smoothing_entry.get())
        res = smoothing(x[1], k)
        ax1[idx].plot(x_input[idx][0], x_input[idx][1])
        ax2[idx].plot([i for i in range(len(res))], res)

    elif idx == 1:
        d1, d2 = Derivative(x)
        ax1[idx].plot(x_input[idx][0], x_input[idx][1])
        ax2[idx].plot(d2[0], d2[1])

    elif idx == 2:
        k = int(k_steps_entry.get())
        f = fold_bool.get()

        res = Fold_and_Shift(x, k, f)
        # if f and k == 0:
        #     Compare_Signals('Output_fold.txt', res[0], res[1])
        ax1[idx].plot(x_input[idx][0], x_input[idx][1])
        ax2[idx].plot(res[0], res[1])

    elif idx == 3:
        res = calc_I_DFT('dft', x[1])
        amp, phase, F = get_amp_phase_F(res, 4)
        amp = amp[1:]
        phase = phase[1:]
        F = F[1:]
        ax1[idx].cla()
        ax1[idx].stem(F, amp)
        ax2[idx].stem(F, phase)
        ax1[idx].set_xlabel('Frequency')
        ax1[idx].set_ylabel('Amplitude')
        ax2[idx].set_xlabel('Frequency')
        ax2[idx].set_ylabel('Phase')

    elif idx == 4:
        h = x_input[idx + 1]
        res = convolution(x, h)
        # ConvTest(res[0], res[1])
        ax1[idx].stem(x_input[idx][0], x_input[idx][1])
        ax2[idx].stem(res[0], res[1])

    canvas[idx].draw()

def Enhance_and_Transform(tabs):
    time_domain = ttk.Frame(tabs)
    tabs.add(time_domain, text="Enhance_and_Transform")
    tabs.pack(fill="both", expand=True)
    inner_tab = ttk.Notebook(time_domain)

    tab = [0] * fn_cnt
    file_labels = [0] * (fn_cnt + 1)
    browse_buttons = [0] * (fn_cnt + 1)
    display_buttons = [0] * fn_cnt

    for i in range(fn_cnt+1):
        if i < fn_cnt:
            tab[i] = ttk.Frame(inner_tab)
            inner_tab.add(tab[i], text=fn_name[i])
            inner_tab.pack(fill="both", expand=True)
        j, txt = i, 'Browse Signal File'
        if j == fn_cnt:
            j, txt = j-1, 'Browse Filter File'

        file_labels[i] = ttk.Label(tab[j], text="")
        file_labels[i].pack()

        browse_buttons[i] = ttk.Button(tab[j], text=txt, command=lambda i=i: browse_file(file_labels[i], x_input, i, readBoth=True))
        browse_buttons[i].pack()

    global k_smoothing_entry, k_steps_entry, fold_bool, ax1, ax2

    k_smoothing_label = ttk.Label(tab[0], text='Enter k:')
    k_smoothing_label.pack()
    k_smoothing_entry = tk.Spinbox(tab[0], from_=0, to=1000, increment=1)
    k_smoothing_entry.pack()

    k_steps_label = ttk.Label(tab[2], text='Steps(k):')
    k_steps_label.pack()
    k_steps_entry = tk.Spinbox(tab[2], from_=-1000, to=1000, increment=1)
    k_steps_entry.pack()
    k_steps_entry.delete(0, tk.END)
    k_steps_entry.insert(0, 0)

    fold_bool = tk.BooleanVar()
    fold_box = tk.Checkbutton(tab[2], text='Fold', variable=fold_bool)
    fold_box.pack()

    for i in range(fn_cnt):
        display_buttons[i] = ttk.Button(tab[i], text="Display", command=lambda i=i: update_plot(i))
        display_buttons[i].pack()

    for i in range(fn_cnt):
        fig = Figure(figsize=(5, 4), dpi=100)
        ax1[i] = fig.add_subplot(121)
        ax2[i] = fig.add_subplot(122)

        canvas[i] = FigureCanvasTkAgg(fig, master=tab[i])
        canvas[i].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas[i].draw()
