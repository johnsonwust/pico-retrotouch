# SPDX-License-Identifier: MIT
"""Small monochrome ST7789 driver for Waveshare Pico-ResTouch-LCD-2.8.

The panel setup follows the working MIT-licensed Picontosh st7789.py driver
by Peter Hinch / Ihor Nehrutsa. No second full RGB framebuffer is allocated.
"""
import time
import framebuf
import micropython
from machine import Pin, SPI


@micropython.viper
def expand(src, dst, start: int, count: int):
    source = ptr8(src)
    target = ptr8(dst)
    for i in range(count):
        pixel = start + i
        value = 0
        if source[pixel >> 3] & (128 >> (pixel & 7)):
            value = 255
        target[i * 2] = value
        target[i * 2 + 1] = value


class Display(framebuf.FrameBuffer):
    def __init__(self):
        self.buffer = bytearray(320 * 240 // 8)
        super().__init__(self.buffer, 320, 240, framebuf.MONO_HLSB)
        self.txline = bytearray(640)
        self.lineview = memoryview(self.txline)
        self.dc = Pin(8, Pin.OUT, value=0)
        self.cs = Pin(9, Pin.OUT, value=1)
        self.rst = Pin(15, Pin.OUT, value=1)
        self.bl = Pin(13, Pin.OUT, value=1)
        self.sdcs = Pin(22, Pin.OUT, value=1)
        self.tpcs = Pin(16, Pin.OUT, value=1)
        self.spi = SPI(1, 40000000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(10)
        self.command(0x01)
        time.sleep_ms(150)
        self.command(0x11)
        time.sleep_ms(10)
        self.command(0x3a, b'\x55')
        self.command(0x20)
        self.command(0x13)
        self.command(0x36, b'\x60')
        self.command(0x29)
        self.fill(0)

    def command(self, value, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytes((value,)))
        if data is not None:
            self.dc(1)
            self.spi.write(data)
        self.cs(1)

    def show_rect(self, x=0, y=0, width=320, height=240):
        x0 = max(0, int(x))
        y0 = max(0, int(y))
        x1 = min(320, int(x + width))
        y1 = min(240, int(y + height))
        width = x1 - x0
        if width <= 0 or y1 <= y0:
            return
        self.spi.init(baudrate=40000000)
        self.command(0x2a, bytes((x0 >> 8, x0 & 255, (x1-1) >> 8, (x1-1) & 255)))
        self.command(0x2b, bytes((y0 >> 8, y0 & 255, (y1-1) >> 8, (y1-1) & 255)))
        self.dc(0)
        self.cs(0)
        self.spi.write(b'\x2c')
        self.dc(1)
        line = self.lineview[:width * 2]
        for row in range(y0, y1):
            expand(self.buffer, self.txline, row * 320 + x0, width)
            self.spi.write(line)
        self.cs(1)

    def show(self):
        self.show_rect()
