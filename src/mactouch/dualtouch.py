"""Dual-boot additions kept separate from verified MacTouch 0.3 sources."""
import os,machine
from macextras import ExtrasDesktop

class DualDesktop(ExtrasDesktop):
    def __init__(self):
        super().__init__()
        self.tools.append('Boot Menu')
    def icon(self,kind,x,y):
        if kind=='Boot Menu':
            self.s.rect(x+3,y+2,30,27,1)
            self.s.hline(x+4,y+9,28,1)
            self.s.rect(x+7,y+14,9,9,1)
            self.s.rect(x+21,y+14,9,9,1)
        else:super().icon(kind,x,y)
    def open(self,app):
        if app=='Boot Menu':
            os.sync()
            print('RETURN_TO_BOOT_MENU')
            machine.reset()
        else:super().open(app)

def run():
    global desk
    desk=DualDesktop()
    print('MACTOUCH_DUALBOOT_READY')
    desk.run()
