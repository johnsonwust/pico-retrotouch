# SPDX-License-Identifier: MIT
"""Original touch miniatures: Notes, Puck, Glider and Castle. No Mac binaries."""
import gc
import os
import time
import json
from macclassic import ClassicDesktop

GAMES = ('Puck', 'Glider', 'Castle')
BODY_START, BODY_END = 50*40, 198*40


class ExtrasDesktop(ClassicDesktop):
    def __init__(self):
        super().__init__()
        self.tools = ['Boot', 'Paint', 'Gallery', 'Maze', 'Cards', 'Puzzle',
                      'Notes', 'Puck', 'Glider', 'Castle', 'Pet', 'Timer', 'Icons', 'About']
        self.desk_page = 0
        self.note_text = ''
        self.note_cursor = 0
        self.note_id = None
        self.note_shift = False
        self.note_symbols = False
        self.note_message = 'English notes / tap to type'
        self.note_browse = False
        self.note_page = 0
        self.note_items = []
        self.note_scroll = 0
        self.input_point = None
        self.game_bg = None
        self.game_last = time.ticks_ms()
        self.puck_new()
        self.glider_new()
        self.castle_new()

    def pause_games(self):
        for name in ('puck_state', 'glider_state', 'castle_state'):
            if getattr(self, name, None) == 'running':
                setattr(self, name, 'paused')
        self.input_point = None

    def desktop(self):
        self.pause_games()
        self.app = 'Desktop'
        self.previous = None
        self.stroke_started = False
        self.background()
        for i, name in enumerate(self.tools[self.desk_page*12:self.desk_page*12+12]):
            x, y = 8+(i%4)*79, 39+(i//4)*59
            self.s.fill_rect(x, y-3, 73, 55, 0)
            self.icon(name, x+18, y)
            self.centered(name, x, y+35, 73)
        self.s.fill_rect(0, 219, 320, 21, 0)
        self.small_button(8, 219, 70, 'Prev', 20)
        self.centered('Classic / %d of 2' % (self.desk_page+1), 79, 222, 162)
        self.small_button(242, 219, 70, 'Next', 20)
        self.s.show()

    def small_button(self, x, y, w, text, h=19, selected=False):
        self.s.fill_rect(x,y,w,h,0)
        self.s.rect(x,y,w,h,1)
        if selected:
            self.s.rect(x+2,y+2,w-4,h-4,1)
        self.centered(text,x,y+3,w)

    def icon(self, kind, x, y):
        s = self.s
        if kind == 'Notes':
            s.rect(x+5,y,26,31,1)
            for yy in range(6,27,5):
                s.hline(x+10,y+yy,16,1)
        elif kind == 'Puck':
            s.rect(x+3,y,29,32,1)
            s.hline(x+3,y+16,29,1)
            s.hline(x+11,y+5,12,1)
            s.hline(x+11,y+27,12,1)
            s.ellipse(x+20,y+19,3,3,1)
        elif kind == 'Glider':
            s.line(x,y+7,x+35,y+2,1)
            s.line(x+35,y+2,x+10,y+30,1)
            s.line(x+10,y+30,x+13,y+13,1)
            s.line(x+13,y+13,x,y+7,1)
            s.line(x+13,y+13,x+35,y+2,1)
        elif kind == 'Castle':
            s.rect(x+4,y+8,28,24,1)
            for xx in (4,15,26):
                s.rect(x+xx,y,6,9,1)
            s.rect(x+14,y+20,8,12,1)
            s.rect(x+9,y+12,3,4,1)
            s.rect(x+24,y+12,3,4,1)
        else:
            super().icon(kind,x,y)

    def open(self, app):
        if self.app in GAMES and self.app != app:
            self.pause_games()
        self.input_point = None
        if app not in ('Notes',) + GAMES:
            return super().open(app)
        self.app = app
        self.previous = None
        print('OPEN', app)
        if app == 'Notes':
            self.notes_draw()
        else:
            self.game_last = time.ticks_ms()
            self.game_draw()
        self.s.show()

    def high_score(self, name, value):
        records = self.records_load()
        if value > records.get(name,0):
            records[name] = value
            try:
                self.store.write_json('records.json',records)
            except OSError as exc:
                print('GAME_RECORD_ERROR',exc)

    # ---- Small English word processor ----------------------------------
    def note_lines(self):
        lines = []
        start = 0
        for i, ch in enumerate(self.note_text):
            if ch == '\n':
                lines.append((start,i))
                start = i+1
            elif i-start >= 33:
                lines.append((start,i))
                start = i
        lines.append((start,len(self.note_text)))
        return lines

    def note_keys(self):
        if self.note_symbols:
            return ('1234567890','-/:;()@#%=','+*_\'"!?.,&')
        rows = ('qwertyuiop','asdfghjkl','zxcvbnm.,?')
        return tuple(row.upper() for row in rows) if self.note_shift else rows

    def notes_draw(self):
        self.window('Notes')
        if self.note_browse:
            try:
                data = self.store.read_json('notes.json',{'items':[]})
                items = data['items']
                assert isinstance(items,list) and len(items) <= 12
                for item in items:
                    assert isinstance(item['id'],int) and isinstance(item['text'],str) and len(item['text']) <= 768
                self.note_items = items
            except (OSError,ValueError,KeyError,TypeError,AssertionError) as exc:
                self.note_items = []
                self.note_message = 'Could not read notes.'
                print('NOTES_READ_ERROR',exc)
            self.text('%s / %d notes' % (self.store.medium,len(self.note_items)),23,56)
            if not self.note_items:
                self.text('Your notebook is empty.',23,94)
            for i,item in enumerate(self.note_items[self.note_page*5:self.note_page*5+5]):
                yy = 80+i*22
                self.s.rect(22,yy,275,21,1)
                title = item['text'].split('\n')[0][:28] or '(empty note)'
                self.s.text(title,28,yy+6,1)
            self.button(19,202,84,'Prev')
            self.button(117,202,84,'Next')
            self.button(215,202,84,'Back')
        else:
            self.note_editor()
            for x,w,label in ((19,44,'New'),(68,48,'Open'),(121,48,'Save'),(174,57,'Shift'),(236,63,'Bksp')):
                self.small_button(x,106,w,label,19,label=='Shift' and self.note_shift)
            for row,keys in enumerate(self.note_keys()):
                start = (320-len(keys)*27)//2
                for col,ch in enumerate(keys):
                    self.small_button(start+col*27,130+row*22,25,ch,20)
            for x,w,label in ((19,44,'ABC' if self.note_symbols else '123'),(68,90,'Space'),
                              (163,60,'Enter'),(228,32,'<'),(265,32,'>')):
                self.small_button(x,202,w,label,23)
        self.s.show_rect(8,26,304,203)
        if not self.note_browse:
            self.note_feedback()

    def note_editor(self):
        self.s.fill_rect(18,53,283,51,0)
        self.s.rect(18,53,283,51,1)
        lines = self.note_lines()
        current = 0
        for i,(start,end) in enumerate(lines):
            if start <= self.note_cursor <= end:
                current = i
        self.note_scroll = max(0,current-4)
        for i,(start,end) in enumerate(lines[self.note_scroll:self.note_scroll+5]):
            yy = 57+i*9
            self.s.text(self.note_text[start:end],24,yy,1)
            if i+self.note_scroll == current:
                self.s.vline(24+(self.note_cursor-start)*8,yy,8,1)
        self.s.fill_rect(19,126,282,3,0)

    def note_insert(self, value):
        if len(self.note_text)+len(value) > 768:
            self.note_message = 'Note is full (768 characters).'
            return
        i = self.note_cursor
        self.note_text = self.note_text[:i]+value+self.note_text[i:]
        self.note_cursor += len(value)
        self.note_message = 'Unsaved changes'

    def note_save(self):
        try:
            data = self.store.read_json('notes.json',{'items':[]})
            items = data['items']
            assert isinstance(items,list) and len(items) <= 12
            found = next((i for i,item in enumerate(items) if item['id']==self.note_id),None)
            if found is None:
                if len(items) >= 12:
                    self.note_message = 'Notebook full: 12 notes.'
                    return
                number = max([item['id'] for item in items]+[0])+1
                items.append({'id':number,'text':self.note_text})
            else:
                number = self.note_id
                items[found] = {'id':number,'text':self.note_text}
            self.store.write_json('notes.json',{'items':items})
            self.note_id = number
            self.note_message = 'Saved to ' + self.store.medium
        except (OSError,ValueError,KeyError,TypeError,AssertionError) as exc:
            self.note_message = 'Save failed. Check storage.'
            print('NOTES_SAVE_ERROR',exc)

    def note_feedback(self):
        self.s.fill_rect(19,126,282,3,0)
        self.s.fill_rect(8,229,302,10,0)
        self.s.text(self.note_message[:36],16,231,1)
        self.s.show_rect(8,229,302,10)

    def notes_click(self,x,y):
        if self.note_browse:
            if 80 <= y < 190 and 22 <= x < 297:
                i = self.note_page*5+(y-80)//22
                if i < len(self.note_items):
                    item = self.note_items[i]
                    self.note_text,self.note_id = item['text'],item['id']
                    self.note_cursor = len(self.note_text)
                    self.note_browse = False
                    self.note_message = 'Opened note %d' % self.note_id
            elif 202 <= y < 225:
                if x < 105:
                    self.note_page = max(0,self.note_page-1)
                elif x < 205:
                    self.note_page = min(max(0,(len(self.note_items)-1)//5),self.note_page+1)
                else:
                    self.note_browse = False
            self.notes_draw()
            return
        redraw = False
        if 54 <= y < 104:
            lines = self.note_lines()
            row = min(len(lines)-1,self.note_scroll+max(0,(y-57)//9))
            start,end = lines[row]
            self.note_cursor = min(end,start+max(0,(x-24+4)//8))
        elif 106 <= y < 125:
            if 19 <= x < 63:
                self.note_text,self.note_cursor,self.note_id = '',0,None
                self.note_message = 'New note'
            elif 68 <= x < 116:
                self.note_browse,self.note_page = True,0
                redraw = True
            elif 121 <= x < 169:
                self.note_save()
            elif 174 <= x < 231:
                self.note_shift = not self.note_shift
                redraw = True
            elif 236 <= x < 299 and self.note_cursor:
                i = self.note_cursor
                self.note_text = self.note_text[:i-1]+self.note_text[i:]
                self.note_cursor -= 1
                self.note_message = 'Unsaved changes'
        elif 130 <= y < 194:
            row = (y-130)//22
            keys = self.note_keys()[row]
            start = (320-len(keys)*27)//2
            col = (x-start)//27
            if 0 <= col < len(keys) and (y-130)%22 < 20:
                self.note_insert(keys[col])
        elif 202 <= y < 225:
            if 19 <= x < 63:
                self.note_symbols = not self.note_symbols
                redraw = True
            elif 68 <= x < 158:
                self.note_insert(' ')
            elif 163 <= x < 223:
                self.note_insert('\n')
            elif 228 <= x < 260:
                self.note_cursor = max(0,self.note_cursor-1)
            elif 265 <= x < 297:
                self.note_cursor = min(len(self.note_text),self.note_cursor+1)
        if redraw:
            self.notes_draw()
        else:
            self.note_editor()
            self.s.show_rect(18,53,283,51)
        self.note_feedback()

    # ---- Common small-game drawing ------------------------------------
    def state(self):
        return getattr(self,self.app.lower()+'_state')

    def game_snapshot(self):
        if self.game_bg is None:
            self.game_bg = bytearray(BODY_END-BODY_START)
        self.game_bg[:] = memoryview(self.s.buffer)[BODY_START:BODY_END]

    def game_restore(self):
        memoryview(self.s.buffer)[BODY_START:BODY_END] = self.game_bg

    def dirty_pair(self,old,new):
        x0,y0 = min(old[0],new[0]),min(old[1],new[1])
        x1,y1 = max(old[0]+old[2],new[0]+new[2]),max(old[1]+old[3],new[1]+new[3])
        x0,y0,x1,y1 = max(9,x0),max(50,y0),min(310,x1),min(198,y1)
        if x1>x0 and y1>y0:
            self.s.show_rect(x0,y0,x1-x0,y1-y0)

    def overlay(self,title,line1,line2):
        s = self.s
        s.fill_rect(55,94,210,72,0)
        s.rect(55,94,210,72,1)
        self.centered(title,55,102,210)
        self.s.text(line1[:24],64,126,1)
        self.s.text(line2[:24],64,143,1)

    def game_draw(self):
        self.window(self.app)
        if self.app == 'Puck':
            self.puck_static()
        elif self.app == 'Glider':
            self.glider_static()
        else:
            self.castle_static()
        self.game_snapshot()
        self.game_actors()
        if self.app == 'Puck':
            self.puck_rects = self.puck_rectangles()
        state = self.state()
        if state != 'running':
            if state == 'won':
                self.overlay('You did it!','A tiny victory.','Tap New to play again.')
            elif state == 'over':
                self.overlay('Try again!','One more adventure?','Tap New to restart.')
            elif self.app == 'Puck':
                self.overlay('Air Hockey','Drag to move your paddle.','First to 5. Tap Start.')
            elif self.app == 'Glider':
                self.overlay('Paper Glider','Hold Lift or touch sky.','Avoid shelves. Tap Lift.')
            else:
                self.overlay('Castle Adventure','Hold arrows. Jump / Throw.','Tap the scene to start.')
        self.s.show_rect(8,26,304,203)

    def game_actors(self):
        if self.app == 'Puck':
            self.puck_actors()
        elif self.app == 'Glider':
            self.glider_actors()
        else:
            self.castle_actors()

    # ---- Air hockey ----------------------------------------------------
    def puck_new(self):
        self.puck_state = 'ready'
        self.puck_you,self.puck_cpu = 0,0
        self.puck_player,self.puck_ai = 160.,160.
        self.puck_x,self.puck_y = 160.,128.
        self.puck_vx,self.puck_vy = 35.,-65.
        self.puck_wait = 0

    def puck_static(self):
        s = self.s
        s.rect(23,64,274,132,1)
        for x in range(26,294,10):
            s.hline(x,129,5,1)
        s.ellipse(160,129,19,13,1)
        self.button(19,202,84,'Start')
        self.button(117,202,84,'Resume' if self.puck_state=='paused' else 'Pause')
        self.button(215,202,84,'New')

    def puck_actors(self):
        self.s.fill_rect(24,50,272,12,0)
        self.centered('You %d : %d CPU' % (self.puck_you,self.puck_cpu),24,50,272)
        self.s.fill_rect(int(self.puck_player)-23,180,46,7,1)
        self.s.fill_rect(int(self.puck_ai)-21,73,42,7,1)
        self.s.ellipse(int(self.puck_x),int(self.puck_y),4,4,1,True)

    def puck_rectangles(self):
        return ((int(self.puck_x)-6,int(self.puck_y)-6,13,13),
                (int(self.puck_player)-25,178,50,12),(int(self.puck_ai)-23,71,46,12))

    def puck_step(self,dt):
        if self.puck_state != 'running':
            return
        if time.ticks_diff(time.ticks_ms(),self.puck_wait)<0:
            return
        delta = max(-53*dt,min(53*dt,self.puck_x-self.puck_ai))
        self.puck_ai = max(46.,min(274.,self.puck_ai+delta))
        old_y = self.puck_y
        self.puck_x += self.puck_vx*dt
        self.puck_y += self.puck_vy*dt
        if self.puck_x < 29:
            self.puck_x,self.puck_vx = 29.,abs(self.puck_vx)
        elif self.puck_x > 291:
            self.puck_x,self.puck_vx = 291.,-abs(self.puck_vx)
        if self.puck_vy>0 and old_y<=176 and self.puck_y>=176 and abs(self.puck_x-self.puck_player)<=27:
            self.puck_y = 176.
            self.puck_vy = -min(145.,abs(self.puck_vy)+6)
            self.puck_vx = (self.puck_x-self.puck_player)*3.4
        elif self.puck_vy<0 and old_y>=84 and self.puck_y<=84 and abs(self.puck_x-self.puck_ai)<=25:
            self.puck_y = 84.
            self.puck_vy = min(145.,abs(self.puck_vy)+5)
            self.puck_vx = (self.puck_x-self.puck_ai)*3.1+8
        scored = self.puck_y<59 or self.puck_y>201
        if scored:
            if self.puck_y<59:
                self.puck_you += 1
            else:
                self.puck_cpu += 1
            if self.puck_you>=5 or self.puck_cpu>=5:
                self.puck_state = 'won' if self.puck_you>=5 else 'over'
                if self.puck_state=='won':
                    self.high_score('puck_won',1)
            self.puck_x,self.puck_y = 160.,128.
            self.puck_vx,self.puck_vy = 32.,(-65. if self.puck_you>=self.puck_cpu else 65.)
            self.puck_wait = time.ticks_add(time.ticks_ms(),700)
            self.game_draw()

    # ---- Paper plane ---------------------------------------------------
    def glider_new(self):
        self.glider_state = 'ready'
        self.glider_room = 0
        self.glider_lives = 3
        self.glider_reset()

    def glider_reset(self):
        self.glider_x,self.glider_y,self.glider_vy = 43.,115.,0.

    def glider_shelves(self):
        k = self.glider_room%3
        return ((116,88+k*5,55,6),(207,151-k*4,48,6))

    def glider_static(self):
        s = self.s
        s.rect(23,68,274,128,1)
        # A doorway, shelves, a picture and a floor fan make a small room.
        s.fill_rect(295,97,2,70,0)
        s.rect(53,76,27,20,1)
        s.line(55,94,76,78,1)
        for x,y,w,h in self.glider_shelves():
            s.fill_rect(x,y,w,h,1)
            s.vline(x+8,y+h,5,1)
        s.rect(87,184,25,10,1)
        for x in range(89,111,4):
            s.vline(x,186,6,1)
            for y in range(130,177,12):
                s.vline(x,y,4,1)
        self.button(19,202,84,'Pause' if self.glider_state=='running' else 'Start')
        self.button(117,202,84,'Lift')
        self.button(215,202,84,'New')

    def glider_actors(self):
        s = self.s
        s.fill_rect(24,50,272,14,0)
        self.centered('Room %d / 5   Lives %d' % (self.glider_room+1,self.glider_lives),24,50,272)
        x,y = int(self.glider_x),int(self.glider_y)
        s.line(x-9,y-4,x+10,y,1)
        s.line(x+10,y,x-7,y+5,1)
        s.line(x-7,y+5,x-3,y,1)
        s.line(x-3,y,x-9,y-4,1)
        s.line(x-3,y,x+10,y,1)

    def glider_step(self,dt):
        if self.glider_state!='running':
            return
        point = self.input_point if self.down else None
        accel = 48.
        if 85<self.glider_x<115 and self.glider_y>103:
            accel -= 115.
        if point and 117<=point[0]<201 and 202<=point[1]<225:
            accel -= 165.
        elif point and 24<=point[0]<296 and 69<=point[1]<194:
            self.glider_vy = max(-65.,min(65.,(point[1]-self.glider_y)*3))
            accel = 0.
        self.glider_vy = max(-80.,min(85.,self.glider_vy+accel*dt))
        self.glider_x += 33*dt
        self.glider_y += self.glider_vy*dt
        crash = self.glider_y<74 or self.glider_y>188
        for x,y,w,h in self.glider_shelves():
            if x-8<self.glider_x<x+w+9 and y-5<self.glider_y<y+h+5:
                crash = True
        if crash:
            self.glider_lives -= 1
            self.glider_state = 'over' if self.glider_lives<=0 else 'ready'
            self.glider_reset()
            self.game_draw()
        elif self.glider_x>285:
            if 97<self.glider_y<167:
                self.glider_room += 1
                self.high_score('glider_rooms',self.glider_room)
                self.glider_reset()
                if self.glider_room>=5:
                    self.glider_room = 4
                    self.glider_state = 'won'
                self.game_draw()
            else:
                self.glider_lives -= 1
                self.glider_state = 'over' if self.glider_lives<=0 else 'ready'
                self.glider_reset()
                self.game_draw()

    # ---- Three small castle rooms --------------------------------------
    def castle_new(self):
        self.castle_state = 'ready'
        self.castle_room = 0
        self.castle_lives = 3
        self.castle_score = 0
        self.castle_reset(True)

    def castle_reset(self,new_room=False):
        self.castle_x,self.castle_y,self.castle_vy = 43.,184.,0.
        self.castle_facing,self.castle_jumpdir = 1,0
        self.castle_grounded = True
        self.castle_rocks = []
        self.castle_shot_at = time.ticks_add(time.ticks_ms(),-1000)
        if new_room:
            self.castle_guard,self.castle_guard_x,self.castle_guard_v = True,220.,23.

    def castle_platforms(self):
        floor = ((24,125,184),(160,296,184)) if self.castle_room==1 else ((24,296,184),)
        return floor+((88,132,151),)

    def castle_static(self):
        s = self.s
        s.rect(23,70,274,126,1)
        for y in range(72,188,16):
            for x in range(25,294,22):
                s.pixel(x+(11 if y%32 else 0),y,1)
        for x1,x2,top in self.castle_platforms():
            s.fill_rect(x1,top,x2-x1,4,1)
        if self.castle_room==1:
            for x in range(128,158,7):
                s.line(x,195,x+3,190,1)
                s.line(x+3,190,x+6,195,1)
        s.rect(272,143,21,41,1)
        s.rect(277,149,11,35,1)
        s.rect(57,84,18,25,1)
        s.vline(66,84,25,1)
        s.hline(57,96,18,1)
        self.small_button(246,50,52,'New' if self.castle_state in ('won','over') else
                          ('Pause' if self.castle_state=='running' else 'Play'),18)
        for x,label in ((17,'Left'),(87,'Jump'),(157,'Right'),(227,'Throw')):
            self.button(x,202,66,label)

    def castle_actors(self):
        s = self.s
        s.fill_rect(24,50,216,15,0)
        s.text('Room %d/3 Lives %d' % (self.castle_room+1,self.castle_lives),27,54,1)
        x,y = int(self.castle_x),int(self.castle_y)
        s.rect(x-4,y-16,8,7,1)
        s.fill_rect(x-3,y-9,6,7,1)
        s.line(x-3,y-2,x-5,y,1)
        s.line(x+3,y-2,x+5,y,1)
        s.hline(x if self.castle_facing>0 else x-8,y-7,8,1)
        if self.castle_guard:
            gx = int(self.castle_guard_x)
            s.rect(gx-5,167,10,16,1)
            s.hline(gx-7,171,14,1)
            s.pixel(gx-2,170,1)
            s.pixel(gx+2,170,1)
        for rock in self.castle_rocks:
            s.fill_rect(int(rock[0])-2,int(rock[1])-2,4,4,1)

    def castle_shoot(self):
        now = time.ticks_ms()
        if time.ticks_diff(now,self.castle_shot_at)>=350 and len(self.castle_rocks)<3:
            self.castle_shot_at = now
            self.castle_rocks.append([self.castle_x+10*self.castle_facing,self.castle_y-9,
                                      170.*self.castle_facing,1.5])

    def castle_step(self,dt):
        if self.castle_state!='running':
            return
        direction = 0
        point = self.input_point if self.down else None
        if point and 202<=point[1]<225:
            if 17<=point[0]<83:
                direction = -1
            elif 157<=point[0]<223:
                direction = 1
        if direction:
            self.castle_facing = direction
        elif not self.castle_grounded:
            direction = self.castle_jumpdir
        self.castle_x = max(29.,min(292.,self.castle_x+direction*70*dt))
        old_y = self.castle_y
        self.castle_vy += 390*dt
        self.castle_y += self.castle_vy*dt
        self.castle_grounded = False
        if self.castle_vy>=0:
            for x1,x2,top in self.castle_platforms():
                if x1-4<=self.castle_x<=x2+4 and old_y<=top+1 and self.castle_y>=top:
                    self.castle_y,self.castle_vy = float(top),0.
                    self.castle_grounded = True
                    self.castle_jumpdir = 0
                    break
        if self.castle_guard:
            self.castle_guard_x += self.castle_guard_v*dt
            if self.castle_guard_x>252 or self.castle_guard_x<187:
                self.castle_guard_v = -self.castle_guard_v
        remaining = []
        for rock in self.castle_rocks:
            rock[0] += rock[2]*dt
            rock[3] -= dt
            if self.castle_guard and abs(rock[0]-self.castle_guard_x)<12 and abs(rock[1]-175)<14:
                self.castle_guard = False
                self.castle_score += 10
            elif rock[3]>0 and 25<rock[0]<295:
                remaining.append(rock)
        self.castle_rocks = remaining
        hit = self.castle_guard and abs(self.castle_x-self.castle_guard_x)<12 and abs(self.castle_y-184)<15
        if self.castle_y>205 or hit:
            self.castle_lives -= 1
            self.castle_state = 'over' if self.castle_lives<=0 else 'ready'
            self.castle_reset()
            self.game_draw()
        elif self.castle_x>283 and self.castle_y>=160:
            self.castle_room += 1
            self.high_score('castle_rooms',self.castle_room)
            if self.castle_room>=3:
                self.castle_room = 2
                self.castle_state = 'won'
            self.castle_reset(True)
            self.game_draw()

    # ---- Input and animation dispatch ---------------------------------
    def game_click(self,x,y):
        self.game_last = time.ticks_ms()
        if self.app=='Puck':
            if 202<=y<225:
                if x<105:
                    if self.puck_state in ('won','over'):
                        self.puck_new()
                    self.puck_state = 'running'
                elif x<205:
                    if self.puck_state not in ('won','over'):
                        self.puck_state = 'paused' if self.puck_state=='running' else 'running'
                else:
                    self.puck_new()
                self.game_draw()
            elif 65<=y<196:
                self.puck_player = float(max(48,min(272,x)))
                if self.puck_state in ('ready','paused'):
                    self.puck_state = 'running'
                    self.game_draw()
        elif self.app=='Glider':
            if 202<=y<225:
                if x<105:
                    if self.glider_state in ('won','over'):
                        self.glider_new()
                    self.glider_state = 'paused' if self.glider_state=='running' else 'running'
                elif x<205:
                    if self.glider_state in ('ready','paused'):
                        self.glider_state = 'running'
                else:
                    self.glider_new()
                self.game_draw()
            elif 69<=y<195 and self.glider_state in ('ready','paused'):
                self.glider_state = 'running'
                self.game_draw()
        else:
            if 246<=x<298 and 50<=y<68:
                if self.castle_state in ('won','over'):
                    self.castle_new()
                else:
                    self.castle_state = 'paused' if self.castle_state=='running' else 'running'
                self.game_draw()
            elif 202<=y<225:
                if self.castle_state in ('ready','paused'):
                    self.castle_state = 'running'
                    self.game_draw()
                if self.castle_state=='running':
                    if 87<=x<153 and self.castle_grounded:
                        self.castle_vy = -155.
                        self.castle_grounded = False
                        self.castle_jumpdir = self.castle_facing
                    elif 227<=x<293:
                        self.castle_shoot()
            elif 70<=y<196 and self.castle_state in ('ready','paused'):
                self.castle_state = 'running'
                self.game_draw()

    def click(self,x,y):
        if y<22 or (self.app!='Desktop' and 12<=x<=42 and 26<=y<=48):
            return super().click(x,y)
        if self.app=='Desktop':
            if 219<=y<240:
                if x<79:
                    self.desk_page = max(0,self.desk_page-1)
                elif x>=241:
                    self.desk_page = min(1,self.desk_page+1)
                self.desktop()
                return
            for i,name in enumerate(self.tools[self.desk_page*12:self.desk_page*12+12]):
                xx,yy = 8+(i%4)*79,36+(i//4)*59
                if xx<=x<xx+73 and yy<=y<yy+55:
                    self.open(name)
                    return
        elif self.app=='Notes':
            self.notes_click(x,y)
        elif self.app in GAMES:
            self.game_click(x,y)
        else:
            super().click(x,y)

    def draw_point(self,point):
        if self.app in GAMES:
            self.input_point = point
            if self.app=='Puck' and 65<=point[1]<197:
                self.puck_player = float(max(48,min(272,point[0])))
        elif self.app!='Notes':
            super().draw_point(point)

    def tick(self):
        super().tick()
        if self.app not in GAMES or self.state()!='running':
            return
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now,self.game_last)
        if elapsed<40:
            return
        self.game_last = now
        dt = min(.06,elapsed/1000)
        if self.app=='Puck':
            old = self.puck_rects
            old_score = (self.puck_you,self.puck_cpu)
            self.puck_step(dt)
            if self.puck_state!='running':
                return
            self.game_restore()
            self.puck_actors()
            new = self.puck_rectangles()
            for a,b in zip(old,new):
                self.dirty_pair(a,b)
            self.puck_rects = new
            if old_score!=(self.puck_you,self.puck_cpu):
                self.s.show_rect(24,50,272,14)
        elif self.app=='Glider':
            old = (int(self.glider_x)-12,int(self.glider_y)-7,25,15)
            self.glider_step(dt)
            if self.glider_state!='running':
                return
            self.game_restore()
            self.glider_actors()
            self.dirty_pair(old,(int(self.glider_x)-12,int(self.glider_y)-7,25,15))
        else:
            self.castle_step(dt)
            if self.castle_state!='running':
                return
            self.game_restore()
            self.castle_actors()
            # Player, guard and projectiles occupy a narrow lower strip.
            self.s.show_rect(24,98,272,99)


def run():
    ExtrasDesktop().run()
