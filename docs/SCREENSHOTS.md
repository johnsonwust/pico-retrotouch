# Real-device screenshots

[Project overview](../README.md) · [Documentation](wiki/Home.md) · [Verification](VERIFICATION.md)

**28 original-size 320×240 PNGs**, captured from a physical RP2040 Pico with the Waveshare Pico-ResTouch-LCD-2.8. These are real display images from scripted interactions and sample data, with no generated scenes, case mockups, screen borders or rescaling.

## Capture scope

- **One boot-menu scene:** the device's LVGL display tiles were written to BMP, read back from SD and converted losslessly to PNG. Decoded RGB pixels match the source BMP.
- **15 MacTouch scenes:** device-written framebuffer images were checked against the device's framebuffer CRC after SD readback.
- **12 native scenes:** all 240 row checks were verified for each capture, including the filtered grayscale Fit view.
- Every exported PNG was visually reviewed. [Machine-readable provenance and SHA-256 hashes](screenshots/captures.json).

**Versions:** MacTouch Classic 0.3.0 and native emulator 0.3.2, plus the installed prototype boot menu. The public-source variant replaces the prototype's font and smile/welcome artwork. These images document the prototype, not physical validation of the replacement public visuals.

System/Finder and classic games shown below were separately supplied for the private working disk and are not bundled with this repository. Third-party interface, font, trademark and game artwork remains with its respective owners; source licenses do not relicense those pixels.

The original working disk was backed up and restored with SHA-256 verification after the application demos. MacTouch sample drawings and notes used an isolated demo namespace. The added boot-menu capture did not replace the firmware or guest disk; the device returned to Finder afterwards.

## Startup: choose an environment

![Prototype startup menu: smile, hello and two environment buttons](screenshots/boot-01-selector.png)

The installed prototype presents Macintosh / System 3.2 and MacTouch Classic. The public source uses original terminal artwork instead of this historical-style welcome screen.

## MacTouch: desktop, creativity and touch games

| Scene | Scene |
|---|---|
| **Boot and SD ready**<br>![Boot and SD ready](screenshots/touch-01-boot.png) | **Touch desktop**<br>![Touch desktop](screenshots/touch-02-desktop.png) |
| **Second desktop page**<br>![Second desktop page](screenshots/touch-03-desktop-tools.png) | **Drawing and patterned fill**<br>![Drawing and patterned fill](screenshots/touch-04-paint.png) |
| **Zoom and navigator**<br>![Zoom and navigator](screenshots/touch-05-paint-zoom.png) | **Saved drawing in SD gallery**<br>![Saved drawing in SD gallery](screenshots/touch-06-gallery.png) |
| **Reloaded drawing**<br>![Reloaded drawing](screenshots/touch-07-saved-picture.png) | **Maze and hint**<br>![Maze and hint](screenshots/touch-08-maze.png) |
| **Sliding puzzle**<br>![Sliding puzzle](screenshots/touch-09-puzzle.png) | **Original card story**<br>![Original card story](screenshots/touch-10-cards.png) |
| **Notes and on-screen keyboard**<br>![Notes and on-screen keyboard](screenshots/touch-11-notes.png) | **Air hockey paddle movement**<br>![Air hockey paddle movement](screenshots/touch-12-puck.png) |
| **Rally, later frame**<br>![Rally, later frame](screenshots/touch-13-puck-rally.png) | **Paper glider in flight**<br>![Paper glider in flight](screenshots/touch-14-glider.png) |
| **Castle jump**<br>![Castle jump](screenshots/touch-15-castle.png) |  |

## Native emulator: applications and games

| Scene | Scene |
|---|---|
| **Finder at crisp 1x**<br>![Finder at crisp 1x](screenshots/native-01-finder.png) | **Blackjack: bet selection**<br>![Blackjack: bet selection](screenshots/native-02-blackjack-bets.png) |
| **Blackjack: full hand in Fit**<br>![Blackjack: full hand in Fit](screenshots/native-03-blackjack-hand-fit.png) | **Blackjack: decision dialog at 1x**<br>![Blackjack: decision dialog at 1x](screenshots/native-04-blackjack-hand-detail.png) |
| **Blackjack: end-of-hand result**<br>![Blackjack: end-of-hand result](screenshots/native-05-blackjack-result.png) | **Brickles: ready to begin**<br>![Brickles: ready to begin](screenshots/native-06-brickles-ready.png) |
| **Brickles: ball, bricks and paddle**<br>![Brickles: ball, bricks and paddle](screenshots/native-07-brickles-playing.png) | **Missile Command: explosions after firing**<br>![Missile Command: explosions after firing](screenshots/native-08-missile-command.png) |
| **Calculator: 128 + 64 = 192**<br>![Calculator: 128 + 64 = 192](screenshots/native-09-calculator.png) | **Daleks: field and direction controls**<br>![Daleks: field and direction controls](screenshots/native-10-daleks.png) |
| **BlackBox: logic board**<br>![BlackBox: logic board](screenshots/native-11-blackbox.png) | **Back to Finder after the demo**<br>![Back to Finder after the demo](screenshots/native-12-finder-return.png) |

## Capture your own native scene

```sh
python scripts/capture_screen.py --port COM4 --output build/captures/lcd.png
```

Run this from the repository root, replacing `COM4` with your device port. The utility targets the native environment; boot-menu and MicroPython captures use different paths. See the [build guide](BUILD.md) for dependencies. Review any new image before sharing it.
