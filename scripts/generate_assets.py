"""MIT font conversion + original terminal artwork; no system fonts required."""
# SPDX-License-Identifier: MIT
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def generate():
    source=(ROOT/'assets/font_petme128_8x8.h').read_text()
    notice=source[:source.index(' */')+3]
    body=source.split('static const uint8_t font_petme128_8x8[] = {',1)[1].split('};',1)[0]
    values=bytes(int(v,16) for v in re.findall(r'0x([0-9a-fA-F]{2})',body))
    assert len(values)==96*8
    rows=[]
    for c in range(95):
        cols=values[c*8:c*8+8]
        rows.append(bytes([0,0]+[sum(((cols[x]>>y)&1)<<(7-x) for x in range(8)) for y in range(8)]+[0,0,0]))
    target=ROOT/'build/generated';target.mkdir(parents=True,exist_ok=True)
    width=[4]+[8]*94
    glyphs=[b''.join(bytes([b,0]) for b in r) for r in rows]
    s=notice+'\n// Transposed MIT MicroPython font; 13px line box.\n'
    s+='static const uint8_t vp_font[95][26]={\n'+',\n'.join('{'+','.join(map(str,g))+'}' for g in glyphs)+'\n};\n'
    s+='static const uint8_t vp_width[95]={'+','.join(map(str,width))+'};\n'
    (target/'font.h').write_text(s)
    py='# Font data adapted from MicroPython font_petme128_8x8.h (MIT).\n'
    py+='# Copyright (c) 2013, 2014 Damien P. George. See LICENSES/Font-MicroPython-MIT.txt.\n'
    py+='GLYPHS='+repr(tuple(r+b'\0' for r in rows))+'\n'
    py+='def get_ch(ch):\n    n=ord(ch)\n    return (GLYPHS[n-32],13,4 if n==32 else 8) if 32<=n<=126 else (None,13,8)\n'
    (ROOT/'src/mactouch/retro_font.py').write_text(py)
    hero=bytearray(230*86)
    def pixel(x,y):
        if 0<=x<230 and 0<=y<86:hero[y*230+x]=255
    def line(x0,y0,x1,y1):
        n=max(abs(x1-x0),abs(y1-y0))
        for i in range(n+1):pixel(x0+(x1-x0)*i//max(n,1),y0+(y1-y0)*i//max(n,1))
    # Independent terminal icon with prompt; no Apple/Finder/Happy Mac graphic.
    for off in [0,1]:
        for a,b,c,d in [(5,15,61,15),(5,15,5,68),(61,15,61,68),(5,68,61,68),(5,27,61,27),
                        (17,38,27,47),(27,47,17,56),(34,56,49,56)]:line(a,b+off,c,d+off)
    for i,ch in enumerate('ready.'):
        for y,b in enumerate(rows[ord(ch)-32][2:10]):
            for x in range(8):
                if b&(128>>x):
                    for yy in range(3):
                        for xx in range(3):pixel(78+i*24+x*3+xx,29+y*3+yy)
    data=[];descs=['{.bitmap_index=0,.adv_w=0,.box_w=0,.box_h=0,.ofs_x=0,.ofs_y=0},']
    for r,w in zip(rows,width):
        offset=len(data)
        bits=[(b>>(7-x))&1 for b in r for x in range(w)]
        for i in range(0,len(bits),8):data.append(sum(v<<(7-j) for j,v in enumerate(bits[i:i+8])))
        descs.append('{.bitmap_index=%d,.adv_w=%d,.box_w=%d,.box_h=13,.ofs_x=0,.ofs_y=0},'%(offset,w*16,w))
    text=notice+'\n#pragma once\n'
    text+='static const uint8_t welcome_hero_data[]={'+','.join(map(str,hero))+'};\n'
    text+='static const lv_image_dsc_t welcome_hero={.header={.magic=LV_IMAGE_HEADER_MAGIC,.cf=LV_COLOR_FORMAT_A8,.flags=0,.w=230,.h=86,.stride=230},.data_size=sizeof(welcome_hero_data),.data=welcome_hero_data};\n'
    text+='static const uint8_t welcome_font_bitmap[]={'+','.join(map(str,data))+'};\n'
    text+='static const lv_font_fmt_txt_glyph_dsc_t welcome_font_glyphs[]={'+''.join(descs)+'};\n'
    text+='static const lv_font_fmt_txt_cmap_t welcome_font_cmap[]={ {.range_start=32,.range_length=95,.glyph_id_start=1,.unicode_list=nullptr,.glyph_id_ofs_list=nullptr,.list_length=0,.type=LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY} };\n'
    text+='static const lv_font_fmt_txt_dsc_t welcome_font_dsc={.glyph_bitmap=welcome_font_bitmap,.glyph_dsc=welcome_font_glyphs,.cmaps=welcome_font_cmap,.kern_dsc=nullptr,.kern_scale=0,.cmap_num=1,.bpp=1,.kern_classes=0,.bitmap_format=0};\n'
    text+='static const lv_font_t welcome_font={.get_glyph_dsc=lv_font_get_glyph_dsc_fmt_txt,.get_glyph_bitmap=lv_font_get_bitmap_fmt_txt,.line_height=13,.base_line=0,.subpx=LV_FONT_SUBPX_NONE,.underline_position=0,.underline_thickness=1,.dsc=&welcome_font_dsc};\n'
    boot=ROOT/'external/PicoBoot/src/ui/lvgl'
    if boot.is_dir():(boot/'welcome_assets.h').write_text(text)
    (target/'welcome_assets.h').write_text(text)
    # PGM lets maintainers inspect the generated original artwork without a GUI dependency.
    (target/'welcome.pgm').write_bytes(b'P5\n230 86\n255\n'+hero)
    print('GENERATED_OPEN_FONT_AND_ORIGINAL_ARTWORK')
if __name__=='__main__':generate()
