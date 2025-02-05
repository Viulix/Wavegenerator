import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import mathfunctions as mf
def update_plot():
    signal_type = signal_var.get()
    freq = float(freq_entry.get()) if freq_entry.get() else 1.0
    time = np.linspace(0, 1, 1000)
    
    if signal_type == "Sine":
        signal = np.sin(2 * np.pi * freq * time)
    elif signal_type == "Square":
        signal = np.sign(np.sin(2 * np.pi * freq * time))
    elif signal_type == "Synapse Impuls":
        signal = np.exp(-5 * time) * (time < 0.2)
    
    ax.clear()
    ax.plot(time, signal)
    ax.set_title("Signal Preview")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    canvas.draw()

def send_signal():
    signal_type = signal_var.get()
    delta_t = delta_t_entry.get()
    unit = unit_var.get()
    freq = freq_entry.get()
    print(f"Signal: {signal_type}, Delta t: {delta_t} {unit}, Frequency: {freq} Hz")
    print(mf.generateSQUSQU)

# Hauptfenster erstellen
root = tk.Tk()
root.title("Signal Sender")
root.geometry("600x300")
root.configure(bg="#f0f0f0")

# Frame für Steuerung
control_frame = tk.Frame(root, bg="#f0f0f0")
control_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Dropdown Menü
signal_var = tk.StringVar(value="Sine")
signal_label = tk.Label(control_frame, text="Signal Type:", bg="#f0f0f0", font=("Arial", 12))
signal_label.pack(pady=5)
signal_dropdown = ttk.Combobox(control_frame, textvariable=signal_var, values=["Sine", "Square", "Synapse Impuls"], state="readonly")
signal_dropdown.pack(pady=5)
signal_dropdown.bind("<<ComboboxSelected>>", lambda e: update_plot())

# Eingabefeld für Frequenz
freq_label = tk.Label(control_frame, text="Frequenz (Hz):", bg="#f0f0f0", font=("Arial", 12))
freq_label.pack(pady=5)
freq_entry = tk.Entry(control_frame)
freq_entry.insert(0, "1.0")
freq_entry.pack(pady=5)
freq_entry.bind("<KeyRelease>", lambda e: update_plot())

# Eingabefeld für Delta t
delta_t_label = tk.Label(control_frame, text="Delta t eingeben:", bg="#f0f0f0", font=("Arial", 12))
delta_t_label.pack(pady=5)
delta_t_entry = tk.Entry(control_frame)
delta_t_entry.pack(pady=5)

# Dropdown Menü für Einheit
unit_var = tk.StringVar(value="ms")
unit_label = tk.Label(control_frame, text="Einheit:", bg="#f0f0f0", font=("Arial", 12))
unit_label.pack(pady=5)
unit_dropdown = ttk.Combobox(control_frame, textvariable=unit_var, values=["s", "ms", "µs"], state="readonly")
unit_dropdown.pack(pady=5)

# Send-Button
send_button = tk.Button(control_frame, text="Send", command=send_signal, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
send_button.pack(pady=10)

# Matplotlib Plot
fig, ax = plt.subplots(figsize=(4, 2))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10)
update_plot()

root.mainloop()
