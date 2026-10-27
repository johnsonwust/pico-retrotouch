// SPDX-License-Identifier: GPL-3.0-or-later
/* Read-only guest state, collected with the emulation core paused. */
static void diagnostics(void) {
    if(!ready) { printf("EMULATOR_NOT_READY\n");return; }
    pause_request=true;
    uint64_t deadline=time_us_64()+1000000;
    while(!paused && time_us_64()<deadline)tight_loop_contents();
    if(!paused) { pause_request=false;printf("DIAG_PAUSE_TIMEOUT\n");return; }
    printf("DIAG version=0.3.2 DSErrCode=%d MemErr=%d MemTop=%08lx BufPtr=%08lx\n",
           (int16_t)RAM_RD16(0xaf0),(int16_t)RAM_RD16(0x220),
           (unsigned long)RAM_RD32(0x108),(unsigned long)RAM_RD32(0x10c));
    printf("DIAG PC=%08lx SR=%04lx SP=%08lx SysZone=%08lx ApplZone=%08lx\n",
           (unsigned long)m68k_get_reg(NULL,M68K_REG_PC),
           (unsigned long)m68k_get_reg(NULL,M68K_REG_SR),
           (unsigned long)m68k_get_reg(NULL,M68K_REG_SP),
           (unsigned long)RAM_RD32(0x2a6),(unsigned long)RAM_RD32(0x2aa));
    for(int i=0;i<8;i++)printf("DIAG D%d=%08lx A%d=%08lx\n",i,
           (unsigned long)m68k_get_reg(NULL,M68K_REG_D0+i),i,
           (unsigned long)m68k_get_reg(NULL,M68K_REG_A0+i));
    unsigned sp=m68k_get_reg(NULL,M68K_REG_SP);
    if(sp<RAM_SIZE-64) {
        printf("DIAG STACK %08x",sp);
        for(unsigned i=0;i<32;i+=2)printf(" %04x",RAM_RD16(sp+i));
        printf("\n");
    }
    printf("DIAG_END\n");stdio_flush();pause_request=false;
}
