# SPDX-License-Identifier: MIT
"""MacTouch: a small stylus desktop for RP2040 + Waveshare ResTouch 2.8.

Public-source variant using MicroPython's MIT-licensed 8x8 font. No Mac ROM, OS image, network or SD card is needed.
"""
import gc
import os
import time
import random
import json
import framebuf
from machine import Pin
import retro_font as font
from macdisplay import Display


class Touch:
    def __init__(self, screen):
        self.spi = screen.spi
        self.cs = screen.tpcs
        self.irq = Pin(17, Pin.IN, Pin.PULL_UP)
        self.tx = bytearray(3)
        self.rx = bytearray(3)
        # The XPT2046 is not reset when the Pico restarts. Explicitly leave
        # its ADC powered down with PENIRQ enabled before waiting for input.
        self.spi.init(baudrate=1000000)
        self.channel(0x90)
        self.cal = None
        try:
            with open('touch_cal.json') as f:
                self.cal = json.load(f)
        except (OSError, ValueError):
            pass

    def channel(self, command):
        self.tx[0] = command
        self.cs(0)
        self.spi.write_readinto(self.tx, self.rx)
        self.cs(1)
        return ((self.rx[1] << 8) | self.rx[2]) >> 3

    def raw(self):
        self.spi.init(baudrate=1000000)
        # Probe the ADC even if PENIRQ is high: this also recovers an XPT2046
        # left in a different power state by a previous program.
        x = self.channel(0xd0)
        y = self.channel(0x90)
        if not (80 <= x <= 4015 and 80 <= y <= 4015):
            return None
        xs = []
        ys = []
        # First reading after changing channel is discarded.
        for _ in range(5):
            self.channel(0xd0)
            xs.append(self.channel(0xd0))
            self.channel(0x90)
            ys.append(self.channel(0x90))
        self.channel(0x90)  # PD=00 leaves pen interrupt enabled.
        xs.sort()
        ys.sort()
        if xs[2] < 80 or xs[2] > 4015 or ys[2] < 80 or ys[2] > 4015:
            return None
        return xs[2], ys[2]

    def point(self):
        raw = self.raw()
        if raw is None or self.cal is None:
            return None
        x, y = raw
        a, b, c, d, e, f = self.cal
        return max(0, min(319, round(a*x+b*y+c))), max(0, min(239, round(d*x+e*y+f)))


