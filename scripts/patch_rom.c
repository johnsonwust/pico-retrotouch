/* SPDX-License-Identifier: GPL-3.0-or-later
 * Local-only adapter around umac's source-available patch routine. No ROM bytes here. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
int rom_patch(uint8_t*);
int main(int argc,char** argv) {
    uint8_t data[131072];
    if(argc!=3)return 2;
    FILE* f=fopen(argv[1],"rb");if(!f)return 3;
    if(fread(data,1,sizeof data,f)!=sizeof data || fgetc(f)!=EOF){fclose(f);return 4;}fclose(f);
    if(rom_patch(data))return 5;
    /* Silent SysBeep, retaining Pascal duration-argument cleanup. */
    const uint8_t quiet[]={0x20,0x5f,0x54,0x8f,0x4e,0xd0};memcpy(data+0x11dc,quiet,sizeof quiet);
    f=fopen(argv[2],"wb");if(!f)return 6;
    int ok=fwrite(data,1,sizeof data,f)==sizeof data;fclose(f);return ok?0:7;
}
