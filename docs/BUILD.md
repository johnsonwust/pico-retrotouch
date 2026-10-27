# Build from source

[Project overview](../README.md) · [Documentation](wiki/Home.md)

For board assembly, first flashing, SD copying and calibration in order, start with [Assembly and first boot](QUICKSTART.md). This page is the concise command reference.

Prerequisites: Python 3, Git, CMake >=3.20, GNU make, a **host C compiler** such as GCC, and the Arm GNU toolchain (`arm-none-eabi-gcc` / `objcopy`). Build scripts use Python's standard library. Optional serial console: `python -m pip install -r requirements-dev.txt`.

Run commands from this repository root. Paths can contain spaces. No script downloads ROMs, system software or games, and no script flashes a physical device automatically.

## 1. Fetch fixed source versions

```sh
python scripts/fetch_dependencies.py --target native
python scripts/fetch_dependencies.py --target menu
```

Dependencies go into ignored `external/`; commits and patch paths are fixed in `upstreams.lock.json`. Fetching checks local changes before switching commits, and patches are applied only when not already present. The native target does not build the GPLv2 SDL frontend.

## 2. Local native emulator build

Supply a Mac Plus V3 128 KiB ROM with version identifier `4d1f8172` and software you have the right to use. Put personal input files in `local-assets/` or outside this repository. There is no ROM downloader.

```sh
python scripts/build.py native --rom local-assets/user.rom --calibration local-assets/touch_cal.json
```

If calibration is omitted, the example coefficients are used, with a warning. The script builds umac's ROM patch utility from source, applies the quiet-beep compatibility patch to a local copy, generates Musashi opcodes, and builds the protected application partition. It does not alter the supplied ROM.

Tool paths can be explicit, for example:

```sh
python scripts/build.py native --rom local-assets/user.rom --host-cc /path/to/gcc --make /path/to/make --cmake /path/to/cmake --toolchain-dir /path/to/arm-gnu-toolchain
```

Output: ignored `dist/firmware/Macintosh.bin` and `.uf2`. **These contain your ROM; do not add them to Git, Releases, Actions artifacts, Pages or downloadable demo packages.** Generated headers, ELF files and temporary ROM copies in `build/` are private too.

## 3. Boot menu

```sh
python scripts/build.py menu
```

Output: `dist/firmware/bootmenu.bin` and `.uf2`, reserved to the first 512 KiB. The public welcome artwork is the project's own terminal graphic; its font comes from the MIT source asset. The menu uses PicoBoot's existing binary catalog and verification.

## 4. MicroPython partition and touch desk

```sh
python scripts/fetch_dependencies.py --target micropython
python scripts/build.py micropython
```

This builds mpy-cross then the `RPI_PICO` port with 512 KiB filesystem and an application origin of `0x10080000`. Do not substitute a stock MicroPython UF2 for this partition build inside the dual-boot layout. The public scripts expose this build path; consult `docs/VERIFICATION.md` for which targets were freshly built in preparing the share snapshot.

For a standalone MicroPython experiment without dual boot, the touch-desk modules can instead be copied to a suitable normal MicroPython installation. That has a different flash layout; back up the device before changing installations.

## 5. Prepare a local SD folder

```sh
python scripts/prepare_sd.py --disk local-assets/user-system-disk.img
```

The optional `--disk` is a user-prepared raw 400 KiB–16 MiB, 512-byte-aligned disk. The port does not accept every disk format merely because it has an `.img` extension. The supplied disk is copied to the local staging folder as `PICOMAC/MAIN.IMG`; an existing destination disk is never replaced. No bundled OS/game or automatic SIT import is supplied.

The staging folder is ignored `dist/sd-card/`:

```text
DUALBOOT/MacTouch.bin       # if built
DUALBOOT/Macintosh.bin      # if built, contains the user's ROM
MACAPPS/*.py
PICOMAC/MAIN.IMG            # if explicitly supplied by the user
picoboot.cfg
```

Merge app files into your own card, preserving newer working disks, drawings, notes and saves. Do not format the card as part of an update. During USB SD access use PicoBoot's serial `maintenance` command to pause touch UI; reboot resumes it. Do not access the SD card from a PC while the guest or touch desk is using it.

After flashing **your own built menu UF2** via BOOTSEL and putting the app binaries/SD modules on your card, choose the MicroPython environment. Copy `src/bootstrap/sdcard_crc.py`, `sd_mount.py`, then **main.py last** to MicroPython's internal filesystem using Thonny or mpremote. The bootstrap imports `dualtouch.py` from `/sd/MACAPPS`. Fresh touch-desk setup asks for calibration; no active calibration file or previous user data is included. The explicitly named example coefficients are only a starting point for the native build.

The native environment requires a usable supplied disk. It tries `/PICOMAC/MAIN.IMG`, with `/PICOMAC/SYSTEM32.IMG` as fallback. Desktop layout and installed games are contents of your disk; no default Games window or seven-game bundle is included in this repository.

## 6. Checks and serial diagnostics

```sh
python scripts/check_viewport.py
python scripts/audit_public.py
python scripts/console.py --port COM4 view
python scripts/capture_screen.py --port COM4 --output build/captures/lcd.png
```

Viewport checks compile the actual renderer and touch dispatcher using **synthetic test pixels**, with no copyrighted disk, game screenshot or RAM dump. They cover exact 1x rows, Fit boundaries/area coverage, Pan isolation, touch mapping, app defaults/recall and reset. Outputs stay under ignored `build/`.

`capture_screen.py` runs against the native firmware and verifies every LCD row before saving a lossless PNG. Optional `--mode frame` captures the whole 512×342 guest instead of the physical LCD view. It needs the optional Pillow/pyserial requirements and does not rescale the captured pixels. A checksum record is saved beside the PNG. The prototype's real-device examples are in [SCREENSHOTS.md](SCREENSHOTS.md); captured third-party interfaces are not relicensed as project source.

Native serial commands include `view`, `view fit`, `view 1x`, `view auto`, `view top`, `diag`, `frame`, `screen` and `menu`. `DSErrCode=40` is a retained startup greeting in the tested System 3.2 environment, not by itself a new crash. The quiet-beep patch emits no sound.
