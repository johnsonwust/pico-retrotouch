"""Portable source build. ROM input is explicit and never downloaded."""
# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,json,os,shutil,struct,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser()
    p.add_argument('target',choices=['native','menu','micropython'])
    p.add_argument('--rom',type=Path,help='User-supplied 128 KiB Mac Plus V3 ROM; native only')
    p.add_argument('--calibration',type=Path,help='Six affine coefficients from touch_cal.json')
    p.add_argument('--host-cc',default='gcc');p.add_argument('--cmake',default='cmake')
    p.add_argument('--make',default=shutil.which('make'));p.add_argument('--toolchain-dir',type=Path)
    a=p.parse_args();env=os.environ.copy()
    if a.target=='native' and not a.rom:p.error('native requires --rom; no ROM is bundled or downloaded')
    if not a.make:p.error('GNU make is required; supply --make /path/to/make')
    for name in ['pico-sdk']+(['umac','sd-spi','PicoBoot'] if a.target=='native' else ['PicoBoot','lvgl','pico-fatfs'] if a.target=='menu' else ['micropython']):
        if not (ROOT/'external'/name).is_dir():p.error('Missing dependency '+name+'; run scripts/fetch_dependencies.py first')
    if a.toolchain_dir:
        tool=a.toolchain_dir.resolve();env['PICO_TOOLCHAIN_PATH']=str(tool)
        env['PATH']=str(tool/'bin')+os.pathsep+str(tool)+os.pathsep+env['PATH']
    env['PATH']=str(Path(a.make).resolve().parent)+os.pathsep+env['PATH']
    env['PICO_SDK_PATH']=str(ROOT/'external/pico-sdk')
    def run(args,cwd=ROOT):subprocess.run([str(x) for x in args],cwd=cwd,env=env,check=True)
    from generate_assets import generate
    generate();gen=ROOT/'build/generated';out=ROOT/'build'/a.target
    common=['-G','Unix Makefiles','-DCMAKE_MAKE_PROGRAM='+str(Path(a.make).resolve()),'-DPICO_NO_PICOTOOL=1']
    if a.toolchain_dir:common+=['-DPICO_TOOLCHAIN_PATH='+str(a.toolchain_dir.resolve())]
    if a.target=='native':
        data=a.rom.read_bytes()
        if len(data)!=131072 or data[:4]!=bytes.fromhex('4d1f8172'):p.error('Expected a 128 KiB Mac Plus V3 ROM with version 4d1f8172')
        u=ROOT/'external/umac';m=u/'external/Musashi';suffix='.exe' if os.name=='nt' else ''
        patcher=gen/('patch_rom'+suffix)
        run([a.host_cc,'-O2','-DSIM','-DUMAC_MEMSIZE=192','-DDISP_WIDTH=512','-DDISP_HEIGHT=342',
             '-DBYTE_ORDER=1234','-DLITTLE_ENDIAN=1234','-I'+str(u/'include'),'-I'+str(m),
             ROOT/'scripts/patch_rom.c',u/'src/rom.c','-o',patcher])
        patched=gen/'private-patched-rom.bin';run([patcher,a.rom.resolve(),patched])
        data=patched.read_bytes()
        (gen/'quiet_rom.h').write_text('\n'.join(','.join('0x%02x'%x for x in data[i:i+16])+',' for i in range(0,len(data),16)))
        cal=json.loads(a.calibration.read_text()) if a.calibration else json.loads((ROOT/'config/touch_cal.example.json').read_text())
        if len(cal)!=6 or not all(isinstance(x,(int,float)) for x in cal):p.error('Calibration must be a JSON array of six numbers')
        (gen/'touch_cal.h').write_text('static const float touch_cal[6]={'+','.join(str(float(x))+'f' for x in cal)+'};\n')
        if not a.calibration:print('Using example calibration; calibrate each physical screen before normal use.')
        generator=gen/('m68kmake'+suffix)
        run([a.host_cc,'-O2',m/'m68kmake.c','-o',generator]);run([generator],cwd=m)
        run([sys.executable,u/'tools/decorate_ops.py',m/'m68kops.c',u/'tools/fn_hot200.txt'])
        run([a.cmake,'-S',ROOT/'src/native','-B',out,*common,'-DCMAKE_BUILD_TYPE=Release'])
        run([a.cmake,'--build',out,'--parallel','8','--target','picomac_dualboot'])
        source=out/'picomac_dualboot.elf';filename='Macintosh.bin';limit=0x100000
    elif a.target=='menu':
        run([a.cmake,'-S',ROOT/'external/PicoBoot','-B',out,*common,
             '-DPICO_SDK_PATH='+str(ROOT/'external/pico-sdk'),'-DPICOBOOT_BOARD=crowpanel_pico_hmi_28',
             '-DPICO_LVGL_DIR='+str(ROOT/'external/lvgl'),'-DPICO_FATFS_DIR='+str(ROOT/'external/pico-fatfs')])
        run([a.cmake,'--build',out,'--parallel','8','--target','picoboot_lvgl_crowpanel'])
        source=out/'targets/picoboot_lvgl_crowpanel/picoboot_lvgl_crowpanel.elf';filename='bootmenu.bin';limit=0x80000
    else:
        mp=ROOT/'external/micropython'
        run([a.make,'-j8','CC="'+a.host_cc+'"','PYTHON="'+sys.executable+'"'],cwd=mp/'mpy-cross')
        env['MICROPY_MPYCROSS']=str(mp/'mpy-cross/build'/('mpy-cross.exe' if os.name=='nt' else 'mpy-cross'))
        run([a.cmake,'-S',mp/'ports/rp2','-B',out,*common,
             '-DPICO_SDK_PATH_OVERRIDE='+str(ROOT/'external/pico-sdk'),'-DMICROPY_BOARD=RPI_PICO',
             '-DMICROPY_HW_FLASH_STORAGE_BYTES=524288','-DPython3_EXECUTABLE='+sys.executable,
             '-DMICROPY_MAKE_EXECUTABLE='+str(Path(a.make).resolve())])
        run([a.cmake,'--build',out,'--parallel','8','--target','firmware'])
        source=out/'firmware.elf';filename='MacTouch.bin';limit=0x100000
    dist=ROOT/'dist/firmware';dist.mkdir(parents=True,exist_ok=True)
    objcopy=shutil.which('arm-none-eabi-objcopy',path=env['PATH'])
    if not objcopy:raise RuntimeError('arm-none-eabi-objcopy not on toolchain PATH')
    dest=dist/filename;run([objcopy,'-O','binary',source,dest]);data=dest.read_bytes()
    assert len(data)<=limit,'Firmware exceeds protected flash partition'
    address=0x10000000 if a.target=='menu' else 0x10080000
    count=(len(data)+255)//256;uf2=bytearray()
    for i in range(count):
        uf2+=struct.pack('<8I',0x0a324655,0x9e5d5157,0x2000,address+i*256,256,i,count,0xe48bff56)
        uf2+=data[i*256:(i+1)*256].ljust(256,b'\xff')+bytes(220)+struct.pack('<I',0x0ab16f30)
    dest.with_suffix('.uf2').write_bytes(uf2)
    print('BUILT_LOCAL_ONLY',dest,len(data),'bytes')
    if a.target=='native':print('Contains your supplied ROM. Keep firmware, ELF, headers and build outputs private.')
if __name__=='__main__':main()
