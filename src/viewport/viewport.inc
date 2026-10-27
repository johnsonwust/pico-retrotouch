// SPDX-License-Identifier: GPL-3.0-or-later
/* Physical 320x240 view over an unmodified 512x342 Macintosh framebuffer. */
#include "geometry.h"
#include "font.h"
static uint8_t viewport_pixels[VP_LCD_W*VP_LCD_H/8];
static int view_x,view_y,view_fit,view_pan;
static int view_debug_touch;
static unsigned view_revision=1;
static int view_touch_owner,view_start_x,view_start_y,view_drag_x,view_drag_y;
static const int view_edges[]={0,43,85,114,143,172,201,244,320};
/* Area filtering retains thin strokes and small sprites when fitting the screen.
 * Horizontal overlap units are 1/5 guest pixel, vertical units are 1/71.
 * A destination pixel has constant total weight 8*114=912. */
static uint16_t fit_x0[320],fit_y0[VP_FIT_H],fit_rgb[913];
static uint8_t fit_xw[320][3],fit_yw[VP_FIT_H][3];
static void fit_init(void) {
    static int initialized;if(initialized)return;initialized=1;
    for(int x=0;x<320;x++) {
        int a=x*8,b=a+8;fit_x0[x]=a/5;
        for(int k=0;k<3;k++) {
            int left=(fit_x0[x]+k)*5,right=left+5;
            fit_xw[x][k]=vp_clamp((b<right?b:right)-(a>left?a:left),0,5);
        }
    }
    for(int y=0;y<VP_FIT_H;y++) {
        int a=y*114,b=a+114;fit_y0[y]=a/71;
        for(int k=0;k<3;k++) {
            int top=(fit_y0[y]+k)*71,bottom=top+71;
            fit_yw[y][k]=vp_clamp((b<bottom?b:bottom)-(a>top?a:top),0,71);
        }
    }
    for(int i=0;i<=912;i++){int v=(i*31+456)/912;fit_rgb[i]=(uint16_t)((v<<11)|(((v*63+15)/31)<<5)|v);}
}
static unsigned fit_coverage(const uint8_t* fb,int x,int y) {
    unsigned value=0;
    for(int ky=0;ky<3;ky++) {
        unsigned wy=fit_yw[y][ky];if(!wy)continue;
        const uint8_t* row=fb+(fit_y0[y]+ky)*64;
        for(int kx=0;kx<3;kx++) {
            unsigned wx=fit_xw[x][kx];if(!wx)continue;
            unsigned sx=fit_x0[x]+kx;
            if(row[sx/8]&(128>>(sx&7)))value+=wx*wy;
        }
    }
    return value;
}
static void fit_line(int y) {
    fit_init();const uint8_t* fb=ram+umac_get_fb_offset();y-=VP_FIT_Y;
    for(int x=0;x<320;x++) {
        uint16_t rgb=fit_rgb[fit_coverage(fb,x,y)];
        line[x*2]=(uint8_t)(rgb>>8);line[x*2+1]=(uint8_t)rgb;
    }
}
static void view_change(int x,int y) {
    int nx=vp_origin_x(x),ny=vp_origin_y(y);
    if(nx!=view_x || ny!=view_y){view_x=nx;view_y=ny;view_revision++;}
}
#include "profiles.inc"
static void vp_pixel(int x,int y,int black) {
    if(x<0 || x>=320 || y<0 || y>=240)return;
    uint8_t mask=128>>(x&7);uint8_t* p=&viewport_pixels[y*40+(x>>3)];
    if(black)*p|=mask;else *p&=(uint8_t)~mask;
}
static void vp_text(int x,int y,const char* text,int black) {
    for(;*text;text++) {
        unsigned c=(unsigned char)*text;if(c<32 || c>126)continue;c-=32;
        for(int yy=0;yy<13;yy++)for(int xx=0;xx<vp_width[c];xx++)
            if(vp_font[c][yy*2+xx/8]&(128>>(xx&7)))vp_pixel(x+xx,y+yy,black);
        x+=vp_width[c];
    }
}
/* Solid pixel arrows, independent of the text font's ^/v glyph shapes. */
static void vp_arrow(int cx,int cy,int direction) {
    for(int y=-5;y<=4;y++)for(int x=-4;x<=4;x++) {
        if(abs(x)>(y<0?y+5:1))continue;
        int dx=x,dy=y;
        if(direction==0){dx=y;dy=x;}       /* left */
        else if(direction==1){dx=-y;dy=x;}/* right */
        else if(direction==3){dx=x;dy=-y;}/* down; 2 is up */
        vp_pixel(cx+dx,cy+dy,1);
    }
}
static void render_viewport(void) {
    const uint8_t* fb=ram+umac_get_fb_offset();
    memset(viewport_pixels,0,sizeof(viewport_pixels));
    if(!view_fit) {
        for(int y=0;y<VP_CONTENT_H;y++)
            memcpy(viewport_pixels+y*40,fb+(view_y+y)*64+view_x/8,40);
    } else {
        for(int y=0;y<VP_FIT_H;y++) {
            const uint8_t* src=fb+vp_guest_y(y+VP_FIT_Y,1,0)*64;
            for(int x=0;x<320;x++) {
                int sx=vp_guest_x(x,1,0);
                if(src[sx/8]&(128>>(sx&7)))vp_pixel(x,y+VP_FIT_Y,1);
            }
        }
    }
    memset(viewport_pixels+VP_CONTENT_H*40,255,40);
    for(int k=0;k<8;k++)for(int y=VP_CONTENT_H;y<240;y++)vp_pixel(view_edges[k],y,1);
    const char* labels[]={view_fit?"1x":"Fit","Pan","","","","","Top"};
    for(int k=0;k<7;k++) {
        int active=k==1 && view_pan;
        if(active)for(int y=VP_CONTENT_H+1;y<240;y++)for(int x=view_edges[k]+1;x<view_edges[k+1];x++)vp_pixel(x,y,1);
        if(k>=2 && k<=5){vp_arrow((view_edges[k]+view_edges[k+1])/2,VP_CONTENT_H+9,k-2);continue;}
        int width=0;for(const char* p=labels[k];*p;p++)width+=vp_width[(unsigned char)*p-32];
        vp_text((view_edges[k]+view_edges[k+1]-width)/2,VP_CONTENT_H+2,labels[k],!active);
    }
    char info[24];
    char kind=view_profile_index>=0 && view_profiles[view_profile_index].manual?'M':'A';
    if(view_fit)snprintf(info,sizeof(info),"%c Full",kind);else snprintf(info,sizeof(info),"%c %d,%d",kind,view_x,view_y);
    vp_text(247,VP_CONTENT_H+2,info,1);
}
static void display_frame(bool force) {
    view_profile_poll();
    static unsigned previous_revision;
    force=force || previous_revision!=view_revision;previous_revision=view_revision;
    render_viewport();spi_set_baudrate(spi1,40000000);
    for(int y=0;y<240;y++) {
        const uint8_t* src=viewport_pixels+y*40;uint32_t hash=2166136261u;
        int smooth=view_fit && y>=VP_FIT_Y && y<VP_FIT_Y+VP_FIT_H;
        if(smooth){fit_line(y);for(int i=0;i<640;i++)hash=(hash^line[i])*16777619u;}
        else for(int i=0;i<40;i++)hash=(hash^src[i])*16777619u;
        if(!force && hash==hashes[y])continue;hashes[y]=hash;
        if(!smooth)for(int x=0;x<320;x++) {
            uint8_t v=(src[x/8]&(128>>(x&7)))?255:0;
            line[x*2]=v;line[x*2+1]=v;
        }
        const uint8_t cols[]={0,0,1,63},rows[]={0,(uint8_t)y,0,(uint8_t)y};
        command(0x2a,cols,4);command(0x2b,rows,4);
        uint8_t cmd=0x2c;gpio_put(LCD_DC,0);gpio_put(LCD_CS,0);spi_write_blocking(spi1,&cmd,1);
        gpio_put(LCD_DC,1);spi_write_blocking(spi1,line,sizeof(line));gpio_put(LCD_CS,1);framebuffer_updates++;
    }
}
static void view_action(int button) {
    physical_down=0;synthetic_tap=0;
    if(button==0) {
        if(view_fit){view_change(target_x-160,target_y-VP_CONTENT_H/2);view_fit=0;}
        else {view_fit=1;view_pan=0;}
    } else if(button==1) {view_fit=0;view_pan=!view_pan;}
    else if(button==2){view_fit=0;view_change(view_x-64,view_y);}
    else if(button==3){view_fit=0;view_change(view_x+64,view_y);}
    else if(button==4){view_fit=0;view_change(view_x,view_y-48);}
    else if(button==5){view_fit=0;view_change(view_x,view_y+48);}
    else if(button==6){view_fit=0;view_pan=0;view_change(0,0);}
    if(button==7)view_profile_auto();else view_profile_remember(1);
    view_revision++;
}
static void viewport_touch(int sx,int sy,int down) {
    if(!down){physical_down=0;view_touch_owner=0;return;}
    sx=vp_clamp(sx,0,319);sy=vp_clamp(sy,0,239);
    if(!view_touch_owner) {
        if(sy>=VP_CONTENT_H) {
            view_touch_owner=2;
            for(int i=0;i<8;i++)if(sx>=view_edges[i] && sx<view_edges[i+1]){view_action(i);break;}
            return;
        }
        if(view_pan) {
            view_touch_owner=3;view_start_x=sx;view_start_y=sy;view_drag_x=view_x;view_drag_y=view_y;
            physical_down=0;return;
        }
        if(view_fit && (sy<VP_FIT_Y || sy>=VP_FIT_Y+VP_FIT_H)){view_touch_owner=2;return;}
        view_touch_owner=1;synthetic_tap=0;request_id++;
    }
    if(view_touch_owner==3){view_change(view_drag_x+view_start_x-sx,view_drag_y+view_start_y-sy);view_profile_remember(1);return;}
    if(view_touch_owner!=1)return;
    target_x=vp_guest_x(sx,view_fit,view_x);target_y=vp_guest_y(sy,view_fit,view_y);physical_down=1;
}
static void viewport_report(void) {
    printf("VIEW guest=512x342 lcd=320x240 content=320x222 mode=%s origin=%d,%d pan=%d app=%s preference=%s\n",view_fit?"fit":"1x",view_x,view_y,view_pan,
           view_profile_index>=0?view_profiles[view_profile_index].name:"startup",
           view_profile_index>=0 && view_profiles[view_profile_index].manual?"manual":"auto");
}
static void viewport_command(const char* value) {
    int x,y;
    if(!strcmp(value,"auto")){view_profile_auto();viewport_report();return;}
    if(!strcmp(value,"fit")){view_fit=1;view_pan=0;}
    else if(!strcmp(value,"1x")){if(view_fit)view_change(target_x-160,target_y-VP_CONTENT_H/2);view_fit=0;view_pan=0;}
    else if(!strcmp(value,"top")){view_action(6);}
    else if(!strcmp(value,"pan")){view_action(1);}
    else if(sscanf(value,"%d %d",&x,&y)==2){view_fit=0;view_pan=0;view_change(x,y);}
    view_profile_remember(1);view_revision++;viewport_report();
}
static void viewport_gray_snapshot(int row);
static void viewport_snapshot(int row) {
    if(view_fit){viewport_gray_snapshot(row);return;}
    pause_request=true;uint64_t deadline=time_us_64()+1000000;
    while(!paused && time_us_64()<deadline)tight_loop_contents();
    if(!paused){pause_request=false;printf("SCREEN_NOT_READY\n");return;}
    render_viewport();printf("FRAME_HEX 320 240\n");stdio_flush();
    int first=row>=0?row:0,last=row>=0?row:239;
    for(int y=first;y<=last && y<240;y++) {
        const uint8_t* src=viewport_pixels+y*40;char record[128];int used=sprintf(record,"%03d:",y);uint32_t hash=2166136261u;
        for(int i=0;i<40;i++){hash=(hash^src[i])*16777619u;used+=sprintf(record+used,"%02x",src[i]);}
        used+=sprintf(record+used,":%08lx\n",(unsigned long)hash);fwrite(record,1,used,stdout);stdio_flush();sleep_ms(2);
    }
    printf("FRAME_END\n");stdio_flush();pause_request=false;
}
static void viewport_gray_snapshot(int row) {
    pause_request=true;uint64_t deadline=time_us_64()+1000000;
    while(!paused && time_us_64()<deadline)tight_loop_contents();
    if(!paused){pause_request=false;printf("SCREEN_NOT_READY\n");return;}
    render_viewport();printf("FRAME_GRAY 320 240\n");stdio_flush();
    int first=row>=0?row:0,last=row>=0?row:239;
    for(int y=first;y<=last && y<240;y++) {
        int smooth=y>=VP_FIT_Y && y<VP_FIT_Y+VP_FIT_H;
        if(smooth)fit_line(y);
        char record[704];int used=sprintf(record,"%03d:",y);uint32_t hash=2166136261u;
        for(int x=0;x<320;x++) {
            unsigned value=smooth?255-((line[x*2+1]&31)*255+15)/31:
                (viewport_pixels[y*40+x/8]&(128>>(x&7)))?0:255;
            hash=(hash^(uint8_t)value)*16777619u;used+=sprintf(record+used,"%02x",value);
        }
        used+=sprintf(record+used,":%08lx\n",(unsigned long)hash);
        fwrite(record,1,used,stdout);stdio_flush();sleep_ms(2);
    }
    printf("FRAME_END\n");stdio_flush();pause_request=false;
}
