from tkinter import ttk
from matplotlib.figure import Figure
from tkinter import filedialog
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import os
from utils import browse_file, Compare_Signals

x_input = [[]] * 4
test_signals = []
test_signals_name = []

ax1, ax2, canvas, table, delay_value, sampling_val, classes_table = 0, 0, 0, 0, 0, 0, 0


def time_delay_analysis(sampling_freq, cross_corr):
    lag = np.argmax(np.abs(cross_corr))
    time_delay = lag * (1/sampling_freq)
    print('lag:', lag)
    delay_value.config(text=str(time_delay))
    return time_delay



def cross_correlation(x1, x2):
    N = len(x1)
    res = [0] * N
    for i in range(N):
        res[i] = 0
        for j in range(N):
            res[i] += x1[j] * x2[(i + j) % N]
        res[i] /= N
    return res

def normalized_cross_correlation(x1, x2, update=True):
    if update:
        ax1.clear()
        ax2.clear()
        for row in table.get_children():
            table.delete(row)

    N = len(x1)
    n = [i for i in range(N)]
    b = ((sum([i**2 for i in x1]) * sum([i**2 for i in x2])) ** 0.5) # / N
    res = [0] * N

    for i in range(N):
        res[i] = 0
        for j in range(N):
            res[i] += x1[j] * x2[(i + j) % N]
        if update:
            table.insert("", "end", values=(n[i], round(res[i]/N, 5), round(b/N, 5), round(res[i]/b, 5)))
        res[i] = res[i] / b  #/N

    Compare_Signals('CorrOutput.txt', n, res)
    if update:
        ax1.plot(n, x1, label='Signal 1')
        ax1.plot(n, x2, label='Signal 2')
        ax2.plot(n, res)
        ax1.legend()
        canvas.draw()
        # print('res:', res)
        print(sampling_val.get())
        time_delay_analysis(float(sampling_val.get()), res)
    return res


def browse_folder(idx, folder_label, isTestFolder):
    folder_path = filedialog.askdirectory(title="Select Folder")
    if folder_path:
        folder_label.config(text='Selected Folder: '+ folder_path)
        cnt = 0
        global test_signals, test_signals_name
        if not isTestFolder:
            x_input[idx] = []
        else:
            test_signals = []
            test_signals_name = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename.endswith('.txt') and os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    j = 0
                    tmp = []
                    for line in file:
                        if isTestFolder:
                            tmp.append(float(line))
                            continue
                        if j < len(x_input[idx]):
                            x_input[idx][j] += float(line)
                        else:
                            x_input[idx].append(float(line))
                        j += 1
                cnt += 1
                if isTestFolder:
                    test_signals.append(tmp)
                    test_signals_name.append(filename)

        if cnt and not isTestFolder:
            for i in range(len(x_input[idx])):
                x_input[idx][i] /= cnt
            print(x_input[idx])


def correlation(tab):
    file_label = [0] * 2
    browse_button = [0] * 2

    for i in range(2):
        file_label[i] = ttk.Label(tab, text='')
        browse_button[i] = ttk.Button(tab, text='Browse Signal', command=lambda i=i: browse_file(file_label[i], x_input, i))
        file_label[i].pack()
        browse_button[i].pack()

    global ax1, ax2, canvas, table, delay_value, sampling_val

    sampling_label = ttk.Label(tab, text='Enter Sampling period:')
    sampling_val = tk.Spinbox(tab, from_=1, to=1000, increment=1)
    display_button = ttk.Button(tab, text='Display Correlation', command=lambda: normalized_cross_correlation(x_input[0], x_input[1]))

    sampling_label.pack()
    sampling_val.pack()
    display_button.pack()

    fig = Figure(figsize=(5, 4), dpi=100)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()

    table_headers = ["n", "r12(n)", "denominator", "p12(n)"]
    table = ttk.Treeview(tab, columns=table_headers, show="headings")
    delay_label = ttk.Label(tab, text='Time Delay:')
    delay_value = ttk.Label(tab, text='')
    delay_label.pack()
    delay_value.pack()

    for i in range(len(table_headers)):
        table.heading(i, text=table_headers[i])
        table.column(i, width=100)
    table.pack()


def display_matching():
    for row in classes_table.get_children():
        classes_table.delete(row)

    for i in range(len(test_signals)):
        resA = cross_correlation(x_input[2], test_signals[i])
        resB = cross_correlation(x_input[3], test_signals[i])
        avgA = np.average(resA)
        avgB = np.average(resB)
        print(avgA, avgB)
        c = 'A' if avgA > avgB else 'B'
        classes_table.insert("", "end", values=(test_signals_name[i], c))


def template_matching(tab):
    folder_label = [0] * 3
    browse_label = [0] * 3
    browse_button = [0] * 3

    for i in range(2):
        c = 'A' if i == 0 else 'B'
        browse_label[i] = ttk.Label(tab, text=f'Browse Class {c} Folder')
        browse_label[i].pack()
        browse_button[i] = ttk.Button(tab, text='Browse', command=lambda i=i: browse_folder(i + 2, folder_label[i], False))
        browse_button[i].pack()
        folder_label[i] = ttk.Label(tab, text='')
        folder_label[i].pack()

    browse_label[-1] = ttk.Label(tab, text='Browse test Folder')
    browse_label[-1].pack()
    browse_button[-1] = ttk.Button(tab, text='Browse', command=lambda : browse_folder(4, folder_label[-1], True))
    browse_button[-1].pack()
    folder_label[-1] = ttk.Label(tab, text='')
    folder_label[-1].pack()
    display_button = ttk.Button(tab, text='Display', command=display_matching)
    display_button.pack()

    global classes_table

    headers = ['Test file name', 'Class']
    classes_table = ttk.Treeview(tab, columns=headers, show="headings")

    for i in range(len(headers)):
        classes_table.heading(i, text=headers[i])
        classes_table.column(i, width=100)
    classes_table.pack()

def Correlations(tabs):
    corr = ttk.Frame(tabs)
    tabs.add(corr, text="Correlation")
    tabs.pack(fill="both", expand=True)
    inner_tab = ttk.Notebook(corr)

    fn_name = ['Correlation', 'Template Matching']
    tab = [0] * len(fn_name)
    for i in range(len(fn_name)):
        tab[i] = ttk.Frame(inner_tab)
        inner_tab.add(tab[i], text=fn_name[i])
        inner_tab.pack(fill="both", expand=True)

    correlation(tab[0])
    template_matching(tab[1])
