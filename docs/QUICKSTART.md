# Assembly and first boot

[Project overview](../README.md) · [Hardware reference](HARDWARE.md) · [Build details](BUILD.md) · [User guide](wiki/User-guide.md)

This is the installation path for a **DIY parts kit or independently sourced hardware**. You assemble the hardware and install the software yourself. A computer is required. The public source uses a replacement font and welcome graphic; its native/menu builds passed, but the replacement visuals and a fresh public MicroPython partition still need the checks recorded in [VERIFICATION.md](VERIFICATION.md).

## Before you start

| You need | Notes |
|---|---|
| Raspberry Pi Pico with RP2040 | 2 MiB flash. This guide does not validate Pico 2, Pico W or another controller. |
| Waveshare Pico-ResTouch-LCD-2.8 | 320×240 ST7789 display, XPT2046 touch and microSD slot. |
| Headers, stylus and any mounting parts | Use suitable headers; soldering is needed if your Pico has none. The final kit listing will specify its exact contents. |
| FAT32 microSD and a card reader | A 16 GB card was tested. Back up an existing card before changing it. |
| Micro-USB data cable and a computer | A charge-only cable will not expose the programming/serial interfaces. |
| Development tools | Python 3, Git, CMake, GNU make, host GCC and Arm GNU toolchain. Thonny is convenient for copying the MicroPython bootstrap. |
| Optional emulation inputs | A supported, legally usable ROM and a bootable early-system raw disk. They are not supplied here. MacTouch itself does not need Apple software. |

![Logical hardware connections](hardware-overview.svg)

