"""Fetch exact upstream source revisions and apply reviewable project patches."""
# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def run(*args,cwd=None):subprocess.run([str(x) for x in args],cwd=cwd,check=True)
def fetch(target):
    lock=json.loads((ROOT/'upstreams.lock.json').read_text())['components']
    groups={'native':['picoboot','toolset','pico_sdk','umac','musashi','sd_spi'],
            'menu':['picoboot','toolset','pico_sdk','lvgl','pico_fatfs'],
            'micropython':['micropython','pico_sdk']}
    keys=list(lock) if target=='all' else groups[target]
    for key in keys:
        d=lock[key];dest=ROOT/d['path']
        created=False
        if not (dest/'.git').exists():
            if dest.exists() and any(dest.iterdir()):raise RuntimeError('Refusing non-empty dependency directory: '+str(dest))
            dest.parent.mkdir(parents=True,exist_ok=True)
            run('git','clone','--filter=blob:none','--no-checkout',d['url'],dest)
            created=True
        head=subprocess.run(['git','rev-parse','HEAD'],cwd=dest,capture_output=True,text=True)
        if created or head.returncode or head.stdout.strip()!=d['commit']:
            if not created:
                dirty=subprocess.check_output(['git','status','--porcelain'],cwd=dest,text=True)
                if dirty.strip():raise RuntimeError('Dependency has local changes: '+str(dest))
            run('git','fetch','origin',d['commit'],cwd=dest)
            run('git','checkout','--detach',d['commit'],cwd=dest)
        if d.get('patch'):
            patch=ROOT/d['patch']
            already=subprocess.run(['git','apply','--reverse','--check',str(patch)],cwd=dest,capture_output=True)
            if already.returncode:
                run('git','apply','--check',patch,cwd=dest);run('git','apply',patch,cwd=dest)
        if key=='pico_sdk':run('git','submodule','update','--init','--depth','1','lib/tinyusb',cwd=dest)
        if key=='micropython':run('git','submodule','update','--init','--recursive',cwd=dest)
        for relative,source in d.get('added_files',{}).items():
            import shutil
            target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/source,target)
    from generate_assets import generate
    generate()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',choices=['all','native','menu','micropython'],default='native')
    fetch(p.parse_args().target)
