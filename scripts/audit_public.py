"""Pre-publication content guard. Checks the Git index and unignored files.

This detects accidental inputs/secrets, not copyright clearance or all possible
encoded copies. Keep a source allowlist and review new assets independently.
"""
# SPDX-License-Identifier: MIT
from pathlib import Path
import os,re,subprocess,sys,json,hashlib,struct,zlib
ROOT=Path(__file__).resolve().parents[1]
DENY={'.rom','.img','.dsk','.sit','.hqx','.uf2','.bin','.elf','.o','.a','.exe','.ram','.zip','.7z'}
SKIP={'external','build','dist','.git','__pycache__'}
BADNAMES={'quiet_rom.h','umac-rom.h','umac-disc.h','touch_cal.json'}
def check():
    approval=ROOT/'docs/screenshots/captures.json'
    images=json.loads(approval.read_text()).get('files',{}) if approval.exists() else {}
    paths=set()
    for current,dirs,files in os.walk(ROOT):
        dirs[:]=[x for x in dirs if x not in SKIP]
        paths.update((Path(current)/name).relative_to(ROOT).as_posix() for name in files)
    git=subprocess.run(['git','ls-files','--cached','-z'],cwd=ROOT,capture_output=True)
    indexed=[]
    if not git.returncode:
        indexed=[x.decode() for x in git.stdout.split(b'\0') if x]
        paths.update(indexed)
    errors=[]
    for name in sorted(paths):
        p=ROOT/name
        if any(x in {'external','build','dist','.git'} for x in Path(name).parts):
            errors.append(name+': generated/dependency directory is tracked');continue
        if p.suffix.lower() in DENY or p.name in BADNAMES:
            errors.append(name+': binary/private-input extension or name');continue
        if not p.is_file():errors.append(name+': missing file');continue
        if p.suffix.lower()=='.png':
            data=p.read_bytes();record=images.get(name)
            if not record or record.get('sha256')!=hashlib.sha256(data).hexdigest():
                errors.append(name+': screenshot missing from reviewed capture manifest');continue
            if data[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',data[16:24])!=(320,240):
                errors.append(name+': unexpected screenshot format or dimensions');continue
            offset=8
            while offset<len(data):
                size=struct.unpack('>I',data[offset:offset+4])[0];kind=data[offset+4:offset+8]
                payload=data[offset+4:offset+8+size];crc=struct.unpack('>I',data[offset+8+size:offset+12+size])[0]
                if kind not in [b'IHDR',b'IDAT',b'IEND',b'PLTE',b'tRNS'] or zlib.crc32(payload)!=crc:
                    errors.append(name+': unapproved PNG metadata or corrupt chunk');break
                offset+=size+12
                if kind==b'IEND':break
            if offset!=len(data):errors.append(name+': unexpected PNG trailing data')
            continue
        try:s=p.read_text(encoding='utf-8')
        except UnicodeDecodeError:errors.append(name+': unexpected binary; review asset');continue
        patterns=[('personal Windows path',r'[A-Za-z]:[\\/](?:Users|PicoMacintosh)[\\/]'),
                  ('Pico device serial',r'\bE66[A-F0-9]{13}\b'),
                  ('GitHub token',r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})'),
                  ('private key',r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
                  ('embedded ROM byte prefix',r'0x4d\s*,\s*0x1f\s*,\s*0x81\s*,\s*0x72\s*,\s*0x00\s*,\s*0x40')]
        for label,pattern in patterns:
            if re.search(pattern,s):errors.append(name+': '+label)
    for e in errors:print('FAIL',e)
    if errors:return 1
    print('PUBLIC_SOURCE_SCAN_PASSED',len(paths),'files;',len(indexed),'indexed; no private inputs/binaries detected')
    return 0
if __name__=='__main__':sys.exit(check())
