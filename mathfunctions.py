import numpy as np

def generateSQUSQU(amplitude1, amplitude2, uptime, downtime, periodInMilliseconds=10):
    """Generates the Square-Square waveform as string."""
    
    resultAmplitude1 = 1
    resultAmplitude2 = 1
    print(uptime, downtime)

    if amplitude1 > amplitude2:
        ratio = round(amplitude2 / amplitude1, 2)
        resultAmplitude2 = ratio
    else:
        # If the second amplitude is higher, we need to swap the amplitudes
        ratio = round(amplitude1 / amplitude2, 2)
        resultAmplitude1 = ratio
    result = []

    for i in range(periodInMilliseconds):
        if 0 <= i < uptime:
            result.append(resultAmplitude1)
        elif uptime <= i < downtime + uptime:
            result.append(-resultAmplitude2)
        else: result.append(0)
    resultString = ",".join(map(str, result))
    print(resultString)
    return resultString

def MathFunction(x):
    """Returns a hard coded function of x. Used for calculation purposes. Only change, if you want to change the plot."""
    return 2*x

def sendMathFunction(smu, datastr: str):
    """Sends a command to the wavegenerator"""

def normalize_and_format_function(func, sampleNumber: int, a, b):
    """Normalizies a function to provide values from -1 to 1. It calculates all values of func from a to b."""

    datastr = ""
    
    # Calculates values
    x_values = np.linspace(a, b, sampleNumber)  
    y_values = func(x_values)

    # Get min and max values
    min_value = np.min(y_values)
    max_value = np.max(y_values)
    
    normalized_values = 2 * (y_values - min_value) / (max_value - min_value) - 1 # normalize
    
    # Create string for the wave generator
    for value in normalized_values:
        datastr += f"{value:.2f},"
    
    return datastr
