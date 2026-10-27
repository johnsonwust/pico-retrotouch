"""Create a local SD staging folder; never format a card or overwrite a disk."""
# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'dist/sd-card')
    p.add_argument('--disk',type=Path,help='Optional user-owned raw disk image; no automatic download')
    a=p.parse_args();out=a.output;apps=out/'MACAPPS';apps.mkdir(parents=True,exist_ok=True)
    from generate_assets import generate
    generate()
    for src in (ROOT/'src/mactouch').glob('*.py'):shutil.copy2(src,apps/src.name)
    if not (out/'picoboot.cfg').exists():(out/'picoboot.cfg').write_text('auto_boot_timeout=0\n')
    for src in (ROOT/'dist/firmware').glob('*.bin'):
        if src.name in ['MacTouch.bin','Macintosh.bin']:
            dest=out/'DUALBOOT'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
    if a.disk:
        size=a.disk.stat().st_size
        if size<409600 or size>16*1024*1024 or size%512:p.error('Raw disk must be 400 KiB–16 MiB, 512-byte aligned')
        dest=out/'PICOMAC/MAIN.IMG';dest.parent.mkdir(exist_ok=True)
        if dest.exists():raise FileExistsError('Refusing to replace an existing MAIN.IMG')
        shutil.copy2(a.disk,dest)
    # An optional custom app/calibration stays with the user, not in source control.
    print('SD_STAGING_READY',out)
    print('Copy bootstrap/*.py to the MicroPython filesystem separately; see docs/BUILD.md.')
if __name__=='__main__':main()
