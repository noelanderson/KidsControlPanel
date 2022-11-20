import board
import busio
import neopixel
import adafruit_bus_device.i2c_device as i2c_device
import adafruit_vl6180x
import AS5600
import LedArray
import usb_hid
from adafruit_hid.gamepad import Gamepad
from micropython import const
import microcontroller
from microcontroller import watchdog as watchDog
from watchdog import WatchDogMode


class OctoAlert:
    def __init__(self, pin: int):
        self.brightness = 0
        self.pixels = neopixel.NeoPixel(pin, 16)
        self.pixels.fill((255, 165, 0))

    def pulse(self) -> None:
        self.pixels.brightness = (10-abs(10-self.brightness))/10
        self.brightness = (self.brightness + 1) % 20


class MovingAverageFilter:
    def __init__(self, initialValue: int):
        self.buffer = [initialValue] * 8
        self.index = 0

    def update(self, newValue: int) -> int:
        self.buffer[self.index] = newValue
        self.index = (self.index + 1) % 8
        return int(sum(self.buffer) >> 3)


FILTER_ALPHA_POINT2 = const(0x3333)   #(0.2 * 65535)
def ExponentialMovingAverageFilter(new, average, alpha):

    tmp = new * (alpha + 1 ) + average * (65536 - alpha)
    return int((tmp + 32768) / 65536)


octoalert = OctoAlert(board.GP1)
ledArray = LedArray.LedArray(board.GP0)

# Create I2C bus.
i2c = busio.I2C (scl=board.GP15, sda=board.GP14)

'''
# Create time of flight ranging sensor instance.
rangeSensor = adafruit_vl6180x.VL6180X(i2c)
filteredRange = MovingAverageFilter(rangeSensor.range)
OFFSET = const(6) # Min reading from range sensor
MAX = const(106) # Max reading from range sensor
scale = int(round(65536 / (MAX - OFFSET)))
'''

# Create Magnetic Rotation Sensor.
angleSensor = AS5600.AS5600(i2c)
# Set current position as our new zero datum
angleSensor.setZeroPosition(angleSensor.rawAngle)
print(angleSensor.status)
print("MagnetDetected: ", angleSensor.isMagnetDetected)
print("Too Strong: ", angleSensor.isMagnetTooStrong)
print("Too Weak: ", angleSensor.isMagnetTooWeak)

gamePad = Gamepad(usb_hid.devices)

# Setup watchdog
microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
#watchDog.timeout = 5 # Set a timeout of 5 seconds
#watchDog.mode = WatchDogMode.RESET


loopCount = 0
# Main loop
while True:
    if (loopCount % 400) == 0:
        octoalert.pulse()

    if (loopCount % 4000) == 0:
        ledArray.GameOfLife()

    # Read the range in millimeters and print it.
    if (loopCount % 100) == 0:

        # Read control column angle and scale its output for HID Gamepad input
        # 0 to 90 degrees (0 - 2047 angle reading) = 0 to 127
        # 0 to -90 degrees  (4095 - 3072 angle reading) = 0 to -127
        currentAngle = angleSensor.angle
        if currentAngle <= 2047:
            if currentAngle > 1023:
                currentAngle = 1023
            turn = currentAngle >> 3
        else:
            if currentAngle < 3073:
                currentAngle = 3072
            turn = 0 - (abs(currentAngle - 4095) >> 3)

        # Read control column angle and scale its output for HID Gamepad input
        # -127 to 127
        currentRange = filteredRange.update(rangeSensor.range)
        pitch = (((currentRange - OFFSET) * scale) - 32768) >> 8
        if pitch > 127: pitch = 127
        if pitch < -127: pitch = -127

        #print((pitch, turn))
        gamePad.move_joysticks(x = turn, y = pitch)

    #watchDog.feed()
    loopCount = (loopCount + 1) % 1000000