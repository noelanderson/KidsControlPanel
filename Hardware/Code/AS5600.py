from micropython import const
import adafruit_bus_device.i2c_device as i2c_device

_AS5600_DEFAULT_I2C_ADDR = const(0x36)
_AS5600_REG_ZMCO = const(0x00)
_AS5600_REG_ZPOS_HI = const(0x01)
_AS5600_REG_ZPOS_LO = const(0x02)
_AS5600_REG_MPOS_HI = const(0x03)
_AS5600_REG_MPOS_LO = const(0x04)
_AS5600_REG_MANG_HI = const(0x05)
_AS5600_REG_MANG_LO = const(0x06)
_AS5600_REG_CONF_HI = const(0x07)
_AS5600_REG_CONF_LO = const(0x08)
_AS5600_REG_RAW_ANGLE_HI = const(0x0C)
_AS5600_REG_RAW_ANGLE_LO = const(0x0D)
_AS5600_REG_ANGLE_HI = const(0x0E)
_AS5600_REG_ANGLE_LO = const(0x0F)
_AS5600_REG_STATUS = const(0x0B)
_AS5600_REG_SAGC = const(0x1A)
_AS5600_REG_MAGNITUDE_HI = const(0x1B)
_AS5600_REG_MAGNITUDE_LO = const(0x1C)
_AS5600_REG_BURN = const(0xFF)

_BURN_ANGLE_COMMAND = const(0x80)
_BURN_SETTINGS_COMMAND = const(0x40)

_POWER_MODE_MASK =    const(0b11111100)
_HYSTERESIS_MASK =    const(0b11110011)
_OUTPUT_STAGE_MASK =  const(0b11001111)
_PWM_FREQUENCY_MASK = const(0b00111111)
_SLOW_FILTER_MASK = const(0b11111100)
_FAST_FILTER_MASK = const(0b11100011)
_WATCH_DOG_MASK = const(0b11011111)

# User-facing constants:
POWER_MODE_NOM = const(0b00000000)
POWER_MODE_LPM1 = const(0b00000000)
POWER_MODE_LPM2 = const(0b00000010)
POWER_MODE_LPM3 = const(0b00000011)

HYSTERESIS_OFF = const(0b00000000)
HYSTERESIS_1LSB = const(0b00000100)
HYSTERESIS_2LSB = const(0b00001000)
HYSTERESIS_3LSB = const(0b00001100)

OUTPUT_STAGE_ANALOG_FULL = const(0b00000000)
OUTPUT_STAGE_ANALOG_REDUCED = const(0b00010000)
OUTPUT_STAGE_DIGITAL_PWM = const(0b00100000)

PWM_FREQUENCY_115HZ = const(0b00000000)
PWM_FREQUENCY_230HZ = const(0b01000000)
PWM_FREQUENCY_460HZ = const(0b10000000)
PWM_FREQUENCY_920HZ = const(0b11000000)

SLOW_FILTER_16X = const(0b00000000)
SLOW_FILTER_8X = const(0b00000000)
SLOW_FILTER_4X = const(0b00000010)
SLOW_FILTER_2X = const(0b00000011)

FAST_FILTER_THRESHOLD_SLOW = const(0b00000000)
FAST_FILTER_THRESHOLD_6LSB = const(0b00000100)
FAST_FILTER_THRESHOLD_7LSB = const(0b00001000)
FAST_FILTER_THRESHOLD_9LSB = const(0b00001100)
FAST_FILTER_THRESHOLD_18LSB = const(0b00010000)
FAST_FILTER_THRESHOLD_21LSB = const(0b00010100)
FAST_FILTER_THRESHOLD_24LSB = const(0b00011000)
FAST_FILTER_THRESHOLD_10LSB = const(0b00011100)