class Desktop:
    def __init__(self):
        self.s = Display()
        self.touch = Touch(self.s)
        self.app = 'Desktop'
        self.start = time.ticks_ms()
        self.down = False
        self.previous = None
        self.hits = 0
        self.tools = ['Paint', 'Puzzle', 'Pet', 'Timer', 'Icons', 'About']
        self.eraser = False
        self.moves = 0
        self.tiles = list(range(1, 9)) + [0]
        self.pet_food = 0
        self.pet_sleep = False
        self.pet_hop = 0
        self.pet_tick = 0
        self.timer_seconds = 300
        self.timer_end = None
        self.last_second = -1
        self.icon_tick = 0

    def text(self, label, x, y, color=1):
        s = self.s
        for ch in str(label):
            if ch == ' ':
                x += 4
                continue
            data, h, w = font.get_ch(ch)
            if data is None:
                continue
            glyph = framebuf.FrameBuffer(bytearray(data[:-1]), 8 if w <= 8 else 16, h, framebuf.MONO_HLSB)
            if color:
                s.blit(glyph, x, y, 0)
            else:
                for yy in range(h):
                    for xx in range(w):
                        if glyph.pixel(xx, yy):
                            s.pixel(x+xx, y+yy, 0)
            x += w

    def centered(self, text, x, y, w):
        width = 0
        for ch in str(text):
            width += 4 if ch == ' ' else font.get_ch(ch)[2]
        self.text(text, x + (w-width)//2, y)

    def button(self, x, y, w, label, selected=False):
        s = self.s
        s.fill_rect(x, y, w, 23, 0)
        s.rect(x, y, w, 23, 1)
        if selected:
            s.rect(x+2, y+2, w-4, 19, 1)
        self.centered(label, x, y+5, w)

    def menubar(self):
        s = self.s
        s.fill_rect(0, 0, 320, 21, 0)
        s.hline(0, 20, 320, 1)
        self.text('Desk', 10, 4)
        self.text('Help', 62, 4)
        self.text('MacTouch', 121, 4)
        elapsed = time.ticks_diff(time.ticks_ms(), self.start)//1000
        self.text('%02d:%02d' % (elapsed//60, elapsed%60), 273, 4)

    def background(self):
        s = self.s
        tile = framebuf.FrameBuffer(bytearray(b'\x88\x22'*4), 8, 8, framebuf.MONO_HLSB)
        for y in range(24, 240, 8):
            for x in range(0, 320, 8):
                s.blit(tile, x, y)
        self.menubar()

    def window(self, title):
        s = self.s
        self.background()
        s.fill_rect(10, 29, 304, 203, 1)
        s.fill_rect(7, 26, 304, 203, 0)
        s.rect(7, 26, 304, 203, 1)
        for y in range(30, 44, 2):
            s.hline(11, y, 296, 1)
        s.fill_rect(103, 29, 114, 17, 0)
        self.centered(title, 103, 31, 114)
        s.fill_rect(14, 29, 22, 17, 0)
        s.rect(19, 32, 12, 11, 1)
        s.hline(8, 47, 302, 1)

    def icon(self, kind, x, y):
        s = self.s
        if kind == 'Paint':
            s.rect(x+3, y+2, 31, 28, 1)
            s.line(x+10, y+23, x+28, y+5, 1)
            s.line(x+11, y+24, x+29, y+6, 1)
            s.line(x+10, y+23, x+8, y+27, 1)
        elif kind == 'Puzzle':
            for row in range(3):
                for col in range(3):
                    if row != 2 or col != 2:
                        s.rect(x+col*11, y+row*10, 10, 9, 1)
        elif kind == 'Pet':
            s.rect(x+4, y+8, 27, 22, 1)
            s.line(x+4, y+8, x+4, y, 1)
            s.line(x+4, y, x+14, y+8, 1)
            s.line(x+22, y+8, x+31, y, 1)
            s.vline(x+31, y, 8, 1)
            s.fill_rect(x+10, y+15, 3, 3, 1)
            s.fill_rect(x+23, y+15, 3, 3, 1)
            s.hline(x+15, y+23, 8, 1)
        elif kind == 'Timer':
            s.ellipse(x+18, y+17, 15, 15, 1)
            s.line(x+18, y+17, x+18, y+7, 1)
            s.line(x+18, y+17, x+26, y+17, 1)
        elif kind == 'Icons':
            s.rect(x, y+7, 35, 24, 1)
            s.rect(x+2, y+3, 13, 5, 1)
            s.hline(x, y+12, 35, 1)
        else:
            s.rect(x+3, y+1, 29, 30, 1)
            self.text('i', x+15, y+8)

    def desktop(self):
        self.app = 'Desktop'
        self.background()
        for i, name in enumerate(self.tools):
            x = 25 + (i%3)*102
            y = 48 + (i//3)*82
            self.s.fill_rect(x-9, y-4, 88, 61, 0)
            self.icon(name, x+15, y)
            self.centered(name, x-8, y+38, 86)
        self.s.fill_rect(0, 219, 320, 21, 0)
        self.centered('Tap an icon with the stylus', 0, 223, 320)
        self.s.show()

    def open(self, app):
        print('OPEN', app)
        self.app = app
        self.previous = None
        self.window(app)
        if app == 'Paint':
            self.eraser = False
            self.paint_tools()
        elif app == 'Puzzle':
            self.shuffle()
            self.puzzle_draw()
        elif app == 'Pet':
            self.pet_draw()
        elif app == 'Timer':
            self.timer_draw()
        elif app == 'About':
            gc.collect()
            self.text('A tiny, touchable desktop.', 22, 61)
            self.text('Pico RP2040 / 320 x 240', 22, 84)
            self.text('No Mac ROM or SD required.', 22, 107)
            self.text('Free RAM: %d KB' % (gc.mem_free()//1024), 22, 130)
            self.text('Desk: home. Box: close window.', 22, 153)
            self.button(22, 185, 125, 'Calibrate')
            self.button(161, 185, 132, 'Touch test')
        elif app == 'Touch test':
            self.text('Draw here. Desk returns home.', 20, 58)
        elif app == 'Icons':
            self.text('Tap anywhere to leave.', 64, 200)
            self.icon_tick = 0
        self.s.show()

    def paint_tools(self):
        self.s.rect(16, 57, 288, 139, 1)
        self.button(17, 201, 62, 'Clear')
        self.button(89, 201, 54, 'Pen', not self.eraser)
        self.button(153, 201, 65, 'Eraser', self.eraser)
        self.button(228, 201, 74, 'Save')

    def shuffle(self):
        self.tiles = list(range(1, 9)) + [0]
        previous = -1
        for _ in range(60):
            blank = self.tiles.index(0)
            choices = [i for i in range(9) if abs(i//3-blank//3)+abs(i%3-blank%3)==1 and i != previous]
            move = random.choice(choices)
            self.tiles[blank], self.tiles[move] = self.tiles[move], self.tiles[blank]
            previous = blank
        self.moves = 0

    def puzzle_draw(self):
        s = self.s
        s.fill_rect(16, 53, 286, 147, 0)
        self.text('Moves', 21, 76)
        self.text(str(self.moves), 35, 97)
        for i, value in enumerate(self.tiles):
            x = 91 + (i%3)*46
            y = 58 + (i//3)*46
            s.rect(x, y, 44, 44, 1)
            if value:
                self.centered(str(value), x, y+15, 44)
        self.button(117, 202, 85, 'Shuffle')
        if self.tiles == list(range(1, 9)) + [0]:
            self.text('Solved!', 237, 103)

    def pet_draw(self):
        s = self.s
        s.fill_rect(16, 53, 286, 144, 0)
        self.centered('Zzz...' if self.pet_sleep else ('Purr...' if self.pet_food else 'Hello, friend!'), 18, 58, 284)
        y = 100 - (9 if self.pet_hop%2 else 0)
        x = 127
        s.fill_rect(x, y, 64, 55, 1)
        s.fill_rect(x+3, y+3, 58, 49, 0)
        s.line(x, y, x, y-16, 1)
        s.line(x, y-16, x+19, y, 1)
        s.line(x+44, y, x+63, y-16, 1)
        s.vline(x+63, y-16, 17, 1)
        for eye in (x+14, x+44):
            if self.pet_sleep:
                s.hline(eye, y+21, 9, 1)
            else:
                s.fill_rect(eye, y+16, 7, 9, 1)
        s.line(x+27, y+32, x+32, y+37, 1)
        s.line(x+32, y+37, x+37, y+32, 1)
        s.line(x+6, y+31, x-13, y+27, 1)
        s.line(x+57, y+31, x+77, y+27, 1)
        self.centered('Treats: %d' % self.pet_food, 18, 174, 284)
        self.button(47, 201, 98, 'Feed')
        self.button(173, 201, 98, 'Wake' if self.pet_sleep else 'Nap')

    def timer_draw(self):
        s = self.s
        left = self.timer_seconds
        if self.timer_end is not None:
            left = max(0, time.ticks_diff(self.timer_end, time.ticks_ms())//1000)
            if left == 0:
                self.timer_end = None
                self.timer_seconds = 0
        s.fill_rect(17, 54, 285, 139, 0)
        self.centered('Time is up!' if left == 0 else 'A little time to focus.', 18, 61, 284)
        self.centered('%02d : %02d' % (left//60, left%60), 18, 91, 284)
        self.button(40, 126, 65, '1 min')
        self.button(126, 126, 65, '5 min')
        self.button(212, 126, 65, '25 min')
        self.button(66, 169, 81, 'Pause' if self.timer_end is not None else 'Start')
        self.button(174, 169, 81, 'Reset')
        self.centered('Visual timer - no speaker', 18, 208, 284)

    def calibrate(self):
        targets = ((28, 65), (291, 65), (28, 210), (291, 210))
        while True:
            samples = []
            for i, (x, y) in enumerate(targets):
                # Discard an existing press BEFORE showing the next target,
                # so a quick press on the newly shown cross is not swallowed.
                while self.touch.raw() is not None:
                    time.sleep_ms(10)
                self.window('Touch setup')
                self.centered('Tap cross %d of 4' % (i+1), 12, 99, 296)
                self.centered('Touch the cross, then lift.', 12, 123, 296)
                self.s.hline(x-10, y, 21, 1)
                self.s.vline(x, y-10, 21, 1)
                self.s.rect(x-4, y-4, 9, 9, 1)
                self.s.show()
                raw = None
                while raw is None:
                    raw = self.touch.raw()
                    if raw is None:
                        time.sleep_ms(10)
                samples.append(raw)
                print('CAL_POINT', i+1, raw)
                self.s.fill_rect(13, 95, 294, 50, 0)
                self.centered('Got it! Lift the pen.', 12, 105, 296)
                self.s.fill_rect(x-4, y-4, 9, 9, 1)
                self.s.show()
                while self.touch.raw() is not None:
                    time.sleep_ms(10)
            x0, y0 = samples[0]
            ux, uy = samples[1][0]-x0, samples[1][1]-y0
            vx, vy = samples[2][0]-x0, samples[2][1]-y0
            det = ux*vy-vx*uy
            if abs(det) < 10000:
                print('CAL_RETRY degenerate points')
                continue
            a, b = 263*vy/det, -263*vx/det
            d, e = -145*uy/det, 145*ux/det
            cal = [a,b,28-a*x0-b*y0,d,e,65-d*x0-e*y0]
            rx, ry = samples[3]
            error = abs(a*rx+b*ry+cal[2]-291)+abs(d*rx+e*ry+cal[5]-210)
            if error <= 38:
                break
            print('CAL_RETRY validation error', error)
        self.touch.cal = cal
        with open('touch_cal.json', 'w') as f:
            json.dump(cal, f)
        print('CAL_OK error', error)
        self.down = False
        self.desktop()

    def click(self, x, y):
        self.hits += 1
        print('TAP', self.hits, x, y, self.app)
        if y < 22:
            if x < 55:
                self.desktop()
            elif x < 104:
                self.open('About')
            return
        if self.app != 'Desktop' and 12 <= x <= 42 and 26 <= y <= 48:
            self.desktop()
            return
        if self.app == 'Desktop':
            for i, name in enumerate(self.tools):
                ix, iy = 16+(i%3)*102, 44+(i//3)*82
                if ix <= x <= ix+88 and iy <= y <= iy+61:
                    self.open(name)
                    return
        elif self.app == 'Paint' and y >= 199:
            if x < 83:
                self.s.fill_rect(17,58,286,137,0)
                self.s.show_rect(16,57,288,139)
            elif x < 148:
                self.eraser = False
            elif x < 223:
                self.eraser = True
            else:
                with open('drawing.pbm', 'wb') as f:
                    f.write(b'P4\n320 240\n')
                    f.write(self.s.buffer)
                print('DRAWING_SAVED drawing.pbm')
                self.button(228,201,74,'Saved')
                self.s.show_rect(228,201,74,23)
                return
            self.paint_tools()
            self.s.show_rect(16,200,288,25)
        elif self.app == 'Puzzle':
            if 117 <= x <= 202 and 202 <= y <= 227:
                self.shuffle()
            elif 91 <= x < 229 and 58 <= y < 196:
                i = ((y-58)//46)*3+(x-91)//46
                blank = self.tiles.index(0)
                if abs(i//3-blank//3)+abs(i%3-blank%3)==1:
                    self.tiles[i],self.tiles[blank]=self.tiles[blank],self.tiles[i]
                    self.moves += 1
            self.puzzle_draw()
            self.s.show_rect(16,53,288,174)
        elif self.app == 'Pet':
            if (47 <= x <= 145 and y >= 199) or (120 <= x <= 200 and 80 <= y <= 165):
                self.pet_food = min(99,self.pet_food+1)
                self.pet_hop = 6
                self.pet_sleep = False
            elif 173 <= x <= 271 and y >= 199:
                self.pet_sleep = not self.pet_sleep
            self.pet_draw()
            self.s.show_rect(16,53,288,173)
        elif self.app == 'Timer':
            if 126 <= y <= 151:
                self.timer_seconds = 60 if x < 115 else (300 if x < 202 else 1500)
                self.timer_end = None
            elif 169 <= y <= 193 and x < 160:
                if self.timer_end is None:
                    if self.timer_seconds <= 0:
                        self.timer_seconds = 300
                    self.timer_end = time.ticks_add(time.ticks_ms(), self.timer_seconds*1000)
                else:
                    self.timer_seconds = max(0,time.ticks_diff(self.timer_end,time.ticks_ms())//1000)
                    self.timer_end = None
            elif 169 <= y <= 193:
                self.timer_end = None
                self.timer_seconds = 300
            self.timer_draw()
            self.s.show_rect(16,53,288,173)
        elif self.app == 'About' and 181 <= y <= 214:
            if x < 154:
                self.calibrate()
            else:
                self.open('Touch test')
        elif self.app == 'Icons':
            self.desktop()

    def draw_point(self, point):
        x,y = point
        if self.app == 'Paint' and 20 <= x <= 299 and 61 <= y <= 192:
            old = self.previous or point
            color = 0 if self.eraser else 1
            self.s.line(old[0],old[1],x,y,color)
            size = 5 if self.eraser else 3
            self.s.fill_rect(x-size//2,y-size//2,size,size,color)
            self.s.show_rect(min(old[0],x)-3,min(old[1],y)-3,abs(old[0]-x)+7,abs(old[1]-y)+7)
            self.previous = point
        elif self.app == 'Touch test' and 78 <= y <= 215:
            self.s.fill_rect(x-2,y-2,5,5,1)
            self.s.show_rect(x-2,y-2,5,5)

    def tick(self):
        now = time.ticks_ms()
        second = time.ticks_diff(now,self.start)//1000
        if second != self.last_second:
            self.last_second = second
            self.menubar()
            self.s.show_rect(268,0,52,20)
            if self.app == 'Timer' and self.timer_end is not None:
                self.timer_draw()
                self.s.show_rect(17,54,285,138)
        if self.app == 'Pet' and self.pet_hop and time.ticks_diff(now,self.pet_tick)>160:
            self.pet_tick = now
            self.pet_hop -= 1
            self.pet_draw()
            self.s.show_rect(16,53,288,144)
        if self.app == 'Icons' and time.ticks_diff(now,self.icon_tick)>2000:
            self.icon_tick = now
            x,y = random.randint(12,140),random.randint(50,107)
            s=self.s
            s.fill_rect(x+2,y+2,158,95,1)
            s.fill_rect(x,y,158,95,0)
            s.rect(x,y,158,95,1)
            for line in range(4,16,2):
                s.hline(x+2,y+line,154,1)
            s.fill_rect(x+38,y+2,90,16,0)
            name=random.choice(self.tools[:4])
            self.centered(name,x+38,y+3,90)
            s.hline(x,y+19,158,1)
            self.icon(name,x+62,y+39)
            self.s.show_rect(x,y,161,98)

    def run(self):
        gc.collect()
        print('MACTOUCH_READY RAM_FREE',gc.mem_free(),'FB_BYTES',len(self.s.buffer))
        if self.touch.cal is None:
            print('CALIBRATION_REQUIRED: tap four crosses')
            self.calibrate()
        else:
            self.desktop()
        last_gc=time.ticks_ms()
        release_count=0
        while True:
            point=self.touch.point()
            if point is not None:
                release_count=0
                previous_app=self.app
                if not self.down:
                    self.down=True
                    self.previous=None
                    self.click(*point)
                if self.app == previous_app:
                    self.draw_point(point)
            else:
                release_count+=1
                if release_count >= 2:
                    self.down=False
                    self.previous=None
            self.tick()
            if time.ticks_diff(time.ticks_ms(),last_gc)>5000:
                gc.collect()
                last_gc=time.ticks_ms()
            time.sleep_ms(15)


def run():
    Desktop().run()
