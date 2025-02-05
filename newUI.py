import tkinter as tk
from tkinter import ttk, messagebox
from wavefunctions import send_signal

# Hauptfenster erstellen
root = tk.Tk()
root.title("Signal Sender")
root.geometry("600x300")
root.configure(bg="#f0f0f0")

# Frame für Steuerung
control_frame = tk.Frame(root, bg="#f0f0f0")
control_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Grid-Layout konfigurieren
for i in range(6):
    control_frame.columnconfigure(i, weight=1)

def add_labeled_entry(frame, label_text, row, unit_options=None):
    label = tk.Label(frame, text=label_text, bg="#f0f0f0", font=("Arial", 12))
    label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
    entry = tk.Entry(frame)
    entry.grid(row=row, column=1, padx=5, pady=5)
    
    if unit_options:
        unit_var = tk.StringVar(value=unit_options[0])
        unit_dropdown = ttk.Combobox(frame, textvariable=unit_var, values=unit_options, state="readonly", width=5)
        unit_dropdown.grid(row=row, column=2, padx=5, pady=5)
        return entry, unit_var
    
    return entry

# Dropdown Menü: Signal Type (neue Profile)
signal_var = tk.StringVar(value="SQU - SQUR")
tk.Label(control_frame, text="Signal Type:", bg="#f0f0f0", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
signal_dropdown = ttk.Combobox(control_frame, textvariable=signal_var,
                               values=["SQU - SQUR", "SQU - EXP", "EXP - EXP", "TRI - TRI", "Model"],
                               state="readonly")
signal_dropdown.grid(row=0, column=1, columnspan=2, padx=0, pady=5)

# Eingabefelder mit Labels
drop_amplitude_entry = add_labeled_entry(control_frame, "Drop Amplitude:", 1)
amplitude_entry = add_labeled_entry(control_frame, "Amplitude:", 2)
peaktime_entry, peaktime_unit = add_labeled_entry(control_frame, "Peaktime:", 3, ["ms", "µs"])
droptime_entry, droptime_unit = add_labeled_entry(control_frame, "Droptime:", 4, ["ms", "µs"])
delta_t_entry, delta_t_unit = add_labeled_entry(control_frame, "Delta t:", 5, ["ms", "µs"])

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
send_button.grid(row=6, column=0, columnspan=3, pady=15)

# Reset-Button mit Bestätigungsdialog
reset_button = tk.Button(control_frame, text="Reset Device", 
                         command=lambda: messagebox.askyesno("Bestätigung", "Möchten Sie wirklich Erase ausführen?") 
                         and print("Reset Device: Befehl ausgeführt!"),
                         bg="#f44336", fg="white", font=("Arial", 12, "bold"))
reset_button.grid(row=6, column=1, columnspan=5, pady=15)

root.mainloop()
