// SPDX-License-Identifier: GPL-3.0-or-later
/* Exercise actual renderer and input dispatcher with the hardware calls stubbed. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static uint8_t ram[512*342/8],line[640];
static uint32_t hashes[240],framebuffer_updates;
static volatile int physical_down,synthetic_tap,request_id,target_x,target_y;
static volatile int pause_request,paused=1;
#define spi1 0
#define LCD_DC 0
#define LCD_CS 0
static unsigned umac_get_fb_offset(void){return 0;}
static void spi_set_baudrate(int a,int b){}
static void spi_write_blocking(int a,const uint8_t* b,unsigned c){}
static void gpio_put(int a,int b){}
static void command(uint8_t a,const uint8_t* b,unsigned c){}
static void stdio_flush(void){}
static void sleep_ms(int a){}
static uint64_t time_us_64(void){return 0;}
static void tight_loop_contents(void){}
#include "viewport.inc"
static void output(const char* name) {
    FILE* f=fopen(name,"wb");assert(f);fprintf(f,"P4\n320 240\n");
    fwrite(viewport_pixels,1,sizeof viewport_pixels,f);fclose(f);
}
static void app(const char* name) {
    unsigned n=strlen(name);ram[0x910]=n;memcpy(ram+0x911,name,n);
    for(int i=0;i<12;i++)view_profile_poll();
}
int main(int argc,char** argv) {
    for(unsigned i=0;i<sizeof ram;i++)ram[i]=(uint8_t)(i*37u+19u);
    view_fit=0;view_change(0,0);render_viewport();
    for(int y=0;y<222;y++)assert(!memcmp(viewport_pixels+y*40,ram+y*64,40));
    output("build/preview/top.pbm");
    view_change(192,120);render_viewport();
    for(int y=0;y<222;y++)assert(!memcmp(viewport_pixels+y*40,ram+(y+120)*64+24,40));
    output("build/preview/bottom-right.pbm");
    view_change(0,0);int before=request_id;
    viewport_touch(60,230,1);viewport_touch(0,0,0);assert(view_pan && request_id==before);
    viewport_touch(230,150,1);viewport_touch(50,30,1);viewport_touch(0,0,0);
    assert(view_x==176 && view_y==120 && !physical_down && request_id==before);
    viewport_touch(60,230,1);viewport_touch(0,0,0);assert(!view_pan);
    viewport_touch(319,221,1);assert(target_x==495 && target_y==341 && request_id==before+1);
    viewport_touch(0,0,0);assert(!physical_down);
    viewport_touch(20,230,1);viewport_touch(0,0,0);assert(view_fit && request_id==before+1);
    viewport_touch(319,VP_FIT_Y+VP_FIT_H-1,1);assert(target_x==511 && target_y==341);
    viewport_touch(0,0,0);render_viewport();output("build/preview/fit.pbm");
    fit_init();
    FILE* gray=fopen("build/preview/fit-smooth.pgm","wb");assert(gray);fprintf(gray,"P5\n320 240\n255\n");
    for(int y=0;y<240;y++) {
        if(y>=VP_FIT_Y && y<VP_FIT_Y+VP_FIT_H)fit_line(y);
        for(int x=0;x<320;x++) {
            int value=y>=VP_FIT_Y && y<VP_FIT_Y+VP_FIT_H?255-((line[x*2+1]&31)*255+15)/31:
                (viewport_pixels[y*40+x/8]&(128>>(x&7)))?0:255;
            fputc(value,gray);
        }
    }fclose(gray);
    for(int y=0;y<VP_FIT_H;y++)for(int x=0;x<320;x++) {
        int gx=vp_guest_x(x,1,0),gy=vp_guest_y(y+VP_FIT_Y,1,0);
        assert(gx>=0 && gx<512 && gy>=0 && gy<342);
        int a=!!(ram[gy*64+gx/8]&(128>>(gx&7)));
        int c=!!(viewport_pixels[(y+VP_FIT_Y)*40+x/8]&(128>>(x&7)));
        assert(a==c);
    }
    viewport_touch(220,230,1);viewport_touch(0,0,0);assert(!view_fit && !view_pan && !view_x && !view_y);
    memset(ram,255,sizeof ram);
    for(int y=0;y<VP_FIT_H;y++)for(int x=0;x<320;x++)assert(fit_coverage(ram,x,y)==912);
    memset(ram,0,sizeof ram);
    for(int y=0;y<VP_FIT_H;y++)for(int x=0;x<320;x++)assert(fit_coverage(ram,x,y)==0);
    app("Finder");assert(!view_fit && !view_x && !view_y && view_profile_index==0);
    const char* games[]={"MissileCommand","Daleks","Bubba","Break Bricks","BlackBox","Blackjack","Brickles 5.0"};
    for(int i=0;i<7;i++){app(games[i]);assert(view_fit && !view_pan);}
    app("Blackjack");view_action(0);view_change(192,120);view_profile_remember(1);
    assert(!view_fit && view_profiles[view_profile_index].manual);
    app("Finder");assert(!view_fit && !view_x && !view_y);
    app("Blackjack");assert(!view_fit && view_x==192 && view_y==120);
    int id=request_id;viewport_touch(280,230,1);viewport_touch(0,0,0);
    assert(view_fit && !view_pan && !view_profiles[view_profile_index].manual && id==request_id);
    physical_down=1;app("Finder");assert(view_fit && !strcmp(view_profiles[view_profile_index].name,"Blackjack"));
    physical_down=0;view_profile_poll();assert(!view_fit);
    int previous=view_profile_index;ram[0x910]=255;
    for(int i=0;i<12;i++)view_profile_poll();assert(view_profile_index==previous);
    app("Calculator");assert(!view_fit);
    puts("ADAPTIVE_PROFILES_DEFAULTS_RECALL_TOUCH_GUARD_AND_RESET_PASSED");
    puts("VIEWPORT_RENDER_AND_INPUT_CHECKS_PASSED");return 0;
}
