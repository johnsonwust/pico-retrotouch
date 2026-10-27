// SPDX-License-Identifier: GPL-3.0-or-later
/* Display and touch share these exact viewport transforms. No guest state here. */
#pragma once
#define VP_LCD_W 320
#define VP_LCD_H 240
#define VP_TOOL_H 18
#define VP_CONTENT_H (VP_LCD_H-VP_TOOL_H)
#define VP_GUEST_W 512
#define VP_GUEST_H 342
#define VP_FIT_H (VP_GUEST_H*VP_LCD_W/VP_GUEST_W)
#define VP_FIT_Y ((VP_CONTENT_H-VP_FIT_H)/2)
static inline int vp_clamp(int x,int lo,int hi){return x<lo?lo:x>hi?hi:x;}
static inline int vp_origin_x(int x){return vp_clamp(x,0,VP_GUEST_W-VP_LCD_W)&~7;}
static inline int vp_origin_y(int y){return vp_clamp(y,0,VP_GUEST_H-VP_CONTENT_H);}
static inline int vp_guest_x(int sx,int fit,int x){return fit?vp_clamp(sx*511/319,0,511):x+vp_clamp(sx,0,319);}
static inline int vp_guest_y(int sy,int fit,int y){return fit?vp_clamp((sy-VP_FIT_Y)*341/(VP_FIT_H-1),0,341):y+vp_clamp(sy,0,VP_CONTENT_H-1);}
