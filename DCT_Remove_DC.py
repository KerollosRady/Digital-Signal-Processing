import math
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from utils import browse_file, save_file, SignalSamplesAreEqual

x_input = [[], []]
x_output = [[], []]

def DCT_and_Remove_DC(tabs, idx):
    tab = ttk.Frame(tabs)
    tabs.add(tab, text="DCT" if idx == 0 else 'Remove DC')
    tabs.pack(fill="both", expand=True)

    file_label = ttk.Label(tab, text="")
    file_label.pack()

    def update_plot():
        if not x_input[idx]:
            return
        global x_output
        n_idx = [i for i in range(len(x_input[idx]))]
        ax1.cla()
        ax2.cla()

        ax1.plot(n_idx, x_input[idx])

        if idx == 0:
            x_output[idx] = [0] * (len(x_input[idx]))
            for k in range(len(x_input[idx])):
                x_output[idx][k] = 0
                for n in range(len(x_input[idx])):
                    x_output[idx][k] += x_input[idx][n] * np.cos(np.pi/(4*len(x_input[idx])) * (2*n-1)*(2*k-1))
                x_output[idx][k] *= math.sqrt(2/len(x_input[idx]))
            num_of_coeff_val.delete(0, tk.END)
            num_of_coeff_val.insert(0, len(x_output[idx]))
            ax2.stem(n_idx, x_output[idx])
        else:
            r = sum(x_input[idx]) / len(x_input[idx])
            x_output[idx] = [x - r for x in x_input[idx]]
            ax2.plot(n_idx, x_output[idx])
            y1_min, y1_max = ax1.get_ylim()
            y2_min, y2_max = ax2.get_ylim()
            y_min, y_max = min(y1_min, y2_min), max(y1_max, y2_max)
            ax1.set_ylim(y_min, y_max)
            ax2.set_ylim(y_min, y_max)

        print(x_output[idx])
        canvas.draw()
        output_file = 'DCT_out.txt' if idx == 0 else 'removed_DC_component_out.txt'
        # SignalSamplesAreEqual(output_file, x_output[idx])
        save_file(output_file, n_idx, x_output[idx])

    browse_button = ttk.Button(tab, text='Browse file', command=lambda: browse_file(file_label, x_input, idx))
    browse_button.pack()
    display_button = ttk.Button(tab, text="Display", command=update_plot)
    display_button.pack()

    def update_save_number():
        num = int(num_of_coeff_val.get())
        if not 1 <= num <= len(x_output[idx]):
            num = len(x_output[idx])
            num_of_coeff_val.delete(0, tk.END)
            num_of_coeff_val.insert(0, num)
        save_file('DCT_out.txt', [i for i in range(num)], x_output[idx][:num])

    if idx == 0:
        num_of_coeff_label = ttk.Label(tab, text='Numer of coefficients to save:')
        num_of_coeff_label.pack()
        num_of_coeff_val = tk.Spinbox(tab, from_=0, to=1e10, increment=1, command=update_save_number)
        num_of_coeff_val.pack()

    fig = Figure(figsize=(5, 4), dpi=100)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()


def DCT_Remove_DC(tabs):
    DCT_and_Remove_DC(tabs, 0)
    DCT_and_Remove_DC(tabs, 1)