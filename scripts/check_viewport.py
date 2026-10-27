"""Exercise the actual display/input code using synthetic pixels only."""
# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--cc',default='gcc');a=p.parse_args()
    out=ROOT/'build/preview';out.mkdir(parents=True,exist_ok=True)
    from generate_assets import generate
    generate();exe=out/'test-viewport.exe'
    subprocess.run([a.cc,'-O2','-I'+str(ROOT/'src/viewport'),'-I'+str(ROOT/'build/generated'),
                    str(ROOT/'tests/test_viewport.c'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],cwd=ROOT,check=True)
if __name__=='__main__':main()
