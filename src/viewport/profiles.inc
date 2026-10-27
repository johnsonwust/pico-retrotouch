// SPDX-License-Identifier: GPL-3.0-or-later
/* View preferences are host-only: never change Macintosh RAM or window resources.
 * CurApName (Pascal string at 0x910) was checked against real Finder + 7 app dumps.
 * Two matching reads plus an idle touch are required before changing views.
 * Manual preferences are remembered for this power-on session. */
#define VP_PROFILE_MAX 16
typedef struct {char name[32];int fit,x,y,manual;} ViewProfile;
static ViewProfile view_profiles[VP_PROFILE_MAX];
static int view_profile_count,view_profile_index=-1,view_candidate_count;
static char view_candidate[32];
static int view_read_name(char name[32]) {
    unsigned n=((volatile uint8_t*)ram)[0x910];
    if(!n || n>31)return 0;
    for(unsigned i=0;i<n;i++) {
        unsigned c=((volatile uint8_t*)ram)[0x911+i];
        if(c<32 || c>126)return 0;
        name[i]=(char)c;
    }
    name[n]=0;
    return ((volatile uint8_t*)ram)[0x910]==n;
}
static int view_default_fit(const char* name) {
    static const char* full[]={"MissileCommand","Daleks","Bubba","Break Bricks","BlackBox","Blackjack","Brickles 5.0"};
    for(unsigned i=0;i<sizeof(full)/sizeof(full[0]);i++)if(!strcmp(name,full[i]))return 1;
    return 0; /* Finder, its desk accessories, and as-yet unknown applications. */
}
static void view_profile_remember(int manual) {
    if(view_profile_index<0)return;
    ViewProfile* p=&view_profiles[view_profile_index];
    p->fit=view_fit;p->x=view_x;p->y=view_y;
    if(manual)p->manual=1;
}
static void view_profile_auto(void) {
    if(view_profile_index<0)return;
    ViewProfile* p=&view_profiles[view_profile_index];
    p->manual=0;p->fit=view_default_fit(p->name);p->x=p->y=0;
    view_fit=p->fit;view_pan=0;view_change(0,0);view_revision++;
}
static void view_profile_poll(void) {
    char name[32],confirm[32];
    if(!view_read_name(name) || !view_read_name(confirm) || strcmp(name,confirm))return;
    if(strcmp(view_candidate,name)){strcpy(view_candidate,name);view_candidate_count=1;return;}
    if(view_candidate_count<8){view_candidate_count++;return;}
    if(physical_down || synthetic_tap || view_touch_owner)return;
    if(view_profile_index>=0 && !strcmp(view_profiles[view_profile_index].name,name))return;
    view_profile_remember(0);
    int index=0;
    for(;index<view_profile_count;index++)if(!strcmp(view_profiles[index].name,name))break;
    if(index==view_profile_count) {
        /* Keep established profiles when the bounded table is full. */
        if(view_profile_count==VP_PROFILE_MAX)return;
        ViewProfile* p=&view_profiles[view_profile_count++];
        strcpy(p->name,name);p->fit=view_default_fit(name);
        p->x=p->y=p->manual=0;
    }
    view_profile_index=index;
    ViewProfile* p=&view_profiles[index];
    view_fit=p->fit;view_pan=0;view_change(p->x,p->y);view_revision++;
    printf("VIEW_APP name=%s mode=%s preference=%s origin=%d,%d\n",p->name,
           view_fit?"fit":"1x",p->manual?"manual":"auto",view_x,view_y);
}
