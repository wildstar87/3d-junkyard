import digitalio
import board
import neopixel
import math
import random
import array
import adafruit_ssd1306
import busio as io
import usb_host
import usb.core
import adafruit_usb_host_descriptors
from rainbowio import colorwheel

# Layout description:
# Lines are arrays containing key descriptions.
# Key descriptions can be a simple string if there's a normal offset of 1U from the
# previous key and if the width of the key is 1U.
# If a key has an offset, is wider or taller, define the key as a tuple with the'
# string description as the first element, the offset as the second, the width in
# keyboard units as the third and the height as the fourth.
keys = [
    ['Esc', ('F1', 1), 'F2', 'F3', 'F4', ('F5', 0.5), 'F6', 'F7', 'F8', ('F9', 0.5), 'F10', 'F11', 'F12', ('PrtSc', 0.5), 'ScrLck', 'Pause', ('Break', 0.5), 'Inverse', ('Power', 1)],
    ['`~', '1!', '2@', '3#', '4$', '5%', '6^', '7&', '8*', '9(', '0)', '-_', '=+', ('Backspace', 0, 2), ('Insert', 0.5), 'Home', 'PgUp', ('NumLck', 0.5), '/', '*', '-', ('Reset', 0.5)],
    [('Tab', 0, 1.5), 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[{', ']}', ('\|', 0, 1.5), ('Del', 0.5), 'End', 'PgDn', ('7', 0.5), '8', '9', ('+', 0, 1, 2), ('Option', 0.5)],
    [('CapsLck', 0, 1.75), 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';:', '\'\"', ('Return', 0, 2.25), ('4', 4), '5', '6', ('Select', 1.5)],
    [('LeftShift', 0, 2.25), 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',<', '.>', '/?', ('RightShift', 0, 2.75), ('Up', 1.5), ('1', 1.5), '2', '3', ('Enter', 0, 1, 2), ('Start', 0.5)],
    [('LeftControl', 0, 1.25), ('Win', 0, 1.25), ('LeftAlt', 0, 1.25), ('Space', 0, 6.25), ('RightAlt', 0, 1.25), ('Fn', 0, 1.25), ('Menu', 0, 1.25), ('RightControl', 0, 1.25), ('Left', 0.5), 'Down', 'Right', ('0', 0.5, 2), '.', ('Help', 1.5)]
]

# List of keys in the same order they are positioned on the PCB
leds = ['Power', 'Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'PrtSc', 'ScrLck', 'Pause',
    '`~', '1!', '2@', '3#', '4$', '5%', '6^', '7&', '8*', '9(', '0)', '-_', '=+', 'Backspace', 'Insert', 'Home', 'PgUp',
    'Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[{', ']}', '\|', 'Del', 'End', 'PgDn',
    'CapsLck', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';:', '\'\"', 'Return',
    'LeftShift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',<', '.>', '/?', 'RightShift', 'Up',
    'LeftControl', 'Win', 'LeftAlt', 'Space', 'RightAlt', 'Fn', 'Menu', 'RightControl', 'Left', 'Down', 'Right',
    'NumLck', '/', '*', '-', '7', '8', '9', '+', '4', '5', '6', '1', '2', '3', 'Enter', '0', '.',
    'Help', 'Start', 'Select', 'Option', 'Reset', 'Break', 'Inverse']

# Modifier key mask definitions
CONTROL = 0x11
SHIFT = 0x22
ALT = 0x44
WIN = 0x88

# Key code to name mapping
# Reference for the key codes: https://www.usb.org/sites/default/files/hut1_5.pdf#chapter.10
keymap = {
    0x66: "Power",
    0x29: "Esc", 0x3A: "F1", 0x3B: "F2", 0x3C: "F3", 0x3D: "F4", 0x3E: "F5", 0x3F: "F6", 0x40: "F7", 0x41: "F8", 0x42: "F9", 0x43: "F10", 0x44: "F11", 0x45: "F12", 0x46: "PrtSc", 0x47: "ScrLck", 0x48: "Pause",
    0x35: '`~', 0x1E: "1!", 0x1F: "2@", 0x20: "3#", 0x21: "4$", 0x22: "5%", 0x23: "6^", 0x24: "7&", 0x25: "8*", 0x26: "9(", 0x27: "0)", 0x2D: "-_", 0x2E: "=+", 0x2A: "Backspace", 0x49: 'Insert', 0x4A: 'Home', 0x4B: 'PgUp',
    0x2B: 'Tab', 0x14: 'Q', 0x1A: 'W', 0x08: 'E', 0x15: 'R', 0x17: 'T', 0x1C: 'Y', 0x18: 'U', 0x0C: 'I', 0x12: 'O', 0x13: 'P', 0x2F: '[{', 0x30: ']}', 0x31: '\|', 0x4C: 'Del', 0x4D: 'End', 0x4E: 'PgDn',
    0x39: 'CapsLck', 0x04: 'A', 0x16: 'S', 0x07: 'D', 0x09: 'F', 0x0A: 'G', 0x0B: 'H', 0x0D: 'J', 0x0E: 'K', 0x0F: 'L', 0x33: ';:', 0x34: '\'\"', 0x28: 'Return',
    0x102: 'LeftShift', 0x1D: 'Z', 0x1B: 'X', 0x06: 'C', 0x19: 'V', 0x05: 'B', 0x11: 'N', 0x10: 'M', 0x36: ',<', 0x37: '.>', 0x38: '/?', 0x120: 'RightShift', 0x52: 'Up',
    0x101: 'LeftControl', 0x108: 'Win', 0x104: 'LeftAlt', 0x2C: 'Space', 0x140: 'RightAlt', 0x180: 'Fn', 0x65: 'Menu', 0x110: 'RightControl', 0x50: 'Left', 0x51: 'Down', 0x4F: 'Right',
    0x53: 'NumLck', 0x54: '/', 0x55: '*', 0x56: '-', 0x5F: '7', 0x60: '8', 0x61: '9', 0x57: '+', 0x5C: '4', 0x5D: '5', 0x5E: '6', 0x59: '1', 0x5A: '2', 0x5B: '3', 0x58: 'Enter', 0x62: '0', 0x63: '.',
    0x75: 'Help', 0x74: 'Start', 0x77: 'Select', 0xA1: 'Option', 0x79: 'Reset', 0x78: 'Break', 0xCF: 'Inverse'
}

# Compute coordinates of each key:
# Name: (x, y, led_index)
coordinates = dict()
y = -0.5
for row in keys:
    x = -0.5
    for key in row:
        (name, offset, width, height) = (
            key if type(key) is str else key[0],
            key[1] if type(key) is tuple and len(key) > 1 else 0,
            key[2] if type(key) is tuple and len(key) > 2 else 1,
            key[3] if type(key) is tuple and len(key) > 3 else 1
            )
        coordinates[name] = (x + offset + width / 2, y + height / 2, leds.index(name) if name in leds else -1)
        x = x + width + offset
    y = y + (1.25 if y == 0 else 1)
#print(coordinates)

width = max([x for (x, _, _) in coordinates.values()])
height = max([y for (_, y, _) in coordinates.values()])
center = (width / 2, height / 2)

PIXEL_COUNT = sum([len(key) for key in keys])

# Some basic colors
BLACK = 0x000000
WHITE = 0xFFFFFF
PURPLE = 0x9400D3
BLUE = 0x0000FF
GREEN = 0x00FF00
YELLOW = 0xFFFF00
ORANGE = 0xFF8000
RED = 0xFF0000

# (K3, K4, K5): row number
K_to_row = {
    (False, False, False): 6,
    (True,  False, False): 1,
    (False, True,  False): 4,
    (True,  True,  False): 7,
    (False, False, True ): 2,
    (True,  False, True ): 8,
    (False, True,  True ): 3,
    (True,  True,  True ): 5
}

# (K0, K1, K2): col number
K_to_col = {
    (False, False, False): 7,
    (True,  False, False): 6,
    (False, True,  False): 3,
    (True,  True,  False): 8,
    (False, False, True ): 1,
    (True,  False, True ): 5,
    (False, True,  True ): 2,
    (True,  True,  True ): 4
}

# Setup the display
# VCC is just GPIO16 set to high and GND is GPIO17 set to low.
OLED_WIDTH = 128
OLED_HEIGHT = 32
OLED_SDA = board.GP28
OLED_SCK = board.VOLTAGE_MONITOR

oledI2C = io.I2C(OLED_SCK, OLED_SDA)
oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, oledI2C)
oledCol = 0

