# Wavegenerator

This is a piece of software that allows you to send controlled impulses via an function generator.

---

## Setup

### Devices
- Prologix GPIB-USB (HPIB-USB) controller
- Keysight / Agilent 33220A Function / Arbitary Waveform Generator

### Drivers & Port
- In order to make the prologix communication to the generator, you'll need to install the correct drivers. You can find the correct drivers [here](https://ftdichip.com/drivers/d2xx-drivers/)
- You need to know what USB Port you are using for the connection to the PC. (e.g. COM5)
---
## How To Use?
If you've installed the drivers and downloaded the program from this github, you need to run the exectuable. 
Next you'll need to insert the correct USB port. If you insert the wrong port, the program cannot establish a connection to the device. Make sure to use the correct port.

### Interface
If you've inserted the correct port, you are good to go. Now select a profile at the top and adjust the settings as you wish. Then hit the "Load Profile" button, to make sure that the program is written to the memory of the device.
Wait until the program is loaded. If you selected "Burst Mode" you can send pulses using the according button. Selecting "single pulse" removes the process of subtracting the "returning" pulse.

---

## FAQ

**What does the Reset Button do?**  
This button sends a DC signal for a given period and amplitude. Afterwards, it returns to the running profile.

**Should I use Burst Mode?**  
This program is designed to use this mode. Disabling it is *_not recommended_*.

**I inserted the wrong USB port and the program won't close.**  
When this happens, the program waits for a response from the USB port, which can never be received.  
I recommend unplugging the USB device and then trying to close the application. It may not close properly unless the device is unplugged first.

---
