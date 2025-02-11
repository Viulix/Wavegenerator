import mathfunctions as mf
import pyvisa
import time

rm = pyvisa.ResourceManager()
defaultProfile = "ROUVEN"
loadTimeSeconds = 7

def loadProfile(signal_type, amplitude, drop_amplitude, peaktime, peaktime_unit, droptime, droptime_unit, delta_t, delta_t_unit, burst, pulseWidth):
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

    frequency = (1 / (float(pulseWidth)+ delta_t)) *10**3
    print(frequency)

    if signal_type == "SQU - SQU":
        pulse = mf.generateSQUSQU(float(amplitude), float(drop_amplitude), peaktime, droptime, float(pulseWidth))
        frequency = (1 / (float(pulseWidth)+ delta_t + 1)) *10**3
        maxVoltage = max(abs(pulse))
        pulseDiff = mf.getPulseDifference(pulse, delta_t)
        normPulse = mf.normalizePulse(pulseDiff)
        datastring = ",".join(map(str, normPulse))
        sendAndSaveCustom("0," + datastring)
        time.sleep(loadTimeSeconds)
    elif signal_type == "SQU - EXP":
        print("Aktion: SQU - EXP wird ausgeführt (z.B. quadratischer Impuls mit exponentiellem Abfall).")
    elif signal_type == "EXP - EXP":
        print("Aktion: EXP - EXP wird ausgeführt (z.B. exponentieller Impuls, der exponentiell abklingt).")
    elif signal_type == "TRI - TRI":
        print("Aktion: TRI - TRI wird ausgeführt (z.B. dreieckiger Impuls in beiden Phasen).")
    elif signal_type == "Model":
        datastring = mf.normalize_and_format_function(mf.modelFunction, 24000, 0.001, 12)
        print(datastring)
        sendAndSaveCustom(20, 2, datastring)
        time.sleep(loadTimeSeconds)
    else:
        print("Unbekannter Signaltyp!")
        return
    
    if burst:
        print("Preparing the triggermode")
        prepareTrigger(frequency, maxVoltage)
        time.sleep(3)
    print("Profile has been loaded.")

def sendAndSaveCustom(customDatastring):
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {customDatastring}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.close()

def prepareTrigger(frequency, amplitude, offset=0, cycle_count=1, start_phase=0):
    """Applies the default settings for the Burst-Mode and applies the mode."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"APPL:USER {frequency}, {amplitude} VPP, {offset}")
    smu.write(f"BURS:NCYC {cycle_count}")
    smu.write(f"BURS:PHAS {start_phase}")
    smu.write("BURS:MODE TRIG")
    smu.write("TRIG:SOUR BUS")
    smu.write("BURS:STAT ON")
    smu.close()

def sendTrigger():
    """Sends a single external trigger. Only works in Burst-Mode"""
    print("Sending trigger:")
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write("*TRG")
    smu.close()
    time.sleep(0.1)

def sendCustom(signal_str:str, frequency, amplitude, offset=0):
    """Sends and applies a custome signal string - also stores the pulsform."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {signal_str}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.write(f"APPL:USER {frequency}, {amplitude}, {offset}") # Activate Profile
    smu.close()


def writeAndSaveCustom(signal_str:str):
    """Send a custom signal string and load it into a profile of the generator. Does not apply the profile."""
    smu = rm.open_resource('ASRL6::INSTR')
    smu.write(f"DATA VOLATILE, {signal_str}") # Write arbitary waveform in volatile memory of the device
    smu.write(f"DATA:COPY {defaultProfile}, VOLATILE")  # Copy the waveform into a profile (here ARB3)
    smu.write(f"FUNC:USER {defaultProfile}")  # Activate the profile for the User Mode
    smu.close()