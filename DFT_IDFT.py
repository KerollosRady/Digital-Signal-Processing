import math
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import numpy as np
import cmath
from utils import save_file

dgts = 15

#Both DFT/IDFT #######################################
def round_complex(complex_num, digits):
    real_part = round(complex_num.real, digits)
    imag_part = round(complex_num.imag, digits)
    return complex(real_part, imag_part)


def calc_I_DFT(type, x_input):
    if not x_input:
        return []
    N = len(x_input)
    sign = -1 if type == 'dft' else 1
    divide = 1 if type == 'dft' else N
    x_result = [0 + 0j] * N

    for i in range(N):
        for j in range(N):
            x_result[i] += x_input[j] * np.exp(sign * 2j * np.pi * i * j / N)
        x_result[i] /= divide
        x_result[i] = round_complex(x_result[i], dgts)
    return x_result

def get_amp_phase_F(x_result, Fs):
    amp = [0] * len(x_result)
    phase = [0] * len(x_result)
    F = [0] * len(x_result)

    for i in range(len(x_result)):
        if i == 0:
            F[i] = round((2 * np.pi) / (len(x_result) * 1 / Fs), dgts)
        else:
            F[i] = F[i - 1] + F[0]
        r = x_result[i].real
        im = x_result[i].imag
        amp[i] = round(math.sqrt(r ** 2 + im ** 2), dgts)
        phase[i] = cmath.phase(x_result[i])
    return amp, phase, F
#####################################################

def DFT(tabs):
    DFT_tab = ttk.Frame(tabs)
    tabs.add(DFT_tab, text="DFT")
    tabs.pack(fill="both", expand=True)

    fig1 = Figure(figsize=(6, 5), dpi=100)
    fig2 = Figure(figsize=(6, 5), dpi=100)
    subplot1 = fig1.add_subplot(111)
    subplot2 = fig2.add_subplot(111)

    canvas1 = FigureCanvasTkAgg(fig1, master=DFT_tab)
    canvas2 = FigureCanvasTkAgg(fig2, master=DFT_tab)
    canvas1.get_tk_widget().pack(side=tk.LEFT)
    canvas2.get_tk_widget().pack(side=tk.RIGHT)

    def load_data(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            data = [list(map(float, line.split())) for line in lines[3:]]
            return data

    amp = []
    phase = []
    F = []
    Fs = 0

    def display_plots():
        subplot1.clear()
        subplot2.clear()
        subplot1.stem(F, amp)
        subplot2.stem(F, phase)
        save_file('DFT_out', amp, phase)
        subplot1.set_title('Frequency versus Amplitude')
        subplot2.set_title('Frequency versus Phase')
        subplot1.set_xlabel('Frequency')
        subplot1.set_ylabel('Amplitude')
        subplot2.set_xlabel('Frequency')
        subplot2.set_ylabel('Phase shift')
        subplot1.relim()
        subplot1.autoscale_view()
        subplot2.relim()
        subplot2.autoscale_view()
        canvas1.draw()
        canvas2.draw()

    def update_plot(x_input):

        nonlocal F, amp, phase, Fs

        x_result = calc_I_DFT('dft', x_input)
        Fs = float(sampling_freq.get())
        amp, phase, F = get_amp_phase_F(x_result, Fs)


        print('x_input', x_input)
        print('x_result', x_result)
        print('amp', amp)
        print('phase', phase)
        print('F', F)
        print('Fs', Fs)

        display_plots()

    x_input = []
    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            file_label.config(text="Selected File: " + file_path)
            data = load_data(file_path)
            nonlocal x_input
            x_input = [xi for (i, xi) in data]

    file_label = ttk.Label(DFT_tab, text="")
    file_label.pack()
    browse_button = ttk.Button(DFT_tab, text='Browse file', command=browse_file)
    browse_button.pack()
    sampling_freq_label = ttk.Label(DFT_tab, text="Sampling Frequency (Fs):")
    sampling_freq_label.pack()
    sampling_freq = ttk.Entry(DFT_tab)
    sampling_freq.insert(0, '4')
    sampling_freq.pack()
    display_button = ttk.Button(DFT_tab, text="Display", command=lambda: update_plot(x_input))
    display_button.pack()

    empty_line = ttk.Label(DFT_tab)
    empty_line.pack()

    modify_label = ttk.Label(DFT_tab, text="Modify signal")
    modify_label.pack()

    idx_label = ttk.Label(DFT_tab, text="Index:")
    idx_label.pack()
    idx_entry = ttk.Entry(DFT_tab)
    idx_entry.pack()

    amp_label = ttk.Label(DFT_tab, text="Amplitude:")
    amp_label.pack()
    amp_entry = ttk.Entry(DFT_tab)
    amp_entry.pack()

    phase_label = ttk.Label(DFT_tab, text="Phase:")
    phase_label.pack()
    phase_entry = ttk.Entry(DFT_tab)
    phase_entry.pack()

    def modify():
        idx = idx_entry.get()
        amp_ = amp_entry.get()
        phase_ = phase_entry.get()
        if not idx or not 0 <= int(idx) < len(amp):
            print('invalid input')
            return
        idx = int(idx)
        if amp_:
            amp[idx] = float(amp_)
        if phase_:
            phase[idx] = float(phase_)
        if amp_ or phase_:
            display_plots()

    modify_button = ttk.Button(DFT_tab, text="Modify", command=modify)
    modify_button.pack()

######################################################################
def IDFT(tabs):
    IDFT_tab = ttk.Frame(tabs)
    tabs.add(IDFT_tab, text="IDFT")
    tabs.pack(fill="both", expand=True)

    amp = []
    phase = []

    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            nonlocal amp, phase
            amp = []
            phase = []

            file_label.config(text="Selected File: " + file_path)
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        a = parts[0][:-1] if parts[0][-1] == 'f' else parts[0]
                        amp.append(float(a))
                        p = parts[1][:-1] if parts[1][-1] == 'f' else parts[1]
                        phase.append(float(p))

            print(amp, phase)

    def update_plot():
        x_input = [0] * len(amp)

        for i in range(len(amp)):
            x = amp[i] * cmath.cos(phase[i])
            y = amp[i] * cmath.sin(phase[i])
            x_input[i] = x + 1j * y

        # for i in range(len(x_input)):
        #     x_input[i] = round_complex(x_input[i], 5)
        x_result = calc_I_DFT('idft', x_input)
        for i in range(len(x_result)):
            x_result[i] = round(x_result[i].real, 5)

        print(x_input)
        print(x_result)
        n = [i for i in range(len(x_result))]
        subplot.clear()
        subplot.plot(n, x_result)
        canvas.draw()
        save_file('IDFT_out', n, x_result)

    file_label = ttk.Label(IDFT_tab, text="")
    file_label.pack()
    browse_button = ttk.Button(IDFT_tab, text='Browse file', command=browse_file)
    browse_button.pack()
    sampling_freq_label = ttk.Label(IDFT_tab, text="Sampling Frequency (Fs):")
    sampling_freq_label.pack()
    sampling_freq = ttk.Entry(IDFT_tab)
    sampling_freq.insert(0, '4')
    sampling_freq.pack()
    display_button = ttk.Button(IDFT_tab, text="Display", command=update_plot)
    display_button.pack()


    fig = Figure(figsize=(9, 6), dpi=100)
    subplot = fig.add_subplot(111)
    subplot.plot([1], [2])
    canvas = FigureCanvasTkAgg(fig, master=IDFT_tab)
    canvas.get_tk_widget().pack()

def DFT_IDFT(tabs):
    DFT(tabs)
    IDFT(tabs)