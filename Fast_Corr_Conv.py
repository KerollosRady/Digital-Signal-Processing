from tkinter import ttk
from matplotlib.figure import Figure
from tkinter import filedialog
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import os
import copy
from DFT_IDFT import calc_I_DFT
from utils import browse_file, Compare_Signals, ConvTest


x_input = [[], []] * 4
ax = [0] * 4
canvas = [0] * 2
corr_table = 0

def fast_convolution(idx1_, x_, idx2_, h_, update=False):

    idx1 = copy.deepcopy(idx1_)
    x = copy.deepcopy(x_)
    idx2 = copy.deepcopy(idx2_)
    h = copy.deepcopy(h_)

    L = len(x) + len(h) - 1
    while len(x) < L:
        x.append(0)
        idx1.append(idx1[-1] + 1)
    while len(h) < L:
        h.append(0)
        idx2.append(idx2[-1] + 1)

    X = calc_I_DFT('dft', x)
    H = calc_I_DFT('dft', h)
    Y = []
    for i in range(len(X)):
        Y.append(X[i] * H[i])
    res = calc_I_DFT('idft', Y)

    idx = [0] * len(res)
    for i in range(len(res)):
        idx[i] = min(idx1[0], idx2[0]) + i
        res[i] = round(res[i].real, 5)
    if update:
        ax[0].cla()
        ax[0].plot(idx1, x, label='Signal 1')
        ax[0].plot(idx2, h, label='Signal 2 (Filter)')
        ax[1].cla()
        ax[1].plot(idx, res)
        ax[0].legend()
        canvas[0].draw()
    # ConvTest(idx, res)
    return idx, res

def fast_correlation(x1, x2, update=False):
    if update:
        ax[2].clear()
        ax[3].clear()
        for row in corr_table.get_children():
            corr_table.delete(row)
    N = len(x1)

    n = [i for i in range(N)]

    dft_x1 = calc_I_DFT('dft', x1)
    dft_x2 = calc_I_DFT('dft', x2)

    res = [0] * N
    for i in range(N):
        res[i] = np.conj(dft_x1[i]) * (dft_x2[i])

    res = calc_I_DFT('idft', res)

    for i in range(N):
        res[i] = round(res[i].real/N, 5)
        corr_table.insert("", "end", values=(n[i], res[i]))
    if update:
        ax[2].plot(n, x1, label='Signal 1')
        ax[2].plot(n, x2, label='Signal 2')
        ax[3].plot(n, res)
        ax[2].legend()
        canvas[1].draw()
    # Compare_Signals('Corr_Output.txt', n, res)
    return res

def Build(tabs):

    file_label = [0] * 4
    browse_button = [0] * 4
    display_button = [0] * 2

    idx = -1
    for tab_idx in range(2):
        for sgnl_idx in range(2):
            idx += 1
            file_label[idx] = ttk.Label(tabs[tab_idx], text='')
            browse_button[idx] = ttk.Button(tabs[tab_idx], text=f'Browse signal {sgnl_idx + 1}', command=lambda idx=idx: browse_file(file_label[idx], x_input, idx, readBoth=True))
            browse_button[idx].pack()
            file_label[idx].pack()

        if tab_idx == 0:
            display_button[tab_idx] = ttk.Button(tabs[tab_idx], text='Display',
                                        command=lambda tab_idx=tab_idx: fast_convolution(x_input[0][0], x_input[0][1], x_input[1][0],
                                                                                           x_input[1][1], True))
        else:
            display_button[tab_idx] = ttk.Button(tabs[tab_idx], text='Display',
                                                 command=lambda tab_idx=tab_idx: fast_correlation(x_input[2][1], x_input[3][1], True))

        display_button[tab_idx].pack()
        global ax, canvas, corr_table
        fig = Figure(figsize=(5, 4), dpi=100)
        ax[2*tab_idx + 0] = fig.add_subplot(121)
        ax[2*tab_idx + 1] = fig.add_subplot(122)
        canvas[tab_idx] = FigureCanvasTkAgg(fig, master=tabs[tab_idx])
        canvas[tab_idx].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas[tab_idx].draw()

        if tab_idx == 1:
            h = ['n', 'corr']
            corr_table = ttk.Treeview(tabs[tab_idx], columns=h, show="headings")
            for i in range(len(h)):
                corr_table.heading(i, text=h[i])
                corr_table.column(i, width=100)
            corr_table.pack()

def Fast_Corr_Conv(tabs):
    fast_conv_corr = ttk.Frame(tabs)
    tabs.add(fast_conv_corr, text="Fast Convolution/Correlation (FD)")
    tabs.pack(fill="both", expand=True)
    inner_tab = ttk.Notebook(fast_conv_corr)

    fn_name = ['Fast convolution', 'Fast correlation']
    tab = [0] * len(fn_name)
    for i in range(len(fn_name)):
        tab[i] = ttk.Frame(inner_tab)
        inner_tab.add(tab[i], text=fn_name[i])
        inner_tab.pack(fill="both", expand=True)

    Build(tab)