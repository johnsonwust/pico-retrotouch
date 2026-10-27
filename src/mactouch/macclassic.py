# SPDX-License-Identifier: MIT
"""MacTouch Classic: original MicroPython miniatures inspired by early Macs."""
import gc
import os
import time
import random
import framebuf
import micropython
from mactouch import Desktop
from macstorage import Storage

VERSION = '0.3.0'
CW, CH, CX, CY = 224, 128, 74, 60
MAP_X, MAP_Y, MAP_W, MAP_H = 16, 168, 56, 32


@micropython.viper
def make_thumbnail(src, dst):
    source = ptr8(src)
    target = ptr8(dst)
    for i in range(224):
        target[i] = 0
    for y in range(32):
        for x in range(56):
            offset = y * 112 + (x >> 1)
            bits = source[offset] | source[offset+28] | source[offset+56] | source[offset+84]
            mask = 15
            if (x & 1) == 0:
                mask = 240
            if bits & mask:
                target[y*7+(x >> 3)] |= 128 >> (x & 7)


class ClassicDesktop(Desktop):
    def __init__(self):
        super().__init__()
        self.tools = ['Boot', 'Paint', 'Gallery', 'Maze', 'Cards', 'Puzzle',
                      'Pet', 'Timer', 'Icons', 'About']
        self.store = Storage(self.s)
        self.canvas_data = bytearray(CW * CH // 8)
        self.canvas = framebuf.FrameBuffer(self.canvas_data, CW, CH, framebuf.MONO_HLSB)
        self.undo_data = bytearray(len(self.canvas_data))
        self.undo_valid = False
        self.paint_tool = 'Pen'
        self.paint_size = 1
        self.paint_pattern = 0
        self.paint_zoom = False
        self.paint_pan = False
        self.paint_drag = None
        self.paint_pan_anchor = None
        self.thumbnail_data = bytearray(224)
        self.thumbnail = framebuf.FrameBuffer(self.thumbnail_data, MAP_W, MAP_H, framebuf.MONO_HLSB)
        self.zoom_x, self.zoom_y = 84, 48
        self.paint_focus = (112, 64)
        self.stroke_started = False
        self.paint_message = 'A little room for a big idea.'
        self.gallery_page = 0
        self.gallery_names = []
        self.picture_name = ''
        self.maze = None
        self.maze_hard = False
        self.maze_won = False
        self.maze_hint_until = None
        self.card_data = None
        self.card_index = 0
        self.story = {'key': False, 'floppy': False}
        self.card_notice = ''
        self.story_enabled = True
        self.puzzle_n = 4
        self.puzzle_done = False
        self.puzzle_started = time.ticks_ms()
        self.records = None

    def records_load(self):
        if self.records is None:
            try:
                self.records = self.store.read_json('records.json', {})
            except (OSError, ValueError):
                self.records = {}
        return self.records

    def record(self, name, moves):
        records = self.records_load()
        if moves < records.get(name, 100000):
            records[name] = moves
            try:
                self.store.write_json('records.json', records)
            except OSError as exc:
                print('RECORD_SAVE_ERROR', exc)

    def happy(self, x=124, y=52, scale=1):
        # Original terminal graphic for the public-source edition.
        s=self.s
        s.rect(x,y,72,62,1);s.hline(x,y+10,72,1)
        s.line(x+15,y+23,x+25,y+31,1)
        s.line(x+25,y+31,x+15,y+39,1)
        s.hline(x+33,y+40,20,1)

    def boot(self, pause=True):
        self.s.fill(0)
        self.happy()
        self.centered('Welcome to MacTouch', 0, 152, 320)
        self.centered('Classic little things / ' + VERSION, 0, 213, 320)
        self.s.rect(72, 179, 176, 12, 1)
        self.s.fill_rect(75, 182, 38, 6, 1)
        self.s.show()
        if pause:
            time.sleep_ms(250)
        try:
            self.store.ensure()
            label = self.store.medium + ' storage ready'
        except OSError:
            label = 'Desktop ready'
        self.s.fill_rect(75, 182, 170, 6, 1)
        self.centered(label, 0, 195, 320)
        self.s.show_rect(20, 176, 280, 35)
        print('CLASSIC_BOOT', VERSION, label)
        if pause:
            time.sleep_ms(650)

    def icon(self, kind, x, y):
        s = self.s
        if kind == 'Boot':
            s.rect(x+5, y, 26, 29, 1)
            s.rect(x+8, y+3, 20, 16, 1)
            s.pixel(x+13, y+8, 1)
            s.pixel(x+23, y+8, 1)
            s.hline(x+14, y+13, 9, 1)
            s.hline(x+18, y+23, 9, 1)
        elif kind == 'Gallery':
            s.rect(x, y+4, 29, 23, 1)
            s.rect(x+5, y, 30, 23, 1)
            s.line(x+9, y+18, x+17, y+9, 1)
            s.line(x+17, y+9, x+26, y+18, 1)
            s.ellipse(x+27, y+6, 2, 2, 1)
        elif kind == 'Maze':
            s.rect(x+2, y, 30, 30, 1)
            for xx, yy, ww, hh in ((8, 0, 1, 19), (14, 7, 1, 23), (21, 0, 1, 16),
                                   (21, 22, 11, 1), (27, 7, 1, 16)):
                s.fill_rect(x+xx, y+yy, ww, hh, 1)
        elif kind == 'Cards':
            for offset in (6, 3, 0):
                s.fill_rect(x+offset, y+offset, 29, 24, 0)
                s.rect(x+offset, y+offset, 29, 24, 1)
            s.hline(x+4, y+6, 20, 1)
            s.rect(x+4, y+12, 9, 7, 1)
        elif kind == 'Puzzle':
            for row in range(4):
                for col in range(4):
                    if row != 3 or col != 3:
                        s.rect(x+col*8, y+row*8, 7, 7, 1)
        else:
            super().icon(kind, x, y)

    def desktop(self):
        self.app = 'Desktop'
        self.previous = None
        self.stroke_started = False
        self.background()
        for i, name in enumerate(self.tools):
            x, y = 8+(i%4)*79, 39+(i//4)*59
            self.s.fill_rect(x, y-3, 73, 55, 0)
            self.icon(name, x+18, y)
            self.centered(name, x, y+35, 73)
        self.s.fill_rect(0, 220, 320, 20, 0)
        self.centered('Classic ' + VERSION + '  /  Tap to explore', 0, 224, 320)
        self.s.show()

    def open(self, app):
        if app == 'Boot':
            self.boot()
            self.desktop()
            return
        if app not in ('Paint', 'Gallery', 'Picture', 'Maze', 'Cards', 'Puzzle', 'About'):
            return super().open(app)
        print('OPEN', app)
        self.app = app
        self.previous = None
        self.stroke_started = False
        self.window(app)
        if app == 'Paint':
            self.paint_draw()
        elif app == 'Gallery':
            self.gallery_draw()
        elif app == 'Picture':
            self.picture_draw()
        elif app == 'Maze':
            if self.maze is None:
                self.maze_new()
            self.maze_draw()
        elif app == 'Cards':
            self.cards_load()
            self.card_draw()
        elif app == 'Puzzle':
            if len(self.tiles) != self.puzzle_n**2:
                self.shuffle()
            self.puzzle_draw()
        elif app == 'About':
            gc.collect()
            for i, text in enumerate(('MacTouch Classic ' + VERSION,
                                      'Original little apps, inspired by 1984.',
                                      'Storage: ' + self.store.medium,
                                      'Free RAM: %d KB' % (gc.mem_free()//1024),
                                      'Desk: home. Box: close window.')):
                self.text(text, 21, 59+i*23)
            self.button(22, 185, 125, 'Calibrate')
            self.button(161, 185, 132, 'Touch test')
        self.s.show()

    def checkpoint(self):
        self.undo_data[:] = self.canvas_data
        self.undo_valid = True

    def paint_draw(self):
        s = self.s
        s.fill_rect(15, 52, 58, 150, 0)
        if self.paint_zoom:
            for label, yy in (('Pen', 53), ('Rub', 75), ('Fill', 97), ('Move', 119), ('1x', 141)):
                selected = self.paint_pan if label == 'Move' else (not self.paint_pan and label == self.paint_tool)
                s.rect(16, yy, 49, 20, 1)
                if selected:
                    s.rect(18, yy+2, 45, 16, 1)
                self.centered(label, 16, yy+3, 49)
            self.paint_navigator()
        else:
            for label, yy in (('Pen', 57), ('Rub', 87), ('Fill', 117), ('Zoom', 147)):
                self.button(16, yy, 49, label, label == self.paint_tool)
            self.button(16, 177, 49, str(self.paint_size) + ' px')
        s.rect(CX-1, CY-1, CW+2, CH+2, 1)
        self.paint_render()
        self.paint_status(self.paint_message, False)
        self.button(17, 202, 47, 'New')
        self.button(69, 202, 51, 'Undo')
        self.button(125, 202, 79, ('Solid', 'Check', 'Dots')[self.paint_pattern])
        self.button(210, 202, 88, 'Save ' + self.store.medium)

    def paint_status(self, message, show=True):
        self.paint_message = message
        self.s.fill_rect(73, 189, 228, 12, 0)
        # Compact status text uses the built-in font to fit long filenames.
        if self.paint_zoom:
            message = '4x %03d,%03d %s' % (self.zoom_x, self.zoom_y,
                       'Drag to move' if self.paint_pan else self.paint_tool + ' / tap map')
        self.s.text(message[:28], 74, 191, 1)
        if show:
            self.s.show_rect(73, 189, 228, 12)

    def paint_render(self):
        if not self.paint_zoom:
            self.s.blit(self.canvas, CX, CY)
        else:
            for yy in range(32):
                for xx in range(56):
                    self.s.fill_rect(CX+xx*4, CY+yy*4, 4, 4,
                                     self.canvas.pixel(self.zoom_x+xx, self.zoom_y+yy))

    def paint_map(self, x, y):
        if not CX <= x < CX+CW or not CY <= y < CY+CH:
            return None
        if self.paint_zoom:
            return self.zoom_x+(x-CX)//4, self.zoom_y+(y-CY)//4
        return x-CX, y-CY

    def paint_navigator(self):
        make_thumbnail(self.canvas_data, self.thumbnail_data)
        self.s.blit(self.thumbnail, MAP_X, MAP_Y)
        vx, vy = MAP_X+self.zoom_x//4, MAP_Y+self.zoom_y//4
        self.s.rect(vx-1, vy-1, 16, 10, 0)
        self.s.rect(vx, vy, 14, 8, 1)
        self.s.rect(MAP_X-1, MAP_Y-1, MAP_W+2, MAP_H+2, 1)

    def paint_set_view(self, x, y):
        x, y = max(0, min(CW-56, int(x))), max(0, min(CH-32, int(y)))
        if (x, y) == (self.zoom_x, self.zoom_y):
            return
        self.zoom_x, self.zoom_y = x, y
        self.paint_focus = (x+28, y+16)
        self.paint_render()
        self.paint_navigator()
        self.paint_status(self.paint_message)
        self.s.show_rect(CX, CY, CW, CH)
        self.s.show_rect(MAP_X-1, MAP_Y-1, MAP_W+2, MAP_H+2)

    def paint_map_drag(self, x, y):
        self.paint_set_view((x-MAP_X)*4-28, (y-MAP_Y)*4-16)

    def paint_fill(self, x, y):
        self.checkpoint()
        target = self.canvas.pixel(x, y)
        visited_data = bytearray(len(self.canvas_data))
        seen = framebuf.FrameBuffer(visited_data, CW, CH, framebuf.MONO_HLSB)
        pending = [(x, y)]
        while pending:
            x, y = pending.pop()
            if seen.pixel(x, y) or self.canvas.pixel(x, y) != target:
                continue
            left = x
            while left > 0 and not seen.pixel(left-1, y) and self.canvas.pixel(left-1, y) == target:
                left -= 1
            right = x
            while right+1 < CW and not seen.pixel(right+1, y) and self.canvas.pixel(right+1, y) == target:
                right += 1
            for xx in range(left, right+1):
                seen.pixel(xx, y, 1)
                value = 1-target
                if target == 0 and self.paint_pattern:
                    value = ((xx+y) % 2 == 0) if self.paint_pattern == 1 else (xx%3 == 0 and y%3 == 0)
                self.canvas.pixel(xx, y, int(value))
            for yy in (y-1, y+1):
                if not 0 <= yy < CH:
                    continue
                in_run = False
                for xx in range(left, right+1):
                    valid = not seen.pixel(xx, yy) and self.canvas.pixel(xx, yy) == target
                    if valid and not in_run:
                        pending.append((xx, yy))
                    in_run = valid
        self.paint_render()
        self.s.show_rect(CX, CY, CW, CH)
        if self.paint_zoom:
            self.paint_navigator()
            self.s.show_rect(MAP_X-1, MAP_Y-1, MAP_W+2, MAP_H+2)

    def paint_click(self, x, y):
        self.stroke_started = False
        self.paint_drag = None
        self.paint_pan_anchor = None
        if self.paint_zoom and MAP_X-1 <= x <= MAP_X+MAP_W and MAP_Y-1 <= y <= MAP_Y+MAP_H:
            self.paint_drag = 'map'
            self.paint_map_drag(x, y)
            return
        if self.paint_zoom and 16 <= x < 65:
            for label, yy in (('Pen', 53), ('Rub', 75), ('Fill', 97), ('Move', 119), ('1x', 141)):
                if yy <= y < yy+20:
                    self.previous = None
                    if label == '1x':
                        self.paint_zoom = False
                        self.paint_pan = False
                    elif label == 'Move':
                        self.paint_pan = True
                    else:
                        self.paint_pan = False
                        self.paint_tool = label
                    self.paint_draw()
                    self.s.show_rect(15, 52, 285, 174)
                    return
        elif 16 <= x < 65:
            for label, yy in (('Pen', 57), ('Rub', 87), ('Fill', 117), ('Zoom', 147)):
                if yy <= y < yy+23:
                    if label == 'Zoom':
                        if not self.paint_zoom:
                            self.zoom_x = max(0, min(CW-56, self.paint_focus[0]-28))
                            self.zoom_y = max(0, min(CH-32, self.paint_focus[1]-16))
                            self.paint_pan = True
                        self.paint_zoom = not self.paint_zoom
                    else:
                        self.paint_tool = label
                    self.paint_draw()
                    self.s.show_rect(15, 52, 285, 174)
                    return
            if 177 <= y < 200:
                self.paint_size = {1: 3, 3: 5, 5: 1}[self.paint_size]
                self.paint_draw()
                self.s.show_rect(15, 56, 285, 169)
        elif 202 <= y < 225:
            if 17 <= x < 64:
                self.checkpoint()
                self.canvas.fill(0)
            elif 69 <= x < 120:
                if self.undo_valid:
                    old = bytes(self.canvas_data)
                    self.canvas_data[:] = self.undo_data
                    self.undo_data[:] = old
            elif 125 <= x < 204:
                self.paint_pattern = (self.paint_pattern+1) % 3
            elif 210 <= x < 298:
                try:
                    name = self.store.save_picture(self.canvas_data)
                    self.paint_message = self.store.medium + ': ' + name
                except OSError as exc:
                    print('PAINT_SAVE_ERROR', exc)
                    self.paint_message = 'Save failed. Check card.'
            self.paint_draw()
            self.s.show_rect(15, 56, 285, 169)
        else:
            point = self.paint_map(x, y)
            if point and self.paint_zoom and self.paint_pan:
                self.paint_pan_anchor = (x, y, self.zoom_x, self.zoom_y)
            elif point and self.paint_tool == 'Fill':
                self.paint_focus = point
                self.paint_fill(*point)

    def gallery_draw(self):
        self.s.fill_rect(16, 52, 288, 147, 0)
        try:
            self.gallery_names = self.store.pictures()
            self.gallery_page = min(self.gallery_page, max(0, (len(self.gallery_names)-1)//5))
            self.text('%s album / %d pictures' % (self.store.medium, len(self.gallery_names)), 23, 56)
            if not self.gallery_names:
                self.text('Save your first picture in Paint.', 23, 98)
            for i, name in enumerate(self.gallery_names[self.gallery_page*5:self.gallery_page*5+5]):
                yy = 77+i*23
                self.s.rect(22, yy, 275, 22, 1)
                self.text(name, 33, yy+4)
        except OSError as exc:
            print('GALLERY_ERROR', exc)
            self.text('Card unavailable. Try restarting.', 21, 98)
        self.button(19, 202, 84, 'Prev')
        self.button(117, 202, 84, 'Next')
        self.button(215, 202, 84, 'Paint')

    def picture_draw(self):
        self.centered(self.picture_name, 16, 51, 286)
        try:
            data = self.store.load_picture(self.picture_name)
            view = framebuf.FrameBuffer(bytearray(data), CW, CH, framebuf.MONO_HLSB)
            self.s.blit(view, 48, 68)
            self.s.rect(47, 67, CW+2, CH+2, 1)
            self.button(43, 202, 106, 'Edit')
            self.button(171, 202, 106, 'Album')
        except (OSError, ValueError) as exc:
            print('PICTURE_ERROR', exc)
            self.text('Could not open this picture.', 25, 104)
            self.button(171, 202, 106, 'Album')

    def maze_new(self):
        self.mw, self.mh, self.mc = (15, 9, 16) if self.maze_hard else (11, 7, 20)
        self.mx, self.my = (320-self.mw*self.mc)//2, 53
        count = self.mw*self.mh
        self.maze = bytearray([15]*count)
        visited = bytearray(count)
        visited[0] = 1
        stack = [0]
        while stack:
            cell = stack[-1]
            x, y = cell%self.mw, cell//self.mw
            choices = []
            for dx, dy, wall, opposite in ((0,-1,1,4), (1,0,2,8), (0,1,4,1), (-1,0,8,2)):
                xx, yy = x+dx, y+dy
                if 0 <= xx < self.mw and 0 <= yy < self.mh:
                    nxt = yy*self.mw+xx
                    if not visited[nxt]:
                        choices.append((nxt, wall, opposite))
            if not choices:
                stack.pop()
                continue
            nxt, wall, opposite = random.choice(choices)
            self.maze[cell] &= 15 ^ wall
            self.maze[nxt] &= 15 ^ opposite
            visited[nxt] = 1
            stack.append(nxt)
        self.maze_player = 0
        self.maze_trail = bytearray(count)
        self.maze_trail[0] = 1
        self.maze_moves = 0
        self.maze_won = False
        self.maze_assisted = False
        self.maze_hint_until = None
        self.maze_path = []

    def maze_solution(self):
        goal = len(self.maze)-1
        queue = [self.maze_player]
        parent = {self.maze_player: None}
        for cell in queue:
            if cell == goal:
                break
            for delta, wall in ((-self.mw, 1), (1, 2), (self.mw, 4), (-1, 8)):
                nxt = cell+delta
                if not self.maze[cell] & wall and nxt not in parent:
                    parent[nxt] = cell
                    queue.append(nxt)
        path = [goal]
        while path[-1] != self.maze_player:
            path.append(parent[path[-1]])
        path.reverse()
        return path

    def maze_draw(self):
        s = self.s
        s.fill_rect(16, 50, 288, 150, 0)
        for i, walls in enumerate(self.maze):
            x, y = self.mx+(i%self.mw)*self.mc, self.my+(i//self.mw)*self.mc
            if self.maze_trail[i]:
                s.fill_rect(x+self.mc//2, y+self.mc//2, 2, 2, 1)
            if walls & 1:
                s.hline(x, y, self.mc+1, 1)
            if walls & 2:
                s.vline(x+self.mc, y, self.mc+1, 1)
            if walls & 4:
                s.hline(x, y+self.mc, self.mc+1, 1)
            if walls & 8:
                s.vline(x, y, self.mc+1, 1)
        if self.maze_hint_until is not None:
            for i in self.maze_path:
                x, y = self.mx+(i%self.mw)*self.mc, self.my+(i//self.mw)*self.mc
                s.ellipse(x+self.mc//2, y+self.mc//2, 3, 3, 1)
        gx, gy = self.mx+(self.mw-1)*self.mc, self.my+(self.mh-1)*self.mc
        s.rect(gx+4, gy+4, self.mc-7, self.mc-7, 1)
        self.maze_player_draw()
        self.button(19, 202, 84, 'New')
        self.button(117, 202, 84, 'Hint')
        self.button(215, 202, 84, 'Easy' if self.maze_hard else 'Hard')
        if self.maze_won:
            s.fill_rect(66, 91, 188, 73, 0)
            s.rect(66, 91, 188, 73, 1)
            self.centered('You escaped!', 66, 103, 188)
            self.centered('%d moves' % self.maze_moves, 66, 125, 188)
            self.centered('Tap New to play again', 66, 144, 188)

    def maze_player_draw(self):
        x = self.mx+(self.maze_player%self.mw)*self.mc+self.mc//2
        y = self.my+(self.maze_player//self.mw)*self.mc+self.mc//2
        self.s.fill_rect(x-4, y-4, 8, 8, 1)
        self.s.fill_rect(x-2, y-2, 2, 2, 0)

    def maze_move(self, x, y):
        if self.maze_won:
            return
        tx, ty = (x-self.mx)//self.mc, (y-self.my)//self.mc
        if not 0 <= tx < self.mw or not 0 <= ty < self.mh:
            return
        current = self.maze_player
        px, py = current%self.mw, current//self.mw
        dx, dy = tx-px, ty-py
        if abs(dx)+abs(dy) != 1:
            return
        wall = 2 if dx == 1 else 8 if dx == -1 else 4 if dy == 1 else 1
        if self.maze[current] & wall:
            return
        self.maze_player = ty*self.mw+tx
        self.maze_moves += 1
        self.maze_trail[self.maze_player] = 1
        old_x = self.mx+px*self.mc+self.mc//2
        old_y = self.my+py*self.mc+self.mc//2
        self.s.fill_rect(old_x-4, old_y-4, 8, 8, 0)
        self.s.fill_rect(old_x, old_y, 2, 2, 1)
        self.maze_player_draw()
        if self.maze_player == len(self.maze)-1:
            self.maze_won = True
            if not self.maze_assisted:
                self.record('maze_hard' if self.maze_hard else 'maze_easy', self.maze_moves)
            self.maze_draw()
            self.s.show_rect(16, 50, 288, 150)
        else:
            xx = self.mx+min(px, tx)*self.mc+3
            yy = self.my+min(py, ty)*self.mc+3
            self.s.show_rect(xx, yy, (abs(dx)+1)*self.mc-5, (abs(dy)+1)*self.mc-5)

    def cards_load(self):
        if self.card_data is not None:
            return
        from classic_cards import CARDS
        self.card_data = CARDS
        try:
            data = self.store.read_json('cards.json', None)
            if data is None:
                self.store.write_json('cards.json', CARDS)
            else:
                assert isinstance(data, list) and 0 < len(data) <= 32
                for card in data:
                    assert isinstance(card['title'], str) and len(card['title']) <= 40
                    assert len(card['body']) <= 3 and len(card['buttons']) <= 3
                    for line in card['body']:
                        assert isinstance(line, str) and len(line) <= 48
                    for label, target in card['buttons']:
                        assert isinstance(label, str) and len(label) <= 12
                        assert ((isinstance(target, int) and 0 <= target < len(data)) or
                                target in ('app:Paint', 'app:Gallery', 'app:Maze', 'app:Puzzle'))
                self.card_data = data
            saved = self.store.read_json('story.json', self.story)
            if isinstance(saved, dict):
                self.story = {'key': bool(saved.get('key')), 'floppy': bool(saved.get('floppy'))}
            self.story_enabled = self.card_data == CARDS
        except (OSError, ValueError, AssertionError, KeyError, TypeError) as exc:
            print('CARDS_LOAD_ERROR', exc)
            self.card_notice = 'Using the built-in story.'

    def card_art(self, art):
        s = self.s
        s.rect(28, 55, 264, 72, 1)
        if art in ('room', 'desk'):
            s.hline(46, 106, 226, 1)
            s.vline(58, 106, 18, 1)
            s.vline(262, 106, 18, 1)
            s.rect(73, 64, 49, 37, 1)
            s.rect(78, 69, 39, 23, 1)
            s.hline(88, 99, 20, 1)
            s.rect(199, 109, 51, 14, 1)
            s.rect(219, 113, 10, 4, 1)
            if self.story['floppy']:
                s.fill_rect(210, 111, 28, 9, 0)
        elif art == 'books':
            for i in range(10):
                x, hh = 45+i*20, 29+(i%3)*8
                s.rect(x, 103-hh, 15, hh, 1)
                s.hline(x+2, 108-hh, 10, 1)
            s.hline(38, 104, 242, 1)
            if not self.story['key']:
                s.ellipse(224, 115, 4, 4, 1)
                s.hline(228, 115, 15, 1)
                s.vline(240, 115, 4, 1)
        elif art == 'studio':
            self.icon('Paint', 69, 70)
            self.icon('Pet', 154, 70)
            self.icon('Gallery', 230, 70)
        elif art == 'window':
            s.rect(100, 61, 120, 59, 1)
            s.vline(160, 61, 59, 1)
            s.hline(100, 90, 120, 1)
            for xx, yy in ((117,75),(176,70),(199,104),(134,111)):
                s.hline(xx-3, yy, 7, 1)
                s.vline(xx, yy-3, 7, 1)
        else:
            s.rect(133, 61, 54, 59, 1)
            s.rect(144, 61, 31, 22, 1)
            s.rect(143, 96, 34, 24, 1)
            s.fill_rect(165, 65, 5, 14, 1)

    def card_draw(self):
        self.window('Cards')
        self.card_index = min(self.card_index, len(self.card_data)-1)
        card = self.card_data[self.card_index]
        self.card_art(card.get('art', 'floppy'))
        self.centered(card['title'], 20, 132, 280)
        body = card['body']
        if self.story_enabled and self.card_index == 1 and self.story['key'] and not self.story['floppy']:
            body = ['The brass key fits the drawer!', 'Tap its handle in the picture.', 'Your floppy might be inside.']
        for i, line in enumerate(body):
            self.s.text(line[:34], 24, 153+i*11, 1)
        notice = self.card_notice or ('Inventory: floppy + key' if self.story['floppy'] else
                                     'Inventory: brass key' if self.story['key'] else 'Tap pictures to find hidden things.')
        self.s.text(notice[:35], 20, 190, 1)
        for i, item in enumerate(card['buttons']):
            self.button(19+i*98, 202, 86, item[0])

    def card_click(self, x, y):
        self.card_notice = ''
        changed = False
        if self.story_enabled and 55 <= y < 127:
            if self.card_index == 2 and 209 <= x <= 256 and y >= 105:
                self.story['key'] = True
                self.card_notice = 'You found a brass key!'
                changed = True
            elif self.card_index == 1 and 195 <= x <= 257 and y >= 105:
                if self.story['key']:
                    self.story['floppy'] = True
                    self.card_index = min(5, len(self.card_data)-1)
                    changed = True
                else:
                    self.card_notice = 'Locked. Look in the library.'
        elif 202 <= y < 225:
            card = self.card_data[self.card_index]
            for i, (label, target) in enumerate(card['buttons']):
                if 19+i*98 <= x < 105+i*98:
                    if isinstance(target, str):
                        self.open(target[4:])
                        return
                    self.card_index = target
                    break
        if changed:
            try:
                self.store.write_json('story.json', self.story)
            except OSError:
                self.card_notice = 'Progress not saved. Check card.'
        self.card_draw()
        self.s.show_rect(8, 26, 302, 202)

    def shuffle(self):
        n = self.puzzle_n
        self.tiles = list(range(1, n*n)) + [0]
        previous = -1
        for _ in range(120):
            blank = self.tiles.index(0)
            choices = [i for i in range(n*n) if abs(i//n-blank//n)+abs(i%n-blank%n)==1 and i != previous]
            move = random.choice(choices)
            self.tiles[blank], self.tiles[move] = self.tiles[move], self.tiles[blank]
            previous = blank
        if self.tiles == list(range(1, n*n)) + [0]:
            self.tiles[-1], self.tiles[-2] = self.tiles[-2], self.tiles[-1]
        self.moves = 0
        self.puzzle_done = False
        self.puzzle_started = time.ticks_ms()

    def puzzle_draw(self):
        n = self.puzzle_n
        step = 34 if n == 4 else 44
        self.s.fill_rect(16, 53, 286, 147, 0)
        self.text('Moves', 19, 76)
        self.text(str(self.moves), 32, 98)
        self.text('%d x %d' % (n, n), 19, 141)
        for i, value in enumerate(self.tiles):
            x, y = 94+(i%n)*step, 57+(i//n)*step
            self.s.rect(x, y, step-2, step-2, 1)
            if value:
                self.centered(str(value), x, y+(step-15)//2, step-2)
        best = self.records_load().get('puzzle_%d' % n)
        self.text('Best', 245, 76)
        self.text(str(best) if best is not None else '--', 253, 98)
        if self.puzzle_done:
            self.text('Solved!', 240, 141)
        self.button(79, 202, 90, 'Shuffle')
        self.button(184, 202, 100, '3 x 3' if n == 4 else '4 x 4')

    def click(self, x, y):
        if y < 22 or (self.app != 'Desktop' and 12 <= x <= 42 and 26 <= y <= 48):
            return super().click(x, y)
        if self.app == 'Desktop':
            for i, name in enumerate(self.tools):
                xx, yy = 8+(i%4)*79, 36+(i//4)*59
                if xx <= x < xx+73 and yy <= y < yy+55:
                    self.open(name)
                    return
        elif self.app == 'Paint':
            self.paint_click(x, y)
        elif self.app == 'Gallery':
            if 77 <= y < 192 and 22 <= x < 297:
                index = self.gallery_page*5+(y-77)//23
                if index < len(self.gallery_names):
                    self.picture_name = self.gallery_names[index]
                    self.open('Picture')
            elif 202 <= y < 225:
                if x < 105:
                    self.gallery_page = max(0, self.gallery_page-1)
                elif x < 205:
                    self.gallery_page = min(max(0, (len(self.gallery_names)-1)//5), self.gallery_page+1)
                else:
                    return self.open('Paint')
                self.gallery_draw()
                self.s.show_rect(16, 52, 288, 175)
        elif self.app == 'Picture':
            if 202 <= y < 225:
                if 43 <= x < 149:
                    try:
                        data = self.store.load_picture(self.picture_name)
                        self.checkpoint()
                        self.canvas_data[:] = data
                        self.paint_zoom = False
                        self.paint_pan = False
                        self.paint_message = 'Opened ' + self.picture_name
                        self.open('Paint')
                    except (OSError, ValueError) as exc:
                        print('EDIT_LOAD_ERROR', exc)
                elif 171 <= x < 277:
                    self.open('Gallery')
        elif self.app == 'Maze':
            if 202 <= y < 225:
                if 19 <= x < 103:
                    self.maze_new()
                elif 117 <= x < 201:
                    self.maze_path = self.maze_solution()
                    self.maze_hint_until = time.ticks_add(time.ticks_ms(), 3000)
                    self.maze_assisted = True
                elif 215 <= x < 299:
                    self.maze_hard = not self.maze_hard
                    self.maze_new()
                self.maze_draw()
                self.s.show_rect(16, 50, 288, 177)
            else:
                self.maze_move(x, y)
        elif self.app == 'Cards':
            self.card_click(x, y)
        elif self.app == 'Puzzle':
            n, step = self.puzzle_n, 34 if self.puzzle_n == 4 else 44
            if 202 <= y < 225:
                if 79 <= x < 169:
                    self.shuffle()
                elif 184 <= x < 284:
                    self.puzzle_n = 3 if n == 4 else 4
                    self.shuffle()
            elif not self.puzzle_done and 94 <= x < 94+n*step and 57 <= y < 57+n*step:
                i = ((y-57)//step)*n+(x-94)//step
                blank = self.tiles.index(0)
                if abs(i//n-blank//n)+abs(i%n-blank%n)==1:
                    self.tiles[i], self.tiles[blank] = self.tiles[blank], self.tiles[i]
                    self.moves += 1
                    if self.tiles == list(range(1,n*n)) + [0]:
                        self.puzzle_done = True
                        self.record('puzzle_%d' % n, self.moves)
            self.puzzle_draw()
            self.s.show_rect(16, 53, 288, 174)
        else:
            super().click(x, y)

    def draw_point(self, point):
        x, y = point
        if self.app == 'Paint':
            if self.paint_zoom and self.paint_drag == 'map':
                self.paint_map_drag(x, y)
                return
            if self.paint_zoom and self.paint_pan:
                if self.paint_pan_anchor is None:
                    if self.paint_map(x, y) is None:
                        return
                    self.paint_pan_anchor = (x, y, self.zoom_x, self.zoom_y)
                ax, ay, ox, oy = self.paint_pan_anchor
                self.paint_set_view(ox-int((x-ax)/4), oy-int((y-ay)/4))
                return
            mapped = self.paint_map(x, y)
            if mapped is None:
                self.previous = None
                self.stroke_started = False
                return
            if self.paint_tool == 'Fill':
                return
            if not self.stroke_started:
                self.checkpoint()
                self.stroke_started = True
            px, py = mapped
            self.paint_focus = mapped
            old = self.previous or mapped
            color = 0 if self.paint_tool == 'Rub' else 1
            dx, dy = px-old[0], py-old[1]
            steps = max(abs(dx), abs(dy), 1)
            radius = self.paint_size//2
            for i in range(steps+1):
                xx, yy = old[0]+dx*i//steps, old[1]+dy*i//steps
                self.canvas.fill_rect(xx-radius, yy-radius, self.paint_size, self.paint_size, color)
            self.previous = mapped
            self.paint_render()
            scale = 4 if self.paint_zoom else 1
            ox, oy = (self.zoom_x, self.zoom_y) if self.paint_zoom else (0, 0)
            left = max(0, min(old[0], px)-radius)
            top = max(0, min(old[1], py)-radius)
            right = min(CW, max(old[0], px)+radius+1)
            bottom = min(CH, max(old[1], py)+radius+1)
            self.s.show_rect(CX+(left-ox)*scale, CY+(top-oy)*scale,
                             (right-left)*scale, (bottom-top)*scale)
            if self.paint_zoom:
                self.paint_navigator()
                self.s.show_rect(MAP_X-1, MAP_Y-1, MAP_W+2, MAP_H+2)
        elif self.app == 'Maze':
            self.maze_move(x, y)
        else:
            super().draw_point(point)

    def tick(self):
        super().tick()
        if self.app == 'Maze' and self.maze_hint_until is not None:
            if time.ticks_diff(time.ticks_ms(), self.maze_hint_until) >= 0:
                self.maze_hint_until = None
                self.maze_draw()
                self.s.show_rect(16, 50, 288, 150)

    def run(self):
        self.boot()
        gc.collect()
        print('MACTOUCH_CLASSIC_READY', VERSION, 'RAM_FREE', gc.mem_free())
        if self.touch.cal is None:
            self.calibrate()
        else:
            self.desktop()
        last_gc = time.ticks_ms()
        release_count = 0
        gesture_app = None
        while True:
            point = self.touch.point()
            if point is not None:
                release_count = 0
                if not self.down:
                    self.down = True
                    self.previous = None
                    before = self.app
                    self.click(*point)
                    # Release an icon-opening press before drawing in its app.
                    gesture_app = self.app if self.app == before else None
                if gesture_app == self.app:
                    self.draw_point(point)
            else:
                release_count += 1
                if release_count >= 2:
                    self.down = False
                    self.previous = None
                    self.stroke_started = False
                    self.paint_drag = None
                    self.paint_pan_anchor = None
                    gesture_app = None
            self.tick()
            if time.ticks_diff(time.ticks_ms(), last_gc) > 5000:
                gc.collect()
                last_gc = time.ticks_ms()
            time.sleep_ms(15)


def run():
    ClassicDesktop().run()
