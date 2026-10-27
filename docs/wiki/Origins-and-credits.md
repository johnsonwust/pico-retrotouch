# Origins and credits

[Documentation home](Home.md) · [License map](../../LICENSE.md) · [Full third-party notices](../../THIRD_PARTY_NOTICES.md)

## How the project developed

The starting point was **Simon Boak's Picontosh** and [his illustrated article from 30 November 2024](https://unimplementedtrap.com/picontosh-exploring-classic-macintosh-icon-format/): a Pico project that presents an early Macintosh-inspired display. Our hardware follows its Pico/Waveshare/SD approach. That working display setup led to a touch-controlled miniature desktop, followed by a separate native emulator environment.

The emulator work builds on **Matt Evans' umac** and its Musashi 68000 core. This project adapts that foundation for the Waveshare SPI display, resistive touch input and SD storage. **PicoBoot / Pico-Toolset** provide the basis for selecting the two firmware environments at startup.

The touch desktop and the emulator are distinct parts of the project. The former contains new miniature applications; the latter relies on upstream emulation and separately supplied guest software. Neither the original Macintosh system nor the demonstrated classic games are authored or distributed by this repository.

## Main references

| Project / author | Role in this project |
|---|---|
| [Picontosh — Simon Boak](https://github.com/simonboak/Picontosh), [illustrated hardware/project article](https://unimplementedtrap.com/picontosh-exploring-classic-macintosh-icon-format/) | Original inspiration and first working Pico/display setup; photos remain at their source |
| [umac — Matt Evans](https://github.com/evansm7/umac) | Minimal early Macintosh emulation foundation |
| [Musashi — Karl Stenerud and contributors; Evans fork](https://github.com/evansm7/Musashi) | Motorola 68000 CPU emulation |
| Basilisk II — Christian Bauer | Disk-driver source lineage retained inside umac; GPL notices apply |
| [PicoBoot](https://github.com/lohengrin/PicoBoot) / [Pico-Toolset](https://github.com/lohengrin/Pico-Toolset) — Lohengrin | SD firmware selection, menu and board integration framework |
| [MicroPython — Damien P. George and contributors](https://github.com/micropython/micropython) | Touch-desktop runtime and explicitly MIT-licensed PETME 8×8 font |
| [MicroPython-lib](https://github.com/micropython/micropython-lib) | SPI SD driver lineage |
| [Pico SDK — Raspberry Pi and contributors](https://github.com/raspberrypi/pico-sdk) | RP2040 platform support |
| [LVGL](https://github.com/lvgl/lvgl) | Boot-menu UI framework |
| [Native SD/FatFs driver](https://github.com/evansm7/no-OS-FatFS-SD-SPI-RPi-Pico) / [boot-menu pico_fatfs](https://github.com/elehobica/pico_fatfs) | Storage foundations; original authors' notices retained |
| Peter Hinch / Ihor Nehrutsa, ST7789 reference code | Display initialization lineage via Picontosh / nano-gui |
| [Waveshare board wiki](https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8) | Manufacturer's pin mapping, controller documentation and examples |

Exact fetched revisions are recorded in [upstreams.lock.json](../../upstreams.lock.json). Consult the [notice table](../../THIRD_PARTY_NOTICES.md) and full texts under `LICENSES/` for attribution and terms; this short overview does not replace them.

## Contributions in this repository

- A MicroPython monochrome desktop with drawing, zoom navigation, SD gallery, notes, original story content and small touch games.
- Shared-SPI integration for the LCD, touch controller and SD card, including command CRC and storage handling.
- Pressure-filtered, calibrated touch input and stylus-to-guest mouse mapping.
- Protected flash partition integration for two selectable environments.
- A 512×342 guest viewport with area-filtered Fit, crisp 1x, Pan, solid arrow controls and application preferences.
- Build/staging tools, diagnostics, capture verification and documentation.

These contributions do not imply ownership of upstream emulators, Apple software or third-party game artwork.

## Historical appearance and the public source

The documentary screenshots retain the prototype's actual historical-style font and smile/`hello.` screen. The public source uses an **original terminal illustration** and the **MIT MicroPython font** instead. Original-size captures and their provenance are listed in the [gallery](../SCREENSHOTS.md).

The replacement artwork/font path has clean build checks but still needs physical validation. Source licenses do not relicense third-party interfaces or game pixels shown in screenshots. [Verification scope](../VERIFICATION.md).

## Future kits

The planned unassembled Tindie kit is described in [KIT.md](../KIT.md): US$69 with estimated US$20 shipping. Purchase links, a final packing list and a contact channel will be added with the live listing. Any future distribution must follow the relevant component licenses and separately address rights in embedded or bundled software. The current repository remains a source-only DIY project with no included ROM, system or game collection.
