# Verification scope

[Project overview](../README.md) · [Documentation](wiki/Home.md)

## Hardware prototype, before this public export

The RP2040 + ResTouch prototype 0.3.2 was tested on a physical device:

- Two-environment boot, SD access, protected MicroPython data partition.
- Touch-desk calibration, Paint/Gallery SD save/readback, notes and small games.
- Native System 3.2 startup from a separately supplied working disk.
- 512×342 guest on 320×240 LCD, area-filtered Fit, 1x, Pan, correct touch coordinates.
- Finder 1x → Blackjack Fit → Quit → Finder 1x; manual mode/origin recall within one power-on session and automatic reset.
- Four solid direction-arrow icons captured from the actual LCD framebuffer.

Those tests used private software inputs that are not in this repository. They do not certify all guest applications or a full 1 MiB Mac Plus.

## Public-source variant

The export intentionally replaces the prototype's Chicago-style font and historic smile artwork with the explicitly MIT-licensed MicroPython font and original terminal graphic. The public source paths/build helpers were reorganized and personal serial selection was removed. These are **not** the exact firmware binaries running on the prototype. Public-specific checks and build results are recorded in `SOURCE_VERIFICATION.json`.

No physical flashing of the public-source variant was performed during export preparation. A clean build is evidence of buildability, not physical touch calibration or gameplay validation of the new font/layout. Source and license review is not a legal clearance certificate for future binary releases or bundled user software.

## Real-device screenshot session — 2026-10-27

The original hardware prototype was driven through scripted demos to capture **28** display images: one boot-menu scene, 15 touch-desk scenes and 12 native scenes. All PNGs are 320×240 with no resampling. The additional boot-menu capture used device-written LVGL flush tiles in a BMP; lossless PNG conversion was checked for decoded RGB pixel equality. No native row-hash check is claimed for the menu capture. Native captures checked all 240 row hashes; touch-desk PBMs were written by the device and checked against its framebuffer CRC after USB SD readback. Every exported image was visually reviewed; `docs/screenshots/captures.json` records hashes, captions, environments and provenance.

Scenes include Paint, zoom/navigation, SD save and gallery reload, maze, puzzle, card story, notes, Puck, Glider, Castle, Finder, Calculator and five separately supplied classic games. These are documentary images of scripted interactions, not a broad gameplay benchmark or screenshots of the new public font/artwork variant.

The original guest working disk was backed up before the session and restored with SHA-256 verification afterwards. Touch-desk examples used a separate storage namespace. Existing user drawings/notes were not used as demo content. The device finished in Finder; its installed firmware was not replaced by public-source builds.
