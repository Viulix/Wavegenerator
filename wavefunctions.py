import mathfunctions as mf

def send_signal(signal_type, amplitude, drop_amplitude, peaktime, peaktime_unit, droptime, droptime_unit, delta_t, delta_t_unit):
    """
    Sendet den Impuls. Die Funktion wertet den Signaltyp aus und führt entsprechend unterschiedliche
    Aktionen aus. Hier erfolgt die Unterscheidung demonstrativ über Print-Ausgaben.
    """
    if droptime_unit == "ms":
        droptime = float(droptime)
    if droptime_unit == "µs":
        droptime = float(droptime)*10**(-3)
    if peaktime_unit == "ms":
        peaktime = float(peaktime)
    if peaktime_unit == "µs":
        peaktime = float(peaktime)*10**(-3)
    if delta_t_unit == "ms":
        delta_t = float(delta_t)
    if delta_t_unit == "µs":
        delta_t = float(delta_t)*10**(-3)
    
    print("------------ Send Signal ------------")
    print("Signal Type:", signal_type)
    print("Amplitude:", amplitude)
    print("Drop Amplitude:", drop_amplitude)
    print(f"Peaktime: {peaktime} ms")
    print(f"Droptime: {droptime} ms")
    print(f"Delta t: {delta_t} ms")
    



    if signal_type == "SQU - SQUR":
        print(mf.generateSQUSQU(float(amplitude), float(drop_amplitude), float(peaktime), float(droptime)))
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