# Setup the mode button
mode_button = digitalio.DigitalInOut(board.GP26)
mode_button.switch_to_input(pull=digitalio.Pull.UP)

def log(str):
    global oledCol
    # Echo the string on both the console and the oled screen
    print(str)
    oled.scroll(0, -8)
    oled.fill_rect(0, OLED_HEIGHT - 8, OLED_WIDTH, 8, 0)
    oled.text(str, 0, OLED_HEIGHT - 8, 1)
    oled.show()
    oledCol = OLED_WIDTH / 6

def ch(chars):
    global oledCol
    print(chars)
    if oledCol + len(chars) > OLED_WIDTH / 6:
        oled.scroll(0, -8)
        oled.fill_rect(0, OLED_HEIGHT - 8, OLED_WIDTH, 8, 0)
        oledCol = 0
    oled.text(chars, oledCol * 6, OLED_HEIGHT - 8, 1)
    oled.show()
    oledCol = oledCol + len(chars)

def cls():
    oled.fill(0)
    oled.show()

log("DecentKeyboardTester")
log("(c) B. Le Roy 2025")

def modulate(color, intensity):
    intensity = max(0, min(1, intensity))
    red = math.ceil(((color & 0xFF0000) >> 16) * intensity)
    green = math.ceil(((color & 0xFF00) >> 8) * intensity)
    blue = math.ceil((color & 0xFF) * intensity)
    return (red << 16) | (green << 8) | blue

