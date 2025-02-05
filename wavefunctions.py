import numpy as np

def update_plot(ax, canvas, signal_type):
    """
    Aktualisiert den Plot basierend auf dem Signaltyp.
    Hier erfolgt eine Beispiel-Darstellung, die je nach Signalprofil angepasst werden kann.
    """
    time = np.linspace(0, 1, 1000)
    
    # Beispielhafte Darstellung, kann je nach Bedarf verfeinert werden
    if signal_type == "SQU - SQUR":
        signal = np.sign(np.sin(2 * np.pi * time))
    elif signal_type == "SQU - EXP":
        signal = np.exp(-5 * time) * np.sign(np.sin(2 * np.pi * time))
    elif signal_type == "EXP - EXP":
        signal = np.exp(-5 * time)
    elif signal_type == "TRI - TRI":
        signal = 1 - 2 * np.abs(2 * time - 1)
    elif signal_type == "Model":
        signal = np.sin(2 * np.pi * time) * np.exp(-time)
    else:
        signal = np.zeros_like(time)
    
    ax.clear()
    ax.plot(time, signal)
    ax.set_title("Signal Preview")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    canvas.draw()

def send_signal(signal_type, amplitude, drop_amplitude, peaktime, peaktime_unit, droptime, droptime_unit, delta_t, delta_t_unit):
    """
    Sendet den Impuls. Die Funktion wertet den Signaltyp aus und führt entsprechend unterschiedliche
    Aktionen aus. Hier erfolgt die Unterscheidung demonstrativ über Print-Ausgaben.
    """
    print("------------ Send Signal ------------")
    print("Signal Type:", signal_type)
    print("Amplitude:", amplitude)
    print("Drop Amplitude:", drop_amplitude)
    print(f"Peaktime: {peaktime} {peaktime_unit}")
    print(f"Droptime: {droptime} {droptime_unit}")
    print(f"Delta t: {delta_t} {delta_t_unit}")
    
    if signal_type == "SQU - SQUR":
        print("Aktion: SQU - SQUR wird ausgeführt (z.B. quadratischer Impuls mit Quaderform).")
    elif signal_type == "SQU - EXP":
        print("Aktion: SQU - EXP wird ausgeführt (z.B. quadratischer Impuls mit exponentiellem Abfall).")
    elif signal_type == "EXP - EXP":
        print("Aktion: EXP - EXP wird ausgeführt (z.B. exponentieller Impuls, der exponentiell abklingt).")
    elif signal_type == "TRI - TRI":
        print("Aktion: TRI - TRI wird ausgeführt (z.B. dreieckiger Impuls in beiden Phasen).")
    elif signal_type == "Model":
        print("Aktion: Model wird ausgeführt (z.B. Modellbasierter Impuls).")
    else:
        print("Unbekannter Signaltyp!")
    print("-------------------------------------")
