import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wavefunctions import update_plot, send_signal

# Hauptfenster erstellen
root = tk.Tk()
root.title("Signal Sender")
root.geometry("750x450")
root.configure(bg="#f0f0f0")

# Frame für Steuerung
control_frame = tk.Frame(root, bg="#f0f0f0")
control_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Dropdown Menü: Signal Type (neue Profile)
signal_var = tk.StringVar(value="SQU - SQUR")
signal_label = tk.Label(control_frame, text="Signal Type:", bg="#f0f0f0", font=("Arial", 12))
signal_label.pack(pady=5)
signal_dropdown = ttk.Combobox(control_frame, textvariable=signal_var,
                               values=["SQU - SQUR", "SQU - EXP", "EXP - EXP", "TRI - TRI", "Model"],
                               state="readonly")
signal_dropdown.pack(pady=5)
signal_dropdown.bind("<<ComboboxSelected>>", lambda e: update_plot(ax, canvas, signal_var.get()))

# Eingabefeld für Amplitude
amplitude_label = tk.Label(control_frame, text="Amplitude:", bg="#f0f0f0", font=("Arial", 12))
amplitude_label.pack(pady=5)
amplitude_entry = tk.Entry(control_frame)
amplitude_entry.pack(pady=5)

# Eingabefeld für Drop Amplitude (neuer Parameter)
drop_amplitude_label = tk.Label(control_frame, text="Drop Amplitude:", bg="#f0f0f0", font=("Arial", 12))
drop_amplitude_label.pack(pady=5)
drop_amplitude_entry = tk.Entry(control_frame)
drop_amplitude_entry.pack(pady=5)

# Eingabefeld für Peaktime mit Einheit
peaktime_label = tk.Label(control_frame, text="Peaktime:", bg="#f0f0f0", font=("Arial", 12))
peaktime_label.pack(pady=5)
peaktime_frame = tk.Frame(control_frame, bg="#f0f0f0")
peaktime_frame.pack(pady=5)
peaktime_entry = tk.Entry(peaktime_frame, width=10)
peaktime_entry.pack(side=tk.LEFT)
peaktime_unit = tk.StringVar(value="ms")
peaktime_unit_dropdown = ttk.Combobox(peaktime_frame, textvariable=peaktime_unit, values=["ms", "µs"], state="readonly", width=5)
peaktime_unit_dropdown.pack(side=tk.LEFT, padx=5)

# Eingabefeld für Droptime mit Einheit
droptime_label = tk.Label(control_frame, text="Droptime:", bg="#f0f0f0", font=("Arial", 12))
droptime_label.pack(pady=5)
droptime_frame = tk.Frame(control_frame, bg="#f0f0f0")
droptime_frame.pack(pady=5)
droptime_entry = tk.Entry(droptime_frame, width=10)
droptime_entry.pack(side=tk.LEFT)
droptime_unit = tk.StringVar(value="ms")
droptime_unit_dropdown = ttk.Combobox(droptime_frame, textvariable=droptime_unit, values=["ms", "µs"], state="readonly", width=5)
droptime_unit_dropdown.pack(side=tk.LEFT, padx=5)

# Eingabefeld für Delta t mit Einheit
delta_t_label = tk.Label(control_frame, text="Delta t:", bg="#f0f0f0", font=("Arial", 12))
delta_t_label.pack(pady=5)
delta_t_frame = tk.Frame(control_frame, bg="#f0f0f0")
delta_t_frame.pack(pady=5)
delta_t_entry = tk.Entry(delta_t_frame, width=10)
delta_t_entry.pack(side=tk.LEFT)
delta_t_unit = tk.StringVar(value="ms")
delta_t_unit_dropdown = ttk.Combobox(delta_t_frame, textvariable=delta_t_unit, values=["ms", "µs"], state="readonly", width=5)
delta_t_unit_dropdown.pack(side=tk.LEFT, padx=5)

# Send-Button: Übergibt alle Parameter an send_signal
send_button = tk.Button(control_frame, text="Send Impuls", 
                        command=lambda: send_signal(
                            signal_var.get(),
                            amplitude_entry.get(),
                            drop_amplitude_entry.get(),
                            peaktime_entry.get(), peaktime_unit.get(),
                            droptime_entry.get(), droptime_unit.get(),
                            delta_t_entry.get(), delta_t_unit.get()),
                        bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
send_button.pack(pady=10)

# Reset-Button mit Bestätigungsdialog
reset_button = tk.Button(control_frame, text="Reset Device", 
                         command=lambda: messagebox.askyesno("Bestätigung", "Möchten Sie wirklich Erase ausführen?") 
                         and print("Reset Device: Befehl ausgeführt!"),
                         bg="#f44336", fg="white", font=("Arial", 12, "bold"))
reset_button.pack(pady=5)

# Matplotlib Plot
import numpy as np
fig, ax = plt.subplots(figsize=(4, 2))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10)
update_plot(ax, canvas, signal_var.get())

root.mainloop()
