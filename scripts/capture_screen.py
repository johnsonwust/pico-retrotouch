"""Capture native firmware's LCD/guest framebuffer with per-row checksums."""
# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,hashlib,io,json,time,serial
from serial.tools import list_ports
from PIL import Image
def main():
    p=argparse.ArgumentParser();p.add_argument('--port');p.add_argument('--mode',choices=['screen','frame'],default='screen')
    p.add_argument('--output',type=Path,default=Path('build/captures/lcd.png'));a=p.parse_args()
    ports=[x.device for x in list_ports.comports() if x.vid==0x2e8a]
    if not a.port and len(ports)!=1:p.error('Use --port to choose a Pico running native firmware')
    rows={};w=h=0;gray=False
    with serial.Serial(a.port or ports[0],115200,timeout=.3,write_timeout=1) as s:
        def receive():
            nonlocal w,h,gray
            end=time.monotonic()+15
            while time.monotonic()<end:
                line=s.readline().strip()
                if line.startswith((b'FRAME_HEX ',b'FRAME_GRAY ')):
                    tag,ww,hh=line.split();w,h=int(ww),int(hh);gray=tag==b'FRAME_GRAY'
                elif line==b'FRAME_END':return
                else:
                    try:
                        y,hexdata,checksum=line.split(b':');data=bytes.fromhex(hexdata.decode());value=2166136261
                        for v in data:value=((value^v)*16777619)&0xffffffff
                        if len(data)==(w if gray else w//8) and value==int(checksum,16):rows[int(y)]=data
                    except ValueError:pass
            raise RuntimeError('Capture timed out; run native firmware and check the selected port')
        s.reset_input_buffer();s.write((a.mode+'\n').encode());receive()
        if not w or not h:raise RuntimeError('No framebuffer header received')
        for _ in range(3):
            missing=[y for y in range(h) if y not in rows]
            if not missing:break
            for y in missing:
                s.write((('srow' if a.mode=='screen' else 'row')+' %d\n'%y).encode());receive()
        if any(y not in rows for y in range(h)):raise RuntimeError('Incomplete checksummed frame')
    header=('P5\n%d %d\n255\n' if gray else 'P4\n%d %d\n')%(w,h)
    raw=header.encode()+b''.join(rows[y] for y in range(h))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    Image.open(io.BytesIO(raw)).save(a.output,format='PNG')
    proof={'mode':a.mode,'width':w,'height':h,'verified_rows':h,'resampling':False,
           'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}
    a.output.with_suffix('.json').write_text(json.dumps(proof,indent=2)+'\n')
    print('CHECKSUMMED_FRAME_SAVED',a.output,w,h)
if __name__=='__main__':main()