pixels = neopixel.NeoPixel(board.GP27, PIXEL_COUNT, auto_write = False)

def clear_keyboard():
    for i in range(PIXEL_COUNT):
        pixels[i] = 0
    pixels.show()

class Mode:
    def init(self):
        pass
    def loop(self):
        pass

class Animation(Mode):
    def __init__(self):
        self.frame_number = 0
    def loop(self):
        self.frame_number = self.frame_number + 1
        self.display_frame()
    def display_frame(self):
        for (key, (x, y, led_index)) in coordinates.items():
            pixels[led_index] = self.paint(x, y)
        pixels.show()
    def paint(self, x, y):
        return 0

class RadialRainbow(Animation):
    def __init__(self):
        super().__init__()
        self.name = "Radial Rainbow"
    def paint(self, x, y):
        return modulate(colorwheel((math.sqrt((x - center[0])**2 + (y - center[1])**2) * 20 + 256 - self.frame_number) % 256), 0.01)

class Droplet:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
        
class GhostInTheShell(Animation):
    def __init__(self):
        super().__init__()
        self.name = "Ghost in the Shell"
        self.droplets = []
    def display_frame(self):
        if (len(self.droplets) < 8):
            self.droplets.append(Droplet(
                x = width * random.random(),
                y = -random.random() * 10
            ))
        for droplet in self.droplets:
            droplet.y = droplet.y + 0.5
            if droplet.y > height + 10:
                self.droplets.remove(droplet)
        super().display_frame()
    def paint(self, x, y):
        intensity = 1
        for droplet in self.droplets:
            if abs(droplet.x - x) < 0.5 and y < droplet.y and y > droplet.y - 9:
                intensity = 10 - droplet.y + y
        return modulate(GREEN, intensity / 100)
    
