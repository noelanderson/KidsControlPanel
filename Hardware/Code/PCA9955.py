# SPDX-FileCopyrightText: Copyright (c) 2022 Noel Anderson
#
# SPDX-License-Identifier: MIT

# pylint: disable=line-too-long

"""
`PCA9955`
================================================================================
CircuitPython library for connecting an NXP PCA9955 16-channel I2C-bus constant current LED driver
* Author(s): Noel Anderson

Implementation Notes
--------------------
**Hardware:**

* `PCA9955 <https://www.nxp.com/docs/en/data-sheet/PCA9955B.pdf>`

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards: https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

from micropython import const
import adafruit_bus_device.i2c_device as i2c_device

# Register map & bit positions

_REGISTER_MODE1 = const(0x00)            # R/W

 #-------+-------+-------+-------+-------+-------+-------+-------+
 #   7   |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
 #-------+-------+-------+-------+-------+-------+-------+-------+
 #  TEMP | ERROR |DMBLNK | CLRERR|  OCH  |EXP_EN |       |       |
 #-------+-------+-------+-------+-------+-------+-------+-------+
_REGISTER_MODE2 = const(0x01)    # R/W
_BIT_OVERTEMP = const(7)         #  ok/overtemp (1 bit)
_BIT_ERROR = const(6)            #  no error/error (1 bit)
_BIT_DMBLNK = const(5)           #  group dimming/blinking (1 bit)
_BIT_CLRERR = const(4)           #  (1 bit)
_BIT_OCH = const(3)              #  (1 bit)
_BIT_EXP_EN = const(2)           #  grad control linear/exponential (1 bit)

_REGISTER_LEDOUT0 = const(0x02)  # R/W
_REGISTER_GRPPWM = const(0x06)   # R/W
_REGISTER_GRPFREQ = const(0x07)  # R/W
_REGISTER_PWM0 = const(0x08)     # R/W
_REGISTER_IREF0 = const(0x18)    # R/W

#---------------------------------------------------------------#
#   7   |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
#-------+-------+-------+-------+-------+-------+-------+-------|
#  R UP | R DOWN|                   RATE                        |
#---------------------------------------------------------------#
_REGISTER_RAMP_RATE_GRP0 = const(0x28)  # R/W
_BIT_RAMP_UP = const(7)                 #  Enable/disable (1 bit)
_BIT_RAMP_DOWN = const(6)               #  Enable/disable (1 bit)
_BIT_RAMP_RATE = const(0)               #  Enable/disable (6 bits)

#---------------------------------------------------------------#
#   7   |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
#-------+-------+-------+-------+-------+-------+-------+-------|
#       | CTIME |               FACTOR PER STEP                 |
#---------------------------------------------------------------#
_REGISTER_STEP_TIME_GRP0 = const(0x2A)  # R/W
_BIT_CYCLE_TIME = const(6)              #  Cycle time 1 bit
_BIT_FACTOR_PER_STEP = const(0)         #  Factor per step (6 bits)

#---------------------------------------------------------------#
#   7   |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
#-------+-------+-------+-------+-------+-------+-------+-------|
#  H ON | H OFF |          ON TIME      |        OFF TIME       |
#---------------------------------------------------------------#
_REGISTER_HOLD_CNTL_GRP0 = const(0x2B)  # R/W
_BIT_HOLD_ON = const(7)                 #  Enable/disable (1 bit)
_BIT_HOLD_OFF = const(6)                #  Enable/disable (1 bit)
_BIT_HOLD_ON_TIME = const(3)            #  Hold On time (3 bits)
_BIT_HOLD_OFF_TIME = const(0)           #  Hold Off time (3 bits)

_REGISTER_IREF_GRP0 = const(0x2C)        # R/W
_REGISTER_GRAD_MODE_SEL0 = const(0x38)   # R/W
_REGISTER_GRAD_MODE_SEL1 = const(0x39)   # R/W
_REGISTER_GRAD_GRP_SEL0 = const(0x3A)    # R/W
_REGISTER_GRAD_CTRL = const(0x3E)        # R/W
_REGISTER_OFFSET = const(0x3F)           # R/W
_REGISTER_PWMALL = const(0x44)           # W
_REGISTER_IREALL = const(0x45)           # W
_REGISTER_EFLAG0 = const(0x46)           # R


_1_BIT =  const(0b00000001)
_2_BITS = const(0b00000011)
_3_BITS = const(0b00000111)
_6_BITS = const(0b00111111)

# User-facing constants:

LED_DRIVER_OFF = const(0x00)
LED_DRIVER_FULL_ON = const(0x01)
LED_DRIVER_PWM = const(0x02)
LED_DRIVER_PWM_GRP = const(0x03)



class Channel:
    """A single PCA9955 channel

    :param PCA9955 device: The PCA9955 device object
    :param int index: The index of the channel
    """

    def __init__(self, device: "PCA9955", index: int):
        self._device = device
        self._index = index

    @property
    def brightness(self) -> int:
        """Channel brightness 0 - 255."""
        return self._device.read_8(_REGISTER_PWM0 + self._index)

    @brightness.setter
    def brightness(self, value: int) -> int:
        if not 0 <= value <= 255:
            raise ValueError("Value must be between 0 & 255")
        self._device.write_8(_REGISTER_PWM0 + self._index, value)

    @property
    def gain(self) -> int:
        """Channel curent gain 0 - 255."""
        return self._device.read_8(_REGISTER_IREF0 + self._index)

    @gain.setter
    def gain(self, value: int) -> int:
        if not 0 <= value <= 255:
            raise ValueError("Value must be between 0 & 255")
        self._device.write_8(_REGISTER_IREF0 + self._index, value)

    @property
    def output_state(self) -> int:
        """Channel Driver output state"""
        return self._device.read_channel_config(_REGISTER_LEDOUT0, self._index)

    @output_state.setter
    def output_state(self, value: int) -> int:
        if not LED_DRIVER_OFF <= value <= LED_DRIVER_PWM_GRP:
            raise ValueError(f"Value must be between {LED_DRIVER_OFF} & {LED_DRIVER_PWM_GRP}")
        self._device.write_channel_config(_REGISTER_LEDOUT0, self._index, value)

    @property
    def led_error(self) -> int:
        """LED error state"""
        return self._device.read_channel_config(_REGISTER_EFLAG0, self._index)

    @property
    def group(self) -> int:
        """Gradation group."""
        return self._device.read_channel_config(_REGISTER_GRAD_GRP_SEL0, self._index)

    @group.setter
    def group(self, value: int) -> int:
        if not 0 <= value <= 3:
            raise ValueError(f"Group must be between 0 and 3")
        self._device.write_channel_config(_REGISTER_GRAD_GRP_SEL0, self._index, value)


class Channels:  # pylint: disable=too-few-public-methods
    """Lazily creates and caches channel objects as needed. Treat it like a sequence.

    :param PCA9955 device: The PCA9955 device object
    """

    def __init__(self, device: "PCA9955") -> None:
        self._device = device
        self._channels = [None] * len(self)

    def __len__(self) -> int:
        return 16

    def __getitem__(self, index: int) -> Channel:
        if not self._channels[index]:
            self._channels[index] = Channel(self._device, index)
        return self._channels[index]


class Group:
    """A PCA9955 Graduation Group (set of channels)

    :param PCA9955 device: The PCA9955 device object
    :param int index: The index of the channel
    """

    def __init__(self, device: "PCA9955", index: int):
        self._device = device
        self._index = index


    @property
    def ramp_up(self) -> bool:
        """Ramp-up enable/disable."""
        return self._device.read_register(_REGISTER_RAMP_RATE_GRP0, self._index, _1_BIT,_BIT_RAMP_UP)

    @ramp_up.setter
    def ramp_up(self, value: bool) -> bool:
        self._device.write_register(_REGISTER_RAMP_RATE_GRP0, self._index, value, _1_BIT, _BIT_RAMP_UP)

    @property
    def ramp_down(self) -> bool:
        """Ramp-down enable/disable."""
        return self._device.read_register(_REGISTER_RAMP_RATE_GRP0, self._index, _1_BIT, _BIT_RAMP_DOWN)

    @ramp_down.setter
    def ramp_down(self, value: bool) -> bool:
        self._device.write_register(_REGISTER_RAMP_RATE_GRP0, self._index, value, _1_BIT, _BIT_RAMP_DOWN)

    @property
    def ramp_rate(self) -> int:
        """Ramp rate per step 0 - 64."""
        return self._device.read_register(_REGISTER_RAMP_RATE_GRP0, self._index, _6_BITS, _BIT_RAMP_RATE)

    @ramp_rate.setter
    def ramp_rate(self, value: int) -> int:
        if not 0 <= value <= 64:
            raise ValueError("Value must be between 0 & 64")
        self._device.write_register(_REGISTER_RAMP_RATE_GRP0, self._index, value, _6_BITS, _BIT_RAMP_RATE)

    @property
    def cycle_time(self) -> int:
        """Cycle time - 0 (0.5ms) or 1 (8ms)."""
        return self._device.read_register(_REGISTER_STEP_TIME_GRP0 , self._index, _1_BIT, _BIT_CYCLE_TIME)

    @cycle_time.setter
    def cycle_time(self, value: int) -> int:
        if not 0 <= value <= 64:
            raise ValueError("Valid values are 0 (0.5ms) or 1 (8ms)")
        self._device.write_register(_REGISTER_STEP_TIME_GRP0, self._index, value, _1_BIT, _BIT_CYCLE_TIME)

    @property
    def factor_per_step(self) -> int:
        """Multiple factor per step 0 - 64."""
        return self._device.read_register(_REGISTER_STEP_TIME_GRP0, self._index, _6_BITS, _BIT_FACTOR_PER_STEP)

    @factor_per_step.setter
    def factor_per_step(self, value: int) -> int:
        if not 0 <= value <= 64:
            raise ValueError("Value must be between 0 & 64")
        self._device.write_register(_REGISTER_STEP_TIME_GRP0, self._index, value, _6_BITS, _BIT_FACTOR_PER_STEP)

    @property
    def hold_on(self) -> bool:
        """Hold on enable/disable."""
        return self._device.read_register(_REGISTER_HOLD_CNTL_GRP0, self._index, _1_BIT, _BIT_HOLD_ON)

    @hold_on.setter
    def hold_on(self, value: bool) -> bool:
        self._device.write_register(_REGISTER_HOLD_CNTL_GRP0, self._index, value, _1_BIT, _BIT_HOLD_ON)

    @property
    def hold_off(self) -> bool:
        """Hold off enable/disable."""
        return self._device.read_register(_REGISTER_HOLD_CNTL_GRP0, self._index, _1_BIT, _BIT_HOLD_OFF)

    @hold_off.setter
    def hold_off(self, value: bool) -> bool:
        self._device.write_register(_REGISTER_HOLD_CNTL_GRP0, self._index, value, _1_BIT, _BIT_HOLD_OFF)

    @property
    def hold_on_time(self) -> int:
        """Hold On time - 0 (0s), 1 (0.25s), 2 (0.5s), 3 (0.75s), 4 (1s), 5 (2s), 6 (4s), 7 (6s)."""
        return self._device.read_register(_REGISTER_HOLD_CNTL_GRP0, self._index, _3_BITS, _BIT_HOLD_ON_TIME)

    @hold_on_time.setter
    def hold_on_time(self, value: int) -> int:
        if not 0 <= value <= 64:
            raise ValueError("Valid values are 0 (0s), 1 (0.25s), 2 (0.5s), 3 (0.75s), 4 (1s), 5 (2s), 6 (4s), 7 (6s)")
        self._device.write_register(_REGISTER_HOLD_CNTL_GRP0, self._index, value, _3_BITS, _BIT_HOLD_ON_TIME)

    @property
    def hold_off_time(self) -> int:
        """Hold On time  - 0 (0s), 1 (0.25s), 2 (0.5s), 3 (0.75s), 4 (1s), 5 (2s), 6 (4s), 7 (6s)."""
        return self._device.read_register(_REGISTER_HOLD_CNTL_GRP0, self._index, _3_BITS, _BIT_HOLD_OFF_TIME)

    @hold_off_time.setter
    def hold_off_time(self, value: int) -> int:
        if not 0 <= value <= 64:
            raise ValueError("Valid values are 0 (0s), 1 (0.25s), 2 (0.5s), 3 (0.75s), 4 (1s), 5 (2s), 6 (4s), 7 (6s)")
        self._device.write_register(_REGISTER_HOLD_CNTL_GRP0, self._index, value, _3_BITS, _BIT_HOLD_OFF_TIME)

    @property
    def output_gain_control(self) -> int:
        """Output current gain 0-255."""
        return self._device.read_register(_REGISTER_IREF_GRP0, self._index)

    @output_gain_control.setter
    def output_gain_control(self, value: int) -> int:
        if not 0 <= value <= 64:
            raise ValueError("Valid values are 0 (0s), 1 (0.25s), 2 (0.5s), 3 (0.75s), 4 (1s), 5 (2s), 6 (4s), 7 (6s)")
        self._device.write_register(_REGISTER_IREF_GRP0, self._index, value)


class Groups:  # pylint: disable=too-few-public-methods
    """Lazily creates and caches Group objects as needed. Treat it like a sequence.

    :param PCA9955 device: The PCA9955 device object
    """

    def __init__(self, device: "PCA9955") -> None:
        self._device = device
        self.groups = [None] * len(self)

    def __len__(self) -> int:
        return 16

    def __getitem__(self, index: int) -> Group:
        if not self.groups[index]:
            self.groups[index] = Group(self._device, index)
        return self.groups[index]


class PCA9955:
    """
    Initialise the PCA9955 chip at ``address`` on ``i2c_bus``.

    :param ~busio.I2C i2c_bus: The I2C bus which the PCA9955 is connected to.
    :param int address: The I2C address of the PCA9955.
    :param int reference_clock_speed: The frequency of the internal reference clock in Hertz.
    """


    def __init__(self, i2c: I2C, address: int) -> None:
        self._device = i2c_device.I2CDevice(i2c, address)
        self.channels = Channels(self)
        self.groups = Groups(self)

    def __enter__(self) -> "PCA9955":
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[type]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
        ) -> None:
        return False

    def deinit(self) -> None:
        """Stop using the PCA9955."""

    @property
    def brightness(self) -> int:
        """Global brightness 0 - 255."""
        raise AttributeError("brightness is write-only")

    @brightness.setter
    def brightness(self, value: int) -> int:
        self.write_8(_REGISTER_PWMALL, value)

    @property
    def output_current(self) -> int:
        """Global output currrent 0 - 255."""
        raise AttributeError("brightness is write-only")

    @output_current.setter
    def output_current(self, value: int) -> int:
        self.write_8(_REGISTER_IREALL, value)

    @property
    def over_temp(self) -> bool:
        """True indicates over temperature condition."""
        return bool(self.read_register(_REGISTER_MODE2,  mask = _1_BIT, offset = _BIT_OVERTEMP))

    @property
    def errors_exist(self) -> bool:
        """True indicates over temperature condition."""
        return bool(self.read_register(_REGISTER_MODE2,  mask = _1_BIT, offset = _BIT_ERROR))

    def read_register(self, base_register: int, index: int = 0, mask: int = 0xFF, offset: int = 0) -> int:
        """Read set of bits from register"""
        register = base_register + index
        mask = mask << offset
        result = self.read_8(register)
        return (result & mask) >> offset

    def write_register(self, base_register: int, index: int, value: int, mask: int = 0xFF, offset: int = 0) -> int:
        """Write set of bits to register"""
        register = base_register + index
        mask = mask << offset
        inverse_mask = ~mask & 0xFF
        current_value = self.read_8(register)
        value = (current_value & inverse_mask) | (value << offset)
        result = self.write_8(register, value)
        return (result & mask) >> offset

    def read_channel_config(self, base_register: int, index: int) -> int:
        """Read channel configuration register"""
        register = base_register + (index >> 2)
        offset = (index % 4) << 1
        mask = _2_BITS << offset
        result = self.read_8(register)
        return (result & mask) >> offset

    def write_channel_config(self, base_register: int, index: int, value: int) -> int:
        """Write channel configuration register"""
        register = base_register + (index >> 2)
        offset = (index % 4) << 1
        mask = _2_BITS << offset
        inverse_mask = ~mask & 0xFF
        current_value = self.read_8(register)
        value = (current_value & inverse_mask) | (value << offset)
        result = self.write_8(register, value)
        return (result & mask) >> offset

    def read_8(self, address: int) -> int:
        """ Read and return a byte from the specified 8-bit register address."""
        result = bytearray(1)
        with self._device as i2c:
            i2c.write(bytes([address]))
            i2c.readinto(result)
        return result[0]

    def write_8(self, address: int, value: int) -> int:
        """ write a byte to the specified 8-bit register address."""
        result = bytearray(1)
        with self._device as i2c:
            i2c.write(bytes([address, value]))
            i2c.write(bytes([address]))
            i2c.readinto(result)
        return result[0]
