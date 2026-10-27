# Pico RetroTouch

**A tiny touch desktop and early Macintosh emulation, on one Raspberry Pi Pico.**

[Assembly & first boot](docs/QUICKSTART.md) · [Documentation](docs/wiki/Home.md) · [Screenshot gallery](docs/SCREENSHOTS.md) · [Hardware](docs/HARDWARE.md) · [Credits](docs/wiki/Origins-and-credits.md)

Pico RetroTouch pairs an RP2040 Pico with a Waveshare 2.8-inch SPI touchscreen and microSD storage. Choose a lightweight creative desktop or an early Macintosh environment at startup, then use the stylus to draw, write, explore and play.

This independent hobby project is shared as **source code**. It builds on Picontosh, umac, Musashi, PicoBoot and other open-source work; see [origins and credits](docs/wiki/Origins-and-credits.md).

The hardware approach follows [Simon Boak's original Picontosh article](https://unimplementedtrap.com/picontosh-exploring-classic-macintosh-icon-format/): a Pico, a small Waveshare display, SD storage and a compact retro enclosure. This project extends that starting point with touch applications and a separate emulator environment.

## Start with a small hello

| Choose an environment | Open the touch desktop |
|---|---|
| ![Physical prototype boot menu with smile, hello and two environment buttons](docs/screenshots/boot-01-selector.png) | ![MacTouch desktop with drawing and game icons](docs/screenshots/touch-02-desktop.png) |

These are **actual 320×240 captures from the physical prototype**, not mockups. The prototype uses historical welcome artwork and a different font. The public source replaces these with original terminal artwork and an MIT-licensed font. Native and boot-menu builds passed; hardware validation of the replacement visuals remains pending. [Capture details and verification scope](docs/VERIFICATION.md).

## Two ways to use it

| Environment | What it does | How it runs |
|---|---|---|
| **MacTouch Classic** | Paint with patterned fills and zoom; save drawings to SD; browse a gallery; write notes; play Maze, Puzzle, Puck, Glider and Castle; explore an original card story. | MicroPython applications designed for this screen. These are new miniature programs inspired by early desktop computing. |
| **Macintosh emulator** | Run compatible early applications from a user-prepared disk, with stylus mouse control and a choice of clear pixels or a full-screen overview. | A native RP2040 port of **umac / Musashi**, with SPI LCD, touch and SD integration. It runs guest software rather than recreating its interface. |

The PicoBoot-based menu selects the environment from SD. Applications within the emulated system launch from Finder; the startup menu does not need a separate entry for every game.

## See it running

| Create on the touch desktop | Explore the emulated desktop |
|---|---|
| **Paint: pen and patterned fill**<br>![Drawing a house, tree and mountains](docs/screenshots/touch-04-paint.png) | **Finder: original pixels at 1x**<br>![Finder at 1x with viewport toolbar](docs/screenshots/native-01-finder.png) |
| **Notes: on-screen keyboard**<br>![Notes with sample text and keyboard](docs/screenshots/touch-11-notes.png) | **Calculator: 128 + 64 = 192**<br>![Calculator showing 192](docs/screenshots/native-09-calculator.png) |
| **Puck: a touch-controlled rally**<br>![Puck during a rally](docs/screenshots/touch-13-puck-rally.png) | **Missile Command: firing in Fit view**<br>![Missile Command with explosions](docs/screenshots/native-08-missile-command.png) |

[**Browse all 28 real-device screenshots →**](docs/SCREENSHOTS.md)

Guest systems and games in these documentary images are separately supplied software. They are **not included** in this repository, and their displayed artwork is not covered by the project's source licenses.

## A small screen with two useful views

The emulated display stays **512×342**; the LCD is **320×240**. The port leaves the guest applications intact and adapts how their framebuffer is shown:

- **1x:** crisp original pixels for text and Finder. Pan or use the four arrow icons to reach the rest of the desktop.
- **Fit:** the entire guest display, filtered to keep small strokes visible. Useful for games and large dialogs, with smaller text.
- **Automatic defaults:** Finder and unknown applications start at 1x; seven named game profiles start at Fit. Manual choices are remembered per application until power-off. Tap the **A/M** status area to restore the current application's default.

See the [illustrated user guide](docs/wiki/User-guide.md) for touch gestures, navigation and application controls.

## Hardware

![Pico, LCD, touch and SD logical connections](docs/hardware-overview.svg)

| Part | Tested configuration |
|---|---|
| Controller | Raspberry Pi Pico, **RP2040**, 2 MiB flash / 264 KiB SRAM |
| Display | Waveshare **Pico-ResTouch-LCD-2.8**, ST7789, 320×240 SPI |
| Touch | XPT2046 resistive controller and stylus |
| Storage | FAT32 microSD; tested with a 16 GB card |
| USB | Power, serial diagnostics and boot-menu SD access |

[Pin mapping and flash layout](docs/HARDWARE.md) · [Manufacturer's board documentation](https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8)

## Build your own

**Start with [Assembly and first boot](docs/QUICKSTART.md):** a numbered guide covering board assembly, tools, user-supplied software, local builds, SD folders, BOOTSEL, the internal bootstrap and calibration.

1. Check the [hardware](docs/HARDWARE.md) and back up any existing installation.
2. Follow the [build guide](docs/BUILD.md) to fetch fixed upstream revisions and build the menu and application partitions.
3. Prepare the SD folders, install the MicroPython bootstrap and calibrate the touchscreen.
4. For emulation, provide a supported ROM and prepared raw disk image that you have the right to use. Select the environment at startup.

**No Apple ROM, System/Finder disk, third-party game or precompiled firmware is supplied.** The native build embeds the ROM you provide; keep that output local. Build tools do not download proprietary software or flash your device automatically.

Dropping a **`.sit` archive onto SD does not install or run it**. Archives must first be extracted with Macintosh metadata preserved and their compatible applications installed into a supported guest disk. Read [software and SD storage](docs/wiki/Software-and-storage.md) before preparing a collection.

## Current limits and status

This source snapshot derives from hardware prototype **0.3.2**; the public variant is **0.3.2-share1**.

- **192 KiB emulated RAM:** this is a constrained early Macintosh emulator, not a full 1 MiB Macintosh Plus. A larger SD card does not increase RAM.
- **No sound output or USB-host keyboard/mouse support** in this port. A USB hub alone does not add those features.
- Software compatibility and animation speed vary. The demonstrated games are examples, not a compatibility guarantee.
- Public native/menu builds and renderer/input checks passed. A fresh public MicroPython partition build and hardware checks of the replacement visuals remain pending. [Full verification record](docs/VERIFICATION.md).

## Documentation and repository map

| I want to… | Start here |
|---|---|
| Understand and use the project | [Documentation home](docs/wiki/Home.md) · [User guide](docs/wiki/User-guide.md) |
| Install it on my own board | [Build](docs/BUILD.md) · [Hardware](docs/HARDWARE.md) |
| Follow the full physical setup | [Assembly and first boot](docs/QUICKSTART.md) |
| Add applications or manage SD files | [Software and storage](docs/wiki/Software-and-storage.md) |
| Find software provenance and excluded files | [Software sources](docs/SOFTWARE-SOURCES.md) |
| Try small changes with a coding assistant | [AI-assisted learning workflow](docs/AI-WORKFLOW.md) |
| Modify the firmware | [Architecture and source map](docs/wiki/Architecture.md) |
| See what has actually been tested | [Verification](docs/VERIFICATION.md) · [Screenshot gallery](docs/SCREENSHOTS.md) |
| Trace upstream work or publish a fork | [Credits](docs/wiki/Origins-and-credits.md) · [License map](LICENSE.md) · [Publishing guide](docs/PUBLISHING.md) |

All repository documentation is in English. The documentation home is a repository-hosted, Wiki-style guide, so its pages and images remain available with a normal clone.

## Kits and support

An **unassembled DIY parts kit** is planned for Tindie at **US$69**, with **estimated shipping of US$20 per kit**. The buyer assembles the hardware, prepares SD storage and installs the software. A computer and comfort following build/setup instructions are required. It is not a preassembled or preconfigured Macintosh computer.

Read the [kit scope and buyer requirements](docs/KIT.md). The final packing list, shipping weight and purchase/contact links will be added with the actual listing. No product order is offered through this README yet. [Prepared English listing copy](docs/TINDIE-LISTING.md).

This is also a practical learning project: use ChatGPT, Claude or another assistant to understand the source, draft a small application or investigate a serial log, then check the result on hardware. See the [example workflow](docs/AI-WORKFLOW.md). Physical assembly, calibration, review and software-compatibility checks remain part of the process.

## Credits and licensing

The project began with [Simon Boak's Picontosh](https://github.com/simonboak/Picontosh) and [his illustrated project article](https://unimplementedtrap.com/picontosh-exploring-classic-macintosh-icon-format/). Emulation is based on [Matt Evans' umac](https://github.com/evansm7/umac) and Musashi; environment selection builds on [PicoBoot](https://github.com/lohengrin/PicoBoot) / Pico-Toolset. MicroPython, Raspberry Pi's SDK, LVGL and SD/FatFs drivers provide further foundations.

This repository contributes the touch desktop, board integration, pressure-filtered stylus control, shared-SPI storage, protected application layout and adaptive viewport. [Detailed attribution](docs/wiki/Origins-and-credits.md) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [Exact upstream revisions](upstreams.lock.json).

The repository contains **multiple licenses**, including MIT, GPL and Apache terms. See [LICENSE.md](LICENSE.md); it is not an all-MIT project. ROMs, operating systems, games and third-party screenshot artwork retain their own rights.

Independent project; no affiliation, authorization or endorsement by Apple Inc. Apple and Macintosh names are used to describe compatibility and remain the property of their respective owners.
