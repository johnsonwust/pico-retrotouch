# Architecture and source map

[Documentation home](Home.md) · [Hardware layout](../HARDWARE.md) · [Build guide](../BUILD.md)

## One selected application at a time

```text
Reset → PicoBoot menu
          ├─ load DUALBOOT/MacTouch.bin
          │    → MicroPython → internal bootstrap → SD:/MACAPPS → touch desktop
          └─ load DUALBOOT/Macintosh.bin
               → umac + Musashi → SD:/PICOMAC/MAIN.IMG → guest Finder/apps
```

These environments do not run concurrently. PicoBoot loads a selected binary into the middle 1 MiB of flash. Its first 512 KiB and the final 512 KiB MicroPython filesystem are reserved separately. The application linkers and boot writer enforce these bounds. See the [flash table](../HARDWARE.md).

Large modules, guest disks and user saves live on SD. The native application currently embeds its supplied ROM. This is why generated native firmware is kept out of public releases.

## Shared hardware

LCD, touch controller and SD card share SPI1 with independent chip-select lines. Drivers restore bus configuration and deselect other devices before transactions. Touch filtering checks pressure and release so a lifted stylus does not continue moving the mouse.

The native guest framebuffer stays 512×342. The host renderer provides a 320×222 content area plus an 18-pixel toolbar. At 1x it copies original pixels; in Fit it computes area-filtered grayscale. Changed-row hashes reduce unnecessary LCD writes. This does not make the SPI panel a general-purpose laptop display.

View profiles read the guest's current application name and select a host-side view. They do not patch application windows or resize the guest framebuffer. A bounded table remembers manual choices during the current session.

## Where to change things

| Path | Responsibility |
|---|---|
| `src/mactouch/` | Touch desktop, original mini-apps, display and SD storage modules |
| `src/bootstrap/` | Small internal MicroPython launcher; mounts SD and imports the desktop |
| `src/native/` | Native board entry point, emulator integration, diagnostics and SD configuration |
| `src/viewport/` | LCD rendering, touch mapping, toolbar and application defaults |
| `config/` | Explicitly named example calibration, not per-unit factory values |
| `patches/` | Reviewable changes to PicoBoot, Toolset, MicroPython and boot-menu SD handling |
| `scripts/` | Dependency fetching, local builds, SD staging, capture and publication checks |
| `tests/` | Host checks of the real viewport code using synthetic pixels |
| `assets/` | MIT font source used by the public visual variant |
| `upstreams.lock.json` | Fixed dependency commits and patch locations |

## Development checks

```sh
python scripts/check_viewport.py
python scripts/audit_public.py
python scripts/console.py --port COM4 view
python scripts/capture_screen.py --port COM4 --output build/captures/lcd.png
```

Replace `COM4` with your device port. The capture utility targets the native environment, verifies every LCD row and saves an unscaled PNG plus a checksum record. It does not capture the boot menu or MicroPython desktop.

`external/`, `build/`, `dist/` and `local-assets/` stay local and ignored. Run the publication audit before sharing new assets, and update the [verification record](../VERIFICATION.md) when the public visual variant is tested on hardware.