class AS5600:

    def __init__(self, i2c, address=_AS5600_DEFAULT_I2C_ADDR):
        self._device = i2c_device.I2CDevice(i2c, address)

    @property
    def angle(self):
        return self._readTwoBytes(_AS5600_REG_ANGLE_HI, _AS5600_REG_ANGLE_LO)

    @property
    def rawAngle(self):
        return self._readTwoBytes(_AS5600_REG_RAW_ANGLE_HI, _AS5600_REG_RAW_ANGLE_LO)

    @property
    def scaledAngle360(self):
        # Coverts angle of 0-4095 into 0-360
        return int((self._readTwoBytes(_AS5600_REG_ANGLE_HI, _AS5600_REG_ANGLE_LO) << 8) / 0xB5F)

    @property
    def scaledAngle(self):
        # Coverts angle of 0-4095 into -127 to +127
        angle = self._readTwoBytes(_AS5600_REG_ANGLE_HI, _AS5600_REG_ANGLE_LO)
        scaledAngle = 0

        if angle <= 2047:
            scaledAngle = angle >> 4
        else:
            scaledAngle = 0 - (abs(angle - 4095) >> 4)
        return scaledAngle

    @property
    def status(self):
        return self._readByte(_AS5600_REG_STATUS) & 0b00111000

    @property
    def isMagnetTooStrong(self):
        isSet = False
        if self.status & 0b00001000:
            isSet =  True
        return isSet

    @property
    def isMagnetTooWeak(self):
        isSet = False
        if self.status & 0b00010000:
            isSet =  True
        return isSet

    @property
    def isMagnetDetected(self):
        isSet = False
        if self.status & 0b00100000:
            isSet =  True
        return isSet

    @property
    def gain(self):
        return self._readByte(_AS5600_REG_SAGC)

    @property
    def magnitude(self):
        return self._readTwoBytes(_AS5600_REG_MAGNITUDE_HI, _AS5600_REG_MAGNITUDE_LO)

    @property
    def zmco(self):
        return self._readByte(_AS5600_REG_ZMCO)

    @property
    def zeroPosition(self):
        return self._readTwoBytes(_AS5600_REG_ZPOS_HI, _AS5600_REG_ZPOS_LO)

    @property
    def maxPosition(self):
        return self._readTwoBytes(_AS5600_REG_MPOS_HI, _AS5600_REG_MPOS_LO)

    @property
    def maxAngle(self):
        return self._readTwoBytes(_AS5600_REG_MANG_HI, _AS5600_REG_MANG_LO)

    def setZeroPosition(self, value):
        self._writeByte(_AS5600_REG_ZPOS_HI, (value & 0xFF00) >> 8)
        self._writeByte(_AS5600_REG_ZPOS_LO, (value & 0x00FF))
        return self._readTwoBytes(_AS5600_REG_ZPOS_HI, _AS5600_REG_ZPOS_LO)

    def setMaxPosition(self, value):
        self._writeByte(_AS5600_REG_MPOS_HI, (value & 0xFF00) >> 8)
        self._writeByte(_AS5600_REG_MPOS_LO, (value & 0x00FF))
        return self._readTwoBytes(_AS5600_REG_MPOS_HI, _AS5600_REG_MPOS_LO)

    def setMaxAngle(self, value):
        self._writeByte(_AS5600_REG_MANG_HI, (value & 0xFF00) >> 8)
        self._writeByte(_AS5600_REG_MANG_LO, (value & 0x00FF))
        return self._readTwoBytes(_AS5600_REG_MANG_HI, _AS5600_REG_MANG_LO)

    def setHysteresis(self, hysteresis):
        result = False
        if hysteresis == HYSTERESIS_OFF\
        or hysteresis == HYSTERESIS_1LSB\
        or hysteresis == HYSTERESIS_2LSB\
        or hysteresis == HYSTERESIS_3LSB:
            result = self._setConf(_AS5600_REG_CONF_LO, _HYSTERESIS_MASK, hysteresis)
        return result

    def setOutputStage(self, outputStage):
        result = False
        if outputStage == OUTPUT_STAGE_ANALOG_FULL\
        or outputStage == OUTPUT_STAGE_ANALOG_REDUCED\
        or outputStage == OUTPUT_STAGE_DIGITAL_PWM:
            result = self._setConf(_AS5600_REG_CONF_LO, _OUTPUT_STAGE_MASK, outputStage)
        return result

    def setPwmFrequency(self, frequencySelector):
        result = False
        if frequencySelector == PWM_FREQUENCY_115HZ\
        or frequencySelector == PWM_FREQUENCY_230HZ\
        or frequencySelector == PWM_FREQUENCY_460HZ\
        or frequencySelector == PWM_FREQUENCY_920HZ:
            result = self._setConf(_AS5600_REG_CONF_LO, _PWM_FREQUENCY_MASK, frequencySelector)
        return result

    def setPowerMode(self, mode):
        result = False
        if mode == POWER_MODE_NOM\
        or mode == POWER_MODE_LPM1\
        or mode == POWER_MODE_LPM2\
        or mode == POWER_MODE_LPM3:
            result = self._setConf(_AS5600_REG_CONF_LO, _POWER_MODE_MASK, mode)
        return result

    def setSlowFilter(self, filterSelector):
        result = False
        if filterSelector == SLOW_FILTER_16X\
        or filterSelector == SLOW_FILTER_8X\
        or filterSelector == SLOW_FILTER_4X\
        or filterSelector == SLOW_FILTER_2X:
            result = self._setConf(_AS5600_REG_CONF_HI, _SLOW_FILTER_MASK, filterSelector)
        return result

    def setFastFilter(self, filterSelector):
        result = False
        if filterSelector == FAST_FILTER_THRESHOLD_SLOW\
        or filterSelector == FAST_FILTER_THRESHOLD_6LSB\
        or filterSelector == FAST_FILTER_THRESHOLD_7LSB\
        or filterSelector == FAST_FILTER_THRESHOLD_9LSB\
        or filterSelector == FAST_FILTER_THRESHOLD_18LSB\
        or filterSelector == FAST_FILTER_THRESHOLD_21LSB\
        or filterSelector == FAST_FILTER_THRESHOLD_24LSB\
        or filterSelector == FAST_FILTER_THRESHOLD_10LSB:
            result = self._setConf(_AS5600_REG_CONF_HI, _FAST_FILTER_MASK, filterSelector)
        return result

    def burnAngle(self):
         self._writeByte(_AS5600_REG_BURN, _BURN_ANGLE_COMMAND)

    def burnSettings(self):
        # burns in MaxAngle and Config
        self._writeByte(_AS5600_REG_BURN, _BURN_SETTINGS_COMMAND)

    def _setConf(self, register, mask, value):
        result = False
        currentValue = self._readByte(register)
        newValue = (currentValue & mask) | value
        self._writeByte(register, newValue)
        if self._readByte(register) == newValue:
            result = True
        return result

    def _readByte(self, address):
        # Read and return a byte from the specified 8-bit register address.
        with self._device as i2c:
            result = bytearray(1)
            i2c.write(bytes([address]))
            i2c.readinto(result)
            return result[0]

    def _readTwoBytes(self, address_hi, address_lo):
        # Read and return a 16-bit unsigned value.
        hi = self._readByte(address_hi)
        lo = self._readByte(address_lo)
        return (hi << 8) | lo

    def _writeByte(self, address, value):
        # write a byte to the specified 8-bit register address.
        with self._device as i2c:
            i2c.write(bytes([address, value]))