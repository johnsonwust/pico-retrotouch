"""Shared SPI SD mount used by imports and MacTouch storage."""
import os,time
from machine import Pin,SPI
import sdcard_crc
spi=SPI(1,baudrate=1000000,sck=Pin(10),mosi=Pin(11),miso=Pin(12))
lcd=Pin(9,Pin.OUT,value=1)
touch=Pin(16,Pin.OUT,value=1)
cs=Pin(22,Pin.OUT,value=1)

class SharedCard(sdcard_crc.SDCard):
    def select_bus(self):
        lcd(1);touch(1)
        self.spi.init(baudrate=5000000,polarity=0,phase=0)
    def readblocks(self,block,buf):
        self.select_bus()
        return super().readblocks(block,buf)
    def writeblocks(self,block,buf):
        self.select_bus()
        return super().writeblocks(block,buf)
    def wait_ready(self):
        start=time.ticks_ms()
        while self.spi.read(1,0xff)[0]==0:
            if time.ticks_diff(time.ticks_ms(),start)>3000:raise OSError('SD write timeout')
    def write(self,token,buf):
        self.cs(0)
        try:
            self.spi.read(1,token);self.spi.write(buf);self.spi.write(b'\xff\xff')
            response=self.spi.read(1,0xff)[0]&31
            if response!=5:raise OSError('SD write rejected: %d'%response)
            self.wait_ready()
        finally:
            self.cs(1);self.spi.write(b'\xff')
    def write_token(self,token):
        self.cs(0)
        try:self.spi.read(1,token);self.spi.write(b'\xff');self.wait_ready()
        finally:self.cs(1);self.spi.write(b'\xff')

card=SharedCard(spi,cs,baudrate=5000000)
card.cmd(59,0,0)
os.mount(card,'/sd')
