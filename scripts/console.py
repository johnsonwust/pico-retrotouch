"""Small serial console with explicit selection if multiple Picos are connected."""
# SPDX-License-Identifier: MIT
import argparse,time,serial
from serial.tools import list_ports
p=argparse.ArgumentParser();p.add_argument('--port');p.add_argument('command',nargs='+');a=p.parse_args()
ports=[x.device for x in list_ports.comports() if x.vid==0x2e8a]
if not a.port and len(ports)!=1:p.error('Use --port to select a device; candidates: '+', '.join(ports))
with serial.Serial(a.port or ports[0],115200,timeout=.2,write_timeout=1) as s:
    s.reset_input_buffer();s.write((' '.join(a.command)+'\n').encode());until=time.monotonic()+6
    while time.monotonic()<until:
        try:line=s.readline()
        except serial.SerialException:break
        if line:print(line.decode(errors='replace').rstrip())
