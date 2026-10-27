# License map

This repository is a collection of separately licensed source components. No single MIT license overrides third-party terms.

| Files | Terms |
|---|---|
| Original `src/mactouch/`, `src/bootstrap/`, Python utility scripts except `patch_rom.c`, original terminal artwork and documentation | MIT, `LICENSES/Project-MIT.txt`; retain applicable notices below |
| `src/native/main_spi.c`, `src/native/diagnostics.inc`, original `src/viewport/`, `tests/test_viewport.c`, `scripts/patch_rom.c` | Original project contributions offered under GPL-3.0-or-later, `LICENSES/GPL-3.0-or-later.txt` |
| `src/native/sd_hw_config.c` | Apache-2.0, adapted from the SD driver; `LICENSES/SD-Apache-2.0.txt` |
| `patches/picoboot.patch`, `patches/toolset.patch` | Original changes MIT; preserve PicoBoot/Pico-Toolset upstream notices |
| `patches/micropython-layout.patch`, `patches/pico-fatfs-crc.patch` | Original changes MIT; retain upstream per-file terms |
| `assets/font_petme128_8x8.h`, derived `retro_font.py` and locally generated bitmap font headers | MicroPython MIT, Damien P. George; `LICENSES/Font-MicroPython-MIT.txt` |
| Display initialization and modified MicroPython SD driver | MIT-derived code; see `LICENSES/ST7789-MIT.txt`, `LICENSES/MicroPython-lib.txt`, and `THIRD_PARTY_NOTICES.md` |

Upstream source is fetched separately at revisions in `upstreams.lock.json`. Preserve **each upstream file's own notices**. umac contains MIT code and a Basilisk II-derived **GPL-2.0-or-later** disk driver. Some SDL keyboard mapping headers are **GPLv2**. The native RP2040 target does not build the SDL frontend. Musashi includes SoftFloat 2b with its own retained notice, and the SD dependency includes Apache-2.0 and other per-file terms.

The GPL-3.0-or-later offer above applies to this project's original native contributions; it does not relicense upstream files, certify every possible dependency combination, or grant rights in Apple software. Public **binary** distribution needs a review of the actual linked sources, compatible license versions, complete corresponding source/build scripts and all embedded software. This source-only snapshot does not supply a binary release or proprietary input files.

MIT terms permit commercial use under their conditions. GPL terms also permit commercial use under their conditions; do not add a blanket “noncommercial only” restriction to GPL-derived work.

The MIT notices and GPL warranty disclaimers apply as written. They are not permission to redistribute third-party ROMs, system disks, fonts or games.

## Documentary screenshots

The approved PNG files under `docs/screenshots/` are real-device documentary captures, not ROMs or application distributions. They show the private prototype running separately supplied software. Third-party interface, font, trademark and game artwork remains with its respective owners; the source-code licenses above do not grant rights in that displayed material. This project makes no blanket open-source licensing claim over third-party pixels. See `docs/screenshots/captures.json` and the gallery captions for provenance and scope.
