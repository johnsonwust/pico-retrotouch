cmake_minimum_required(VERSION 3.20)
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(PICO_BOARD pico CACHE STRING "Board")
set(PICO_NO_PICOTOOL 1)
set(PICO_SDK_PATH "${ROOT}/external/pico-sdk")
include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
project(picomac_dualboot C CXX ASM)
pico_sdk_init()
set(FF_DISABLE_RTC TRUE)
add_subdirectory(${ROOT}/external/sd-spi/FatFs_SPI fatfs)
set(UMAC "${ROOT}/external/umac")
set(MUS "${UMAC}/external/Musashi")
add_executable(picomac_dualboot main_spi.c sd_hw_config.c
    ${UMAC}/src/main.c ${UMAC}/src/rom.c ${UMAC}/src/disc.c ${UMAC}/src/via.c ${UMAC}/src/scc.c
    ${MUS}/m68kcpu.c ${MUS}/m68kdasm.c ${MUS}/m68kops.c ${MUS}/softfloat/softfloat.c)
target_include_directories(picomac_dualboot PRIVATE "${UMAC}/include" "${MUS}"
    "${ROOT}/build/generated" "${ROOT}/src/viewport")
target_compile_definitions(picomac_dualboot PRIVATE PICO=1 UMAC_MEMSIZE=192 DISP_WIDTH=512 DISP_HEIGHT=342
    BYTE_ORDER=1234 LITTLE_ENDIAN=1234 PICO_STDIO_USB_DEFAULT_CRLF=0 PICO_MALLOC_PANIC=0
    MUSASHI_CNF="../include/m68kconf.h" PICO_STACK_SIZE=0x1000 PICO_CORE1_STACK_SIZE=0x1000)
target_compile_options(picomac_dualboot PRIVATE -O3)
target_link_libraries(picomac_dualboot pico_stdlib pico_multicore hardware_spi hardware_clocks pico_bootrom FatFs_SPI)
pico_enable_stdio_uart(picomac_dualboot 0)
pico_enable_stdio_usb(picomac_dualboot 1)
include(${ROOT}/external/PicoBoot/cmake/picoboot_app_linker.cmake)
picoboot_set_app_flash_region(picomac_dualboot 2097152)
pico_add_extra_outputs(picomac_dualboot)
