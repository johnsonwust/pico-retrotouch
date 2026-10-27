# RP2040 Pico + Waveshare Pico-ResTouch-LCD-2.8

Consumer: Pico RetroTouch source build, adapted PicoBoot. Display, SD mount,
SD-based application loading and return-to-menu tested on the physical
RP2040/16 GB FAT32 combination on 2026-10-27. Stylus menu confirmation is
tracked separately in the consumer's verification record. The same panel's
pressure/calibration path was previously confirmed in PicoMacintosh.

Use `kWavesharePicoResTouch28` from the ST7789, XPT2046 and SD config headers.
All devices share SPI1 (SCK10/MOSI11/MISO12): LCD CS9/DC8/RST15/BL13,
touch CS16/IRQ17, SD CS22. Deselect all three devices before SD init.

Pixel clock is 40 MHz, ADC 1 MHz, SD 5 MHz. Restore the SD clock after every
display/touch transaction before pumping USB MSC or accessing FatFs.
The RP2040 application partition begins at 0x10080000; the consumer reserves
the final 512 KiB of 2 MiB Flash for MicroPython LittleFS.

Measured panel calibration in the consumer is affine. Its menu adapter uses
the corresponding swapped-axis ranges: horizontal 4000 to 375 (inverted),
vertical 228 to 3896. These are panel-specific values, not a universal preset.

Consumer build: `python DualBoot/build.py menu` with the portable local SDK
and toolchain. It reuses the CrowPanel target, selecting the named ResTouch
presets. See the consumer README for build and hardware verification logs.