The diagram shows logical connections, not physical header orientation. Check the [Waveshare mounting illustration and pin table](https://www.waveshare.com/wiki/Pico-ResTouch-LCD-2.8) before plugging the boards together. The project follows the Pico + Waveshare + SD approach in [Simon Boak's original Picontosh article](https://unimplementedtrap.com/picontosh-exploring-classic-macintosh-icon-format/); its original hardware photos remain on the author's site.

## 1. Assemble with power disconnected

1. Unplug USB and remove any other power source.
2. If needed, solder the correct headers to the Pico. Check for solder bridges and bent pins before attaching the display.
3. Align the Pico with the display board's marked USB direction. Confirm both header rows are aligned; do not force an offset connection.
4. If your display board has an **SPI / SDIO** selector, set the SD interface to **SPI**. This port uses GP22 as SD chip select.
5. Insert the backed-up FAT32 card into the display's microSD slot. Leave the boards accessible until screen, touch and storage have been checked.

Do not use an enclosure photograph as a connector-orientation guide. A 3D case, printer files and screws are not supplied by this source repository; consult the final kit packing list for physical parts.

## 2. Get the source and tools

1. Clone this repository, or choose **Code → Download ZIP** on GitHub and extract it.
2. Open a terminal in the repository root: the folder containing `README.md`, `scripts/` and `src/`.
3. Install the development tools listed above. Verify that these commands resolve on your computer:

```sh
python --version
git --version
cmake --version
make --version
gcc --version
arm-none-eabi-gcc --version
arm-none-eabi-objcopy --version
```

On Windows, command names depend on the installed toolchain; the build script accepts explicit `--host-cc`, `--make`, `--cmake` and `--toolchain-dir` paths. See [BUILD.md](BUILD.md) for an example. These are developer builds, not a one-click firmware installer.

4. Optional serial capture/debug tools:

```sh
python -m pip install -r requirements-dev.txt
```

5. Fetch the fixed upstream versions:

```sh
python scripts/fetch_dependencies.py --target menu
python scripts/fetch_dependencies.py --target micropython
```

Fetch the native target too if you intend to run the emulator:

```sh
python scripts/fetch_dependencies.py --target native
```

## 3. Prepare your own emulation inputs (optional)

1. Obtain software you have the right to use. The [software sources page](SOFTWARE-SOURCES.md) identifies the prototype's references without redistributing their files.
2. Put a **128 KiB Mac Plus V3 ROM**, identifier `4d1f8172`, at `local-assets/user.rom`. The build validates its size and identifier. Other ROM revisions are not accepted by this build path.
3. Put your prepared, bootable **raw MFS** early-system disk at `local-assets/user-system-disk.img`. The prototype used System 3.2; later systems may exceed this port's 192 KiB guest RAM.
4. Keep the original inputs elsewhere as backups. `local-assets/` is ignored by Git, but that does not make it safe to include in a manually created upload ZIP.

For a first boot, an otherwise suitable raw 400 KiB MFS system disk can be used directly. An extension of `.img` is not enough: StuffIt archives, Disk Copy wrappers, compressed images and arbitrary HFS volumes cannot simply be renamed to make them suitable.

### Adding applications to a working disk

You can complete the touch-desktop installation without this optional preparation. For Macintosh applications:

1. Read each application's requirements and select early 68000 monochrome software. Download it yourself from an appropriate source.
2. Keep the download on the computer, outside the public source files. For a `.sit` archive, a host tool used during prototyping was [StuffIt-Go](https://github.com/ObsoleteMadness/StuffIt-Go). Obtain its official release and follow its checksum instructions. Its CLI provides:

```sh
stuffit list archive.sit
stuffit info -json archive.sit
stuffit extract -C extracted archive.sit
```

3. Preserve the complete extraction result, including `._` sidecars and any nested archives. Extraction does not itself install an application or prove compatibility. The two prototype downloads had different layouts: one wrapped a disk image; another carried a resource-fork application.
4. Prepare a **copy** of your raw MFS working disk in a suitable Macintosh environment. For example, [Mini vMac](https://www.gryphel.com/c/minivmac/start.html) on a computer can boot a user-supplied disk and mount another supported application disk. Once both volumes are mounted, copy the extracted application **inside the Macintosh Finder** to the working volume. This preserves its Macintosh forks and metadata. Quit applications, eject/shut down the guest disks, then close the host emulator before transferring the working image.
5. If the download is still an archive, unpack it in a host Macintosh/emulator environment with an extractor that supports that archive version. This preparation environment may need more memory or a later system than the Pico supports. Mini vMac's [ImportFl documentation](https://www.gryphel.com/c/minivmac/extras/importfl/) explains archive transfer: ImportFl transfers data forks only, so it must not be used to import a bare resource-fork application. An unexpected disk-initialization prompt is a reason to eject the input, not format it.
6. Use that prepared raw MFS image as `local-assets/user-system-disk.img`. Applications can be arranged in Finder and launched there; they do not require separate boot-menu entries.

Archive extraction, wrapper conversion and installing arbitrary downloads remain **format-specific host preparation**, not a completed universal pipeline supplied by this repository. Do not copy a naked application with Windows Explorer and assume its resource fork survived. Start with the working system disk; add one compatible program at a time and keep the last working image.

## 4. Build the firmware locally

Build the menu and MicroPython application:

```sh
python scripts/build.py menu
python scripts/build.py micropython
```

For emulation, build with your supplied ROM. Example calibration is used initially; replace it with your own measured coefficients in step 8.

```sh
python scripts/build.py native --rom local-assets/user.rom
```

The output is under ignored `dist/firmware/`. A stock MicroPython UF2 has a different layout and is **not** a substitute for `MacTouch.bin` in this dual-boot configuration. The native output embeds your ROM; keep it local.

## 5. Put the runtime files on SD

For the two environments with a prepared disk:

```sh
python scripts/prepare_sd.py --disk local-assets/user-system-disk.img
```

For MacTouch without a guest disk, omit `--disk`:

```sh
python scripts/prepare_sd.py
```

1. Open the generated `dist/sd-card/` folder.
2. Use your computer's card reader to copy its **contents** to the FAT32 card root, not into an extra `sd-card` folder.
3. Confirm the resulting layout:

```text
SD root/
├── DUALBOOT/
│   ├── MacTouch.bin
│   └── Macintosh.bin       # optional; requires a local native build
├── MACAPPS/
│   └── *.py
├── PICOMAC/
│   └── MAIN.IMG            # optional; your prepared raw guest disk
└── picoboot.cfg
```

4. Keep `auto_boot_timeout=0` in `picoboot.cfg` to choose an environment at startup.
5. Safely eject the card from the computer and put it back in the display board.

If the staging folder already contains `MAIN.IMG`, the tool refuses to replace it. Use a new `--output` staging folder for a different disk. When updating an existing card, preserve its current working disk, `MacTouch/` saves and `MACAPPS/touch_cal.json`; do not blindly replace them with an older copy.

## 6. Install the boot menu

1. Back up any previous Pico installation. Disconnect USB.
2. Hold the Pico's **BOOTSEL** button, connect the USB data cable, then release the button.
3. Find the USB volume named **RPI-RP2**. It is the Pico programming interface, not the SD card.
4. Copy your locally built `dist/firmware/bootmenu.uf2` to that volume.
5. Wait for the automatic reboot. The programming volume disappearing is expected. The menu should appear after SD initialization.

Only the menu UF2 is copied to RPI-RP2 in this procedure. The two application **`.bin`** files belong under `DUALBOOT/` on SD. The `.py` bootstrap files are copied through MicroPython in the next step.

## 7. Install the MicroPython bootstrap

1. Select **MacTouch** in the boot menu and wait for firmware loading to finish. A fresh board does not yet have the internal launcher.
2. Open [Thonny](https://thonny.org/). In **Tools → Options → Interpreter**, select **MicroPython (Raspberry Pi Pico)** and the device's actual serial port.
3. Open the Files panel. If needed, use Stop to obtain the MicroPython prompt.
4. Copy these files to the **root of the Pico's internal filesystem**, in order:

```text
src/bootstrap/sdcard_crc.py
src/bootstrap/sd_mount.py
src/bootstrap/main.py       # copy last
```

5. Restart the Pico and choose MacTouch again. The internal launcher mounts the card and imports `/sd/MACAPPS/dualtouch.py`.

The SD card carries the desktop modules. They are not placed on the BOOTSEL volume, and the bootstrap is not placed in an SD folder instead of the internal filesystem.

## 8. Calibrate and check the hardware

1. Complete the four cross targets: tap the center and lift fully between points.
2. Open Paint, draw a short line, save it, and open it in Gallery. Confirm storage reports SD; the storage layer can otherwise fall back to limited Pico storage.
3. In this SD-bootstrap setup, calibration is saved at **`MACAPPS/touch_cal.json` on SD**. Copy that six-number JSON file to the ignored `local-assets/touch_cal.json` on the computer when you next access the card offline.
4. Rebuild native firmware with the measured calibration, then stage/copy the updated `Macintosh.bin` to SD:

```sh
python scripts/build.py native --rom local-assets/user.rom --calibration local-assets/touch_cal.json
```

5. Boot-menu calibration is configured separately in the Toolset board patch; if menu taps are offset, see [HARDWARE.md](HARDWARE.md). The example coefficients are not universal.
6. Save, restart and choose Macintosh. Confirm Finder appears, move and release the pointer, open an application and quit back to Finder. Use Fit to locate an off-screen dialog, then 1x/Pan for readable detail.

For the first installation, check the boards before fitting the enclosure. Human checks are still needed for connector alignment, calibration and the actual screen result.

## 9. Daily use, updates and recovery

- Save work before resetting. Restarting returns to environment selection.
- Launch installed guest applications from Finder. Touch the menu title, slide to an item and lift to select it.
- Follow the [user guide](wiki/User-guide.md) for Paint, Notes and Fit/1x/Pan controls.
- For SD access through PicoBoot's USB bridge, return to the menu and run `python scripts/console.py --port COM4 maintenance`, replacing the example port. This pauses the touch UI. Do not access the card from the computer while either environment is running; use the physical reader with the device powered off if uncertain.
- If startup fails, retain the SD files and read the serial error. Check power/data cable, model, FAT32, SPI selection, folder names and bootstrap before rebuilding anything.
- BOOTSEL can reinstall your locally built menu. It does not restore a lost guest disk, notes or drawings; recover those from your own backup.

## First-boot checklist

- [ ] Correct RP2040 board and 2.8-inch ResTouch panel; headers and orientation checked.
- [ ] SD uses FAT32/SPI; runtime folders are at the root.
- [ ] Partitioned firmware built locally; menu installed via BOOTSEL.
- [ ] Bootstrap files copied to the internal MicroPython filesystem.
- [ ] Four-point touch calibration completed.
- [ ] Paint save and Gallery reload verified on SD.
- [ ] Optional licensed ROM/disk prepared; native calibration and Finder checked.
- [ ] Working SD and calibration backed up before further experiments.
