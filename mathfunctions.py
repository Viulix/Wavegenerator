import numpy as np
import matplotlib.pyplot as plt
def generateSQUSQU(amplitude1, amplitude2, uptime, downtime, periodInMilliseconds=10, delta=0):
    """Generates the Square-Square waveform as string."""
    resultAmplitude1 = 1
    resultAmplitude2 = 1

    if amplitude1 > amplitude2:
        ratio = round(amplitude2 / amplitude1, 2)
        resultAmplitude2 = ratio
    else:
        # If the second amplitude is higher, we need to swap the amplitudes
        ratio = round(amplitude1 / amplitude2, 2)
        resultAmplitude1 = ratio
    result = [0]

    for i in range(periodInMilliseconds - 1):
        if 0 <= i < uptime:
            result.append(resultAmplitude1)
        elif uptime <= i < downtime + uptime:
            result.append(-resultAmplitude2)
        else: result.append(0)
    resultString = ",".join(map(str, result))
    return resultString

def generateSQUSQUDiff(puls1, puls2, delta=0):
    """Generates the Square-Square waveform as string."""
    newPuls1 = [0] * delta + str.split(puls1, ",")
    newPuls2 = str.split(puls2, ",") + [0] * delta
    
    diffPuls = [0]
    for i in range(len(newPuls1)):
        diffPuls.append((float(newPuls1[i]) - float(newPuls2[i])) / 2)

    resultString = ",".join(map(str, diffPuls))
    return resultString


def modelMathFunction(x, delta=0):
    """Returns a hard coded function of x. Used for calculation purposes. Only change, if you want to change the plot."""
    f = 20 * np.exp(.1 * np.log(abs(x-delta)) - (x-delta)**2)- 2*np.exp(-.02*(x-delta)**2)
    return f

def sendMathFunction(smu, datastr: str):
    """Sends a command to the wavegenerator"""

def normalize_and_format_function(func, sampleNumber: int, a, b):
    """Normalizies a function to provide values from -1 to 1. It calculates all values of func from a to b."""

    datastr = "0,"
    
    # Calculates values
    x_values = np.linspace(a, b, sampleNumber)  
    y_values = func(x_values)
    
    # Get min and max values
    min_value = np.min(y_values)
    max_value = np.max(y_values)

    maximumValue = np.max([abs(min_value), abs(max_value)])

    normalized_values = y_values / maximumValue
    
    # Create string for the wave generator
    for value in normalized_values:
        datastr += f"{value:.4f},"
    
    return datastr
