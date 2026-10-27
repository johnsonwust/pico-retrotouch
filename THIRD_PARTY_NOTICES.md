# Third-party notices and provenance

| Component | Origin / authors | License notes |
|---|---|---|
| Picontosh inspiration and first working display setup | https://github.com/simonboak/Picontosh — Simon Boak; [illustrated project/hardware article](https://unimplementedtrap.com/picontosh-exploring-classic-macintosh-icon-format/) | MIT source notice retained. Blog photos are not bundled. The Chicago font from the private prototype is **not** included. |
| ST7789 reference setup | Peter Hinch, Ihor Nehrutsa; Picontosh's `st7789.py`, originally nano-gui | MIT notice in `LICENSES/ST7789-MIT.txt`. Public `macdisplay.py` is a small monochrome driver using this reference setup. |
| MicroPython / SPI SD driver | https://github.com/micropython/micropython and https://github.com/micropython/micropython-lib | MIT and per-module. Local `sdcard_crc.py` adds command CRC, shared-bus and write-wait handling. |
| PETME 8×8 font | MicroPython `extmod/font_petme128_8x8.h` — Copyright 2013, 2014 Damien P. George | Complete MIT header preserved in source asset and font license. Conversion transposes columns to rows; no Apple/Chicago or Windows font is shipped. |
| umac | https://github.com/evansm7/umac — Matt Evans | Core files carry MIT notices; `src/disc.c` contains Basilisk II's sony.cpp under GPL-2.0-or-later. |
| Basilisk II driver | Christian Bauer, 1997–2008 | GPL-2.0-or-later, notice remains inside fetched `umac/src/disc.c`. |
| Musashi | https://github.com/evansm7/Musashi — Karl Stenerud and contributors | MIT-style notice plus separate SoftFloat terms. Fetched at a fixed source revision. |
| SoftFloat 2b | John R. Hauser / ICSI | Retain its complete original notice and derivative-work identification, included as `LICENSES/SoftFloat-2b.txt`. Native binary compliance remains a separate review item. |
| PicoBoot / Pico-Toolset | https://github.com/lohengrin/PicoBoot and https://github.com/lohengrin/Pico-Toolset | MIT and per-file source lineage. Patches add this board's pins, pressure filtering, SD/shared-SPI and protected flash regions. |
| Pico SDK | https://github.com/raspberrypi/pico-sdk — Raspberry Pi and contributors | BSD-3-Clause and bundled per-file dependencies. |
| Native SD SPI / FatFs | https://github.com/evansm7/no-OS-FatFS-SD-SPI-RPi-Pico | Apache-2.0 and per-file notices; `sd_hw_config.c` is a board adaptation. FatFs retains ChaN's notices. |
| Boot-menu SD / FatFs | https://github.com/elehobica/pico_fatfs | Per-file notices retained in fetched source; patch only changes command CRC handling. |
| LVGL | https://github.com/lvgl/lvgl — LVGL contributors | MIT; any built-in font has its own retained source notices. The custom welcome font uses MicroPython's MIT font. |

See `upstreams.lock.json` for exact commits. Build-time fetching does not replace the obligation to retain the upstream license files if redistributing those sources or binaries.

Project additions include the monochrome MicroPython desktop, pressure-calibrated stylus path, shared-SPI integration, preserved flash partitioning, 512×342 guest viewport, area-filtered Fit, 1x/Pan controls, per-application preferences and the solid arrow toolbar. They are not claims of authorship over the original emulator or original Macintosh applications.
