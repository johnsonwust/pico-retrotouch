// SPDX-License-Identifier: GPL-3.0-or-later
/* SPI display/touch port for RP2040 + Waveshare ResTouch 2.8.
 * Uses Matt Evans' MIT umac / Musashi core unchanged.
 * Original port implementation, 2026-10-26.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "pico/bootrom.h"
#include "pico/mutex.h"
#include "hardware/spi.h"
#include "hardware/clocks.h"
#include "hardware/watchdog.h"
#include "hardware/structs/watchdog.h"
#include "umac.h"
#include "m68k.h"
#include "touch_cal.h"
#include "ff.h"
#include "hw_config.h"

#define LCD_CS 9
#define LCD_DC 8
#define TOUCH_CS 16
#define SD_CS 22
#define LCD_H 240
#define LCD_Y 0
static uint8_t ram[RAM_SIZE];
static const uint8_t rom[] = {
#include "quiet_rom.h"
};
static uint32_t disk_size=409600u;
#define DISK_SIZE disk_size
#ifndef PICOMAC_DISK_PATH
#define PICOMAC_DISK_PATH "0:/PICOMAC/MAIN.IMG"
#endif
static const char* active_disk_path=PICOMAC_DISK_PATH;
static uint8_t line[640];
static uint32_t hashes[LCD_H];
static volatile uint32_t loops, framebuffer_updates;
static volatile bool ready, pause_request, paused;
static volatile int target_x=15, target_y=15, request_id, physical_down;
static volatile int touch_z1,touch_z2,touch_irq,synthetic_tap;
static volatile int key_request=-1;
static int mouse_button;
static unsigned reads;
static unsigned writes;
static mutex_t spi_bus;
static FIL system_file;
static bool sd_active;


/* Called only by emulation core. Bus lock also covers all FatFs metadata. */
static bool prepare_sd_disk(void) {
    mutex_enter_blocking(&spi_bus);
    set_spi_dma_irq_channel(true,false);
    FRESULT result=FR_NOT_READY;FILINFO info;
    if(sd_init_driver())result=f_mount(&sd_get_by_num(0)->fatfs,"0:",1);
    if(result==FR_OK)result=f_stat(active_disk_path,&info);
    if((result==FR_NO_FILE || result==FR_NO_PATH) && !strcmp(PICOMAC_DISK_PATH,"0:/PICOMAC/MAIN.IMG")) {
        active_disk_path="0:/PICOMAC/SYSTEM32.IMG";result=f_stat(active_disk_path,&info);
    }
    if(result==FR_OK && (info.fsize<409600u || info.fsize>16u*1024u*1024u || (info.fsize&511u)))result=FR_INVALID_OBJECT;
    if(result==FR_OK)disk_size=(uint32_t)info.fsize;
    if(result==FR_OK)result=f_open(&system_file,active_disk_path,FA_READ|FA_WRITE);
    mutex_exit(&spi_bus);
    printf("SD_WORKING_IMAGE path=%s status=%d\n",active_disk_path,result);
    return result==FR_OK;
}
static void return_to_menu(void) {
    if(ready) {
        pause_request=true;while(!paused)tight_loop_contents();
        mutex_enter_blocking(&spi_bus);if(sd_active)f_sync(&system_file);mutex_exit(&spi_bus);
    }
    printf("RETURN_TO_BOOT_MENU\n");stdio_flush();sleep_ms(40);
    watchdog_hw->scratch[0]=0xB00110C0;watchdog_hw->scratch[1]=2;
    watchdog_reboot(0,0,0);while(true)tight_loop_contents();
}

