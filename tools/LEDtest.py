# Test the LEDs by running them in a cycle.
from tools import LED
from time import sleep
while True:
    LED.red()
    sleep(.5)
    LED.green()
    sleep(.5)
    LED.blue()
    sleep(.5)