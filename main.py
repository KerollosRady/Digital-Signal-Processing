import tkinter as tk
from tkinter import ttk

from DFT_IDFT import DFT_IDFT
from DCT_Remove_DC import DCT_Remove_DC
from Enhance_and_Transform import Enhance_and_Transform
from Correlations import Correlations
from Fast_Corr_Conv import Fast_Corr_Conv
from Filtering import Filtering
from Resampling import Resampling

root = tk.Tk()
root.title("Digital Signal Processing")
root.geometry("1500x800")
tabs = ttk.Notebook(root)

# DSP Tasks
DFT_IDFT(tabs)
DCT_Remove_DC(tabs)
Enhance_and_Transform(tabs)
Correlations(tabs)
Fast_Corr_Conv(tabs)
Filtering(tabs)
Resampling(tabs)

style = ttk.Style()
style.configure("TNotebook.Tab", padding=[20, 8])
style.map("TNotebook.Tab", padding=[("selected", [20, 8])])
root.mainloop()