static void command(uint8_t value, const uint8_t *data, size_t size) {
    gpio_put(LCD_DC, 0); gpio_put(LCD_CS, 0);
    spi_write_blocking(spi1, &value, 1);
    if (size) { gpio_put(LCD_DC, 1); spi_write_blocking(spi1, data, size); }
    gpio_put(LCD_CS, 1);
}
static void panel_init(void) {
    const int pins[]={LCD_CS,LCD_DC,15,13,TOUCH_CS,SD_CS};
    for (unsigned i=0;i<sizeof(pins)/sizeof(pins[0]);i++) {
        gpio_init(pins[i]); gpio_set_dir(pins[i],GPIO_OUT); gpio_put(pins[i],1);
    }
    gpio_init(17); gpio_set_dir(17,GPIO_IN); gpio_pull_up(17);
    spi_init(spi1,40000000);
    gpio_set_function(10,GPIO_FUNC_SPI); gpio_set_function(11,GPIO_FUNC_SPI); gpio_set_function(12,GPIO_FUNC_SPI);
    spi_set_format(spi1,8,SPI_CPOL_0,SPI_CPHA_0,SPI_MSB_FIRST);
    gpio_put(15,0); sleep_ms(10); gpio_put(15,1); sleep_ms(10);
    command(0x01,NULL,0); sleep_ms(150);
    command(0x11,NULL,0); sleep_ms(10);
    const uint8_t format=0x55, rotate=0x60;
    command(0x3a,&format,1); command(0x20,NULL,0); command(0x13,NULL,0);
    command(0x36,&rotate,1); command(0x29,NULL,0);
    const uint8_t cols[]={0,0,1,63}, rows[]={0,0,0,239};
    command(0x2a,cols,4); command(0x2b,rows,4);
    uint8_t cmd=0x2c; gpio_put(LCD_DC,0); gpio_put(LCD_CS,0);
    spi_write_blocking(spi1,&cmd,1); gpio_put(LCD_DC,1);
    memset(line,0,sizeof line);
    for (int y=0;y<240;y++) spi_write_blocking(spi1,line,sizeof line);
    gpio_put(LCD_CS,1);
}
#include "viewport.inc"
static int channel(uint8_t cmd) {
    uint8_t tx[3]={cmd,0,0},rx[3];
    gpio_put(TOUCH_CS,0); spi_write_read_blocking(spi1,tx,rx,3); gpio_put(TOUCH_CS,1);
    return ((rx[1]<<8)|rx[2])>>3;
}
static int median(int *v) {
    for(int i=1;i<5;i++) for(int j=i;j>0 && v[j]<v[j-1];j--) {
        int t=v[j];v[j]=v[j-1];v[j-1]=t;
    }
    return v[2];
}
static void touch_poll(void) {
    static int was_down,filtered_x,filtered_y;
    if(view_debug_touch)return;
    spi_set_baudrate(spi1,1000000);
    int zs1[5],zs2[5];
    for(int i=0;i<5;i++) { channel(0xb0);zs1[i]=channel(0xb0);channel(0xc0);zs2[i]=channel(0xc0); }
    touch_z1=median(zs1);touch_z2=median(zs2);touch_irq=gpio_get(17);
    if(touch_z1<100 || touch_z2>4010 || touch_z1+4095-touch_z2<200) {
        viewport_touch(0,0,0);was_down=0;
        return;
    }
    int xs[5],ys[5];
    for(int i=0;i<5;i++) { channel(0xd0);xs[i]=channel(0xd0);channel(0x90);ys[i]=channel(0x90); }
    int x=median(xs),y=median(ys);
    if (x<80 || x>4015 || y<80 || y>4015) { viewport_touch(0,0,0);was_down=0;return; }
    int sx=(int)roundf(touch_cal[0]*x+touch_cal[1]*y+touch_cal[2]);
    int sy=(int)roundf(touch_cal[3]*x+touch_cal[4]*y+touch_cal[5]);
    if (sx<0)sx=0;if(sx>319)sx=319;if(sy<0)sy=0;if(sy>239)sy=239;
    if(!was_down) { filtered_x=sx*4;filtered_y=sy*4; }
    else { filtered_x=(filtered_x*2+sx*4)/3;filtered_y=(filtered_y*2+sy*4)/3; }
    sx=(filtered_x+2)/4;sy=(filtered_y+2)/4;
    viewport_touch(sx,sy,1);was_down=1;
}
static void pointer_poll(void) {
    static uint64_t last,started_at,pressed_at;
    static int seen_request,tracking,applied_x=-1,applied_y=-1;
    uint64_t now=time_us_64();
    if(now-last<8000)return;
    last=now;
    if(request_id!=seen_request) {
        if(mouse_button) { mouse_button=0;umac_mouse(0,0,0); }
        seen_request=request_id;tracking=1;started_at=now;
        applied_x=-1;applied_y=-1;
    }
    if(!tracking)return;
    int x=target_x,y=target_y;
    /* Apple DV520 tablet protocol: no relative acceleration or feedback loop. */
    if(x!=applied_x || y!=applied_y) {
        RAM_WR16(0x828,y);RAM_WR16(0x82a,x);
        RAM_WR16(0x82c,y);RAM_WR16(0x82e,x);
        RAM_WR8(0x8ce,RAM_RD8(0x8cf));
        applied_x=x;applied_y=y;
    }
    if(now-started_at>=50000 && !mouse_button) { mouse_button=1;pressed_at=now; }
    if(mouse_button && !physical_down && synthetic_tap!=2 && now-pressed_at>=100000) {
        mouse_button=0;tracking=0;synthetic_tap=0;
    }
    umac_mouse(0,0,mouse_button);
}
static int emulator_disk_read(void *ctx,uint8_t *out,unsigned offset,unsigned size) {
    if(offset>DISK_SIZE || size>DISK_SIZE-offset)return -1;
    if(sd_active) {
        UINT count=0;mutex_enter_blocking(&spi_bus);spi_set_baudrate(spi1,5000000);
        FRESULT result=f_lseek(&system_file,offset);
        if(result==FR_OK)result=f_read(&system_file,out,size,&count);
        mutex_exit(&spi_bus);
        if(result!=FR_OK || count!=size) { printf("SD_READ_ERROR %d %u\n",result,count);return -1; }
    } else return -1;
    reads++;
    if(reads<=8)printf("DISK_READ %u %u\n",offset,size);
    return 0;
}
static int emulator_disk_write(void *ctx,uint8_t *data,unsigned offset,unsigned size) {
    if(!sd_active || offset>DISK_SIZE || size>DISK_SIZE-offset)return -1;
    UINT count=0;mutex_enter_blocking(&spi_bus);spi_set_baudrate(spi1,5000000);
    FRESULT result=f_lseek(&system_file,offset);
    if(result==FR_OK)result=f_write(&system_file,data,size,&count);
    if(result==FR_OK && count==size)result=f_sync(&system_file);
    mutex_exit(&spi_bus);
    if(result!=FR_OK || count!=size) { printf("SD_WRITE_ERROR %d %u\n",result,count);return -1; }
    writes++;return 0;
}
static void emulator_core(void) {
    disc_descr_t discs[DISC_NUM_DRIVES]={0};
    sd_active=prepare_sd_disk();
    if(!sd_active) { ready=false;printf("SD_REQUIRED: insert existing system card, then reboot\n");while(true)sleep_ms(100); }
    discs[0].size=DISK_SIZE;discs[0].read_only=!sd_active;
    discs[0].op_read=emulator_disk_read;discs[0].op_write=emulator_disk_write;
    umac_init(ram,(void*)rom,discs);
    ready=true;
    printf("EMULATOR_READY RAM=%u ROM=%u DISK=%u\n",RAM_SIZE,(unsigned)sizeof rom,(unsigned)DISK_SIZE);
    uint64_t last_v=0,last_s=0,key_up=0;
    int held_key=-1;
    while(true) {
        if(pause_request) { paused=true;while(pause_request)tight_loop_contents();paused=false; }
        umac_loop();loops++;
        uint64_t now=time_us_64();
        if(now-last_v>=16667) { umac_vsync_event();last_v=now; }
        if(now-last_s>=1000000) { umac_1hz_event();last_s=now; }
        pointer_poll();
        if(key_request>=0 && held_key<0) {
            held_key=key_request;key_request=-1;umac_kbd_event(held_key,1);key_up=now+120000;
        }
        if(held_key>=0 && now>=key_up) { umac_kbd_event(held_key,0);held_key=-1; }
    }
}
static void snapshot_row(int y) {
    const uint8_t *src=ram+umac_get_fb_offset()+y*(DISP_WIDTH/8);
    char record[DISP_WIDTH/4+32];
    int used=sprintf(record,"%03d:",y);uint32_t hash=2166136261u;
    for(int i=0;i<DISP_WIDTH/8;i++) { hash=(hash^src[i])*16777619u;used+=sprintf(record+used,"%02x",src[i]); }
    used+=sprintf(record+used,":%08lx\n",(unsigned long)hash);
    fwrite(record,1,used,stdout);stdio_flush();sleep_ms(2);
}
static void snapshot(int row) {
    if(!ready) { printf("EMULATOR_NOT_READY\n");return; }
    pause_request=true;
    while(!paused)tight_loop_contents();
    printf("FRAME_HEX %d %d\n",DISP_WIDTH,DISP_HEIGHT);
    stdio_flush();
    if(row>=0 && row<DISP_HEIGHT)snapshot_row(row);
    else for(int y=0;y<DISP_HEIGHT;y++)snapshot_row(y);
    printf("\nFRAME_END\n");stdio_flush();pause_request=false;
}
#include "diagnostics.inc"
static void console(void) {
    static char input[96];static unsigned used;
    int c;
    while((c=getchar_timeout_us(0))!=PICO_ERROR_TIMEOUT) {
        if(c=='\r')continue;
        if(c!='\n' && used<sizeof(input)-1) { input[used++]=(char)c;continue; }
        input[used]=0;used=0;
        int x,y,k;
        if(!strcmp(input,"menu"))return_to_menu();
        else if(!strcmp(input,"diag"))diagnostics();
        else if(!strcmp(input,"frame"))snapshot(-1);
        else if(!strcmp(input,"screen"))viewport_snapshot(-1);
        else if(sscanf(input,"srow %d",&y)==1)viewport_snapshot(y);
        else if(!strncmp(input,"view ",5))viewport_command(input+5);
        else if(!strcmp(input,"view"))viewport_report();
        else if(sscanf(input,"vdown %d %d",&x,&y)==2 || sscanf(input,"vmove %d %d",&x,&y)==2) {
            view_debug_touch=1;viewport_touch(x,y,1);viewport_report();
        } else if(!strcmp(input,"vup")) {viewport_touch(0,0,0);view_debug_touch=0;viewport_report();}
        else if(sscanf(input,"row %d",&y)==1)snapshot(y);
        else if(sscanf(input,"tap %d %d",&x,&y)==2 || sscanf(input,"down %d %d",&x,&y)==2) {
            target_x=x<0?0:x>=DISP_WIDTH?DISP_WIDTH-1:x;target_y=y<0?0:y>=DISP_HEIGHT?DISP_HEIGHT-1:y;physical_down=0;synthetic_tap=1;request_id++;
            if(input[0]=='d')synthetic_tap=2;
            printf("TAP_QUEUED %d %d\n",target_x,target_y);
        } else if(sscanf(input,"move %d %d",&x,&y)==2) {
            target_x=x<0?0:x>=DISP_WIDTH?DISP_WIDTH-1:x;target_y=y<0?0:y>=DISP_HEIGHT?DISP_HEIGHT-1:y;
            printf("MOVE_QUEUED %d %d\n",target_x,target_y);
        } else if(!strcmp(input,"up")) {
            synthetic_tap=0;physical_down=0;printf("BUTTON_UP\n");
        } else if(sscanf(input,"key %i",&k)==1) { key_request=k;printf("KEY_QUEUED %d\n",k); }
        else if(!strcmp(input,"bootloader")) { printf("BOOTLOADER\n");stdio_flush();sleep_ms(50);reset_usb_boot(0,0); }
        else if(!strcmp(input,"status")) {
            printf("STATUS loops=%lu pc=%08lx mouse=%u,%u button=%d reads=%u updates=%lu touch=%d z=%d,%d irq=%d target=%d,%d disk=%s writes=%u\n",
                   (unsigned long)loops,(unsigned long)m68k_get_reg(NULL,M68K_REG_PC),RAM_RD16(0x832),RAM_RD16(0x830),mouse_button,reads,(unsigned long)framebuffer_updates,physical_down,touch_z1,touch_z2,touch_irq,target_x,target_y,sd_active?"SD_RW":"FLASH_RO",writes);
        } else printf("COMMANDS status frame tap_X_Y key_CODE bootloader\n");
    }
}
int main(void) {
    set_sys_clock_khz(200000,true);
    stdio_init_all();
    mutex_init(&spi_bus);
    gpio_init(25);gpio_set_dir(25,GPIO_OUT);
    panel_init();
    sleep_ms(1000);
    printf("PICOMAC_RESTOUCH dualboot-0.3.2 guest512x342 adaptive-view SD-library quiet-beep clock=%lu\n",(unsigned long)clock_get_hz(clk_sys));
    multicore_launch_core1(emulator_core);
    while(!ready) { console();sleep_ms(1); }
    uint64_t last_frame=0,last_touch=0;
    bool force=true;
    while(true) {
        uint64_t now=time_us_64();
        console();
        if(now-last_touch>=16000) { mutex_enter_blocking(&spi_bus);touch_poll();mutex_exit(&spi_bus);last_touch=now; }
        if(now-last_frame>=50000) { mutex_enter_blocking(&spi_bus);display_frame(force);mutex_exit(&spi_bus);force=false;last_frame=now; }
        gpio_put(25,(now/500000)&1);
        tight_loop_contents();
    }
}