class AnimationMode(Mode):
    def __init__(self):
        self.name = "Animations"
    def loop(self):
        self.animations[self.current_animation].loop()
        if (mode_button.value == False):
            self.current_animation = (self.current_animation + 1) % len(self.animations)
            cls()
            clear_keyboard()
            log(self.animations[self.current_animation].name)


DATA_PLUS = board.GP0
DATA_MINUS = board.GP1

keyboard_port = usb_host.Port(DATA_PLUS, DATA_MINUS)

DIR_IN = 0x80

class UsbKeyboardMode(Mode):
    def __init__(self):
        self.name = "USB Keyboard"
        self.keyboard = None
        self.keyboard_interface_address = None
        self.char = ""
        self.control = False
        self.alt = False
        self.shift = False
        self.win = False

    def init(self):
        pixels.fill(modulate(ORANGE, 0.01))
        pixels[coordinates['Power'][2]] = modulate(RED, 0.01)
        pixels.show()
        print("Starting USB discovery")
        # HID protocol reference: https://usb.org/sites/default/files/hid1_11.pdf
        for device in usb.core.find(find_all=True):
            config_descriptor = adafruit_usb_host_descriptors.get_configuration_descriptor(
                device, 0
            )

            i = 0
            while i < len(config_descriptor):
                descriptor_len = config_descriptor[i]
                descriptor_type = config_descriptor[i + 1]
                if descriptor_type == adafruit_usb_host_descriptors.DESC_INTERFACE:
                    interface_protocol = config_descriptor[i + 7]
                    if interface_protocol == 1 and self.keyboard == None:
                        log(f"{device.product}")
                        self.keyboard = device
                elif descriptor_type == adafruit_usb_host_descriptors.DESC_ENDPOINT:
                    endpoint_address = config_descriptor[i + 2]
                    if (endpoint_address & DIR_IN) and device == self.keyboard and interface_protocol == 1:
                        self.keyboard_interface_address = endpoint_address
                i += descriptor_len

        if self.keyboard != None and self.keyboard_interface_address != None:
            self.keyboard.set_configuration()
    def loop(self):
        if self.keyboard != None:
            try:
                buffer = array.array("i", range(1))

                self.keyboard.read(self.keyboard_interface_address, buffer)
                current_raw_code = buffer[0]
                print(current_raw_code) if current_raw_code != 0 else None

                current_key_code = (current_raw_code & 0xFF0000) >> 16
                current_modifier = current_raw_code & 0xFFFF

                self.char = keymap[current_key_code] if current_key_code in keymap else ""
                self.control = current_modifier & CONTROL != 0
                self.alt = current_modifier & ALT != 0
                self.shift = current_modifier & SHIFT != 0
                self.win = current_modifier & WIN != 0

                if current_key_code != 0:
                    ch(("CTRL + " if self.control else "") +
                       ("ALT + " if self.alt else "") +
                       ("SHIFT + " if self.shift else "") +
                       ("WIN + " if self.win else "") +
                       self.char if self.char != "" else "0x{:02x}".format(current_key_code))
                if current_key_code in keymap:
                    (_, _, led_index) = coordinates[keymap[current_key_code]]
                    pixels[led_index] = modulate(GREEN, 0.01)
                if current_raw_code | 0x100 in keymap:
                    (_, _, led_index) = coordinates[keymap[current_raw_code | 0x100]]
                    pixels[led_index] = modulate(GREEN, 0.01)
                pixels.show()

            except usb.core.USBTimeoutError:
                pass
            except usb.core.USBError:
                self.keyboard = None
                self.keyboard_interface_address = None

modes = [UsbKeyboardMode(), GhostInTheShell(), RadialRainbow()]
current_mode = 0
log('Mode: ' + modes[current_mode].name)
modes[current_mode].init()

while True:
    modes[current_mode].loop()
    if (mode_button.value == False):
        current_mode = (current_mode + 1) % len(modes)
        cls()
        clear_keyboard()
        log('Mode: ' + modes[current_mode].name)
        modes[current_mode].init()
        while (mode_button.value == False):
            pass
