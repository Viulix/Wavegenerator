import mathfunctions as mf
import pyvisa
import time

rm = pyvisa.ResourceManager()
defaultProfile = "ROUVEN"
loadTimeSeconds = 8

def loadProfile(signal_type, amplitude, drop_amplitude, peaktime, peaktime_unit, droptime, droptime_unit, delta_t, delta_t_unit, burst):
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
        delta_t = int(delta_t)
    if delta_t_unit == "µs": # NEEDS TO BE REMOVED
        delta_t = float(delta_t)*10**(-3)
    print(amplitude, drop_amplitude, peaktime, droptime)

    if signal_type == "SQU - SQU":
        datastring = mf.generateSQUSQU(float(amplitude), float(drop_amplitude), peaktime, droptime)
        diffString = mf.generateSQUSQUDiff(datastring, datastring, delta_t)
        print(diffString)
        return
        sendAndSaveCustom(20, 2, datastring)
        time.sleep(loadTimeSeconds)
    elif signal_type == "SQU - EXP":
        print("Aktion: SQU - EXP wird ausgeführt (z.B. quadratischer Impuls mit exponentiellem Abfall).")
    elif signal_type == "EXP - EXP":
        print("Aktion: EXP - EXP wird ausgeführt (z.B. exponentieller Impuls, der exponentiell abklingt).")
    elif signal_type == "TRI - TRI":
        print("Aktion: TRI - TRI wird ausgeführt (z.B. dreieckiger Impuls in beiden Phasen).")
    elif signal_type == "Model":
        datastring = mf.normalize_and_format_function(mf.modelMathFunction, 24000, 0.001, 12)
        print(datastring)
        sendAndSaveCustom(20, 2, datastring)
        time.sleep(loadTimeSeconds)
    else:
        print("Unbekannter Signaltyp!")
        return
    if burst:
        prepareTrigger()
        time.sleep(8)
    
    print("-------------------------------------")

def sendAndSaveCustom(frequency, amplitude, customeDatastring):
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {customeDatastring}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.close()

def prepareTrigger():
    """Applies the default settings in the Burst-Mode and applies the mode."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write("APPL:USER 10, 2, 0")
    smu.write("BURS:NCYC 1")
    smu.write("BURS:PHAS 0")
    smu.write("BURS:MODE TRIG")
    smu.write("TRIG:SOUR BUS")
    smu.write("BURS:STAT ON")
    smu.close()

def sendTrigger():
    """Only sends a single external trigger. Only works in Burst-Mode"""
    print("Sending trigger:")
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write("*TRG")
    smu.close()

def sendCustom(signal_str:str):
    """Sends and applies a custome signal string - also stores the pulsform."""
    smu = rm.open_resource('ASRL6::INSTR')
    freq = 100
    voltageAmplitdue = 2 # Should not be greater than 10 V!
    smu.write(f"DATA VOLATILE, {signal_str}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.write(f"APPL:USER {freq}, {voltageAmplitdue}, 0") # Activate Profile
    smu.close()


def writeAndSaveCustom(signal_str:str):
    """Send a curtom signal string and load it into a profile of the generator. Does not apply the profile."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {signal_str}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.close()