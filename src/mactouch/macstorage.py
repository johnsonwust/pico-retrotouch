# SPDX-License-Identifier: MIT
"""Synchronous shared-SPI storage for MacTouch; FAT volumes are never formatted."""
import os
import time
import json


class Storage:
    def __init__(self, screen, namespace='MacTouch'):
        self.screen = screen
        self.namespace = namespace
        self.ready = False
        self.attempted = False
        self.card = None
        self.medium = 'Pico'
        self.root = '/' + namespace.lower() + '_data'
        self.error = ''
        self.created_root = False

    def ensure(self, retry=False):
        if self.ready and not retry:
            return
        if self.attempted and not retry:
            raise OSError(self.error or 'Storage unavailable')
        self.attempted = True
        s = self.screen
        s.cs(1)
        s.tpcs(1)
        s.sdcs(1)
        try:
            import sdcard_crc
            # Bootstrap has already mounted the card so Python can import apps.
            # Reuse that block device; a second mount would force Pico fallback.
            try:
                import sd_mount
                self.card=sd_mount.card
            except ImportError:
                pass

            class BusCard(sdcard_crc.SDCard):
                def select_bus(card):
                    s.cs(1)
                    s.tpcs(1)
                    s.spi.init(baudrate=10000000, polarity=0, phase=0)

                def readblocks(card, block, buf):
                    card.select_bus()
                    return super().readblocks(block, buf)

                def writeblocks(card, block, buf):
                    card.select_bus()
                    return super().writeblocks(block, buf)

                def wait_ready(card):
                    start = time.ticks_ms()
                    while card.spi.read(1, 0xff)[0] == 0:
                        if time.ticks_diff(time.ticks_ms(), start) > 3000:
                            raise OSError('SD write timeout')

                def write(card, token, buf):
                    card.cs(0)
                    try:
                        card.spi.read(1, token)
                        card.spi.write(buf)
                        card.spi.write(b'\xff\xff')
                        response = card.spi.read(1, 0xff)[0] & 31
                        if response != 5:
                            raise OSError('SD rejected write: %d' % response)
                        card.wait_ready()
                    finally:
                        card.cs(1)
                        card.spi.write(b'\xff')

                def write_token(card, token):
                    card.cs(0)
                    try:
                        card.spi.read(1, token)
                        card.spi.write(b'\xff')
                        card.wait_ready()
                    finally:
                        card.cs(1)
                        card.spi.write(b'\xff')

            if self.card is None:
                self.card = BusCard(s.spi, s.sdcs, baudrate=10000000)
                os.mount(self.card, '/sd')
            self.root = '/sd/' + self.namespace
            self.medium = 'SD'
            self.error = ''
        except OSError as exc:
            s.sdcs(1)
            self.error = str(exc)
            self.card = None
            self.medium = 'Pico'
            self.root = '/' + self.namespace.lower() + '_data'
        for path in (self.root, self.root + '/paintings'):
            try:
                os.mkdir(path)
                if path == self.root:
                    self.created_root = True
            except OSError:
                if not os.stat(path)[0] & 0x4000:
                    raise
        self.ready = True

    def exists(self, path):
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def read_json(self, name, default):
        self.ensure()
        path = self.root + '/' + name
        if not self.exists(path):
            if self.exists(path + '.bak'):
                path += '.bak'
            else:
                return default
        if os.stat(path)[6] > 16384:
            raise ValueError('JSON file too large')
        with open(path) as f:
            return json.load(f)

    def write_json(self, name, value):
        self.ensure()
        path = self.root + '/' + name
        temp, backup = path + '.tmp', path + '.bak'
        with open(temp, 'w') as f:
            json.dump(value, f)
        os.sync()
        had_old = self.exists(path)
        if self.exists(backup):
            os.remove(backup)
        if had_old:
            os.rename(path, backup)
        try:
            os.rename(temp, path)
        except OSError:
            if had_old:
                os.rename(backup, path)
            raise
        os.sync()
        if had_old:
            os.remove(backup)
        os.sync()

    def pictures(self):
        self.ensure()
        return sorted(n for n in os.listdir(self.root + '/paintings')
                      if n.startswith('Sketch-') and n.endswith('.pbm'))

    def save_picture(self, data):
        self.ensure()
        folder = self.root + '/paintings/'
        number = 1
        while self.exists(folder + 'Sketch-%04d.pbm' % number):
            number += 1
        name = 'Sketch-%04d.pbm' % number
        temp = folder + name + '.tmp'
        with open(temp, 'wb') as f:
            f.write(b'P4\n224 128\n')
            f.write(data)
        os.sync()
        os.rename(temp, folder + name)
        os.sync()
        return name

    def load_picture(self, name):
        self.ensure()
        if '/' in name or name not in self.pictures():
            raise ValueError('Unknown picture')
        with open(self.root + '/paintings/' + name, 'rb') as f:
            if f.readline().strip() != b'P4' or f.readline().strip() != b'224 128':
                raise ValueError('Expected 224 x 128 PBM')
            data = f.read(3585)
        if len(data) != 3584:
            raise ValueError('Incomplete picture')
        return data
