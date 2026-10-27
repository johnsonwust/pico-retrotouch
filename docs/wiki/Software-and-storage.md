# Software and SD storage

[Documentation home](Home.md) · [User guide](User-guide.md) · [Build guide](../BUILD.md)

For numbered installation and host-preparation steps, see [Assembly and first boot](../QUICKSTART.md). External software references and excluded files are documented in [SOFTWARE-SOURCES.md](../SOFTWARE-SOURCES.md).

## What belongs where?

The card uses FAT32. Both environments share the physical card, but the emulated Macintosh sees a **disk image inside it**, not the card's FAT32 directories.

```text
SD root/
├── DUALBOOT/
│   ├── MacTouch.bin        # locally built MicroPython application partition
│   └── Macintosh.bin       # locally built native partition; embeds your ROM
├── MACAPPS/
│   └── *.py                # touch desktop and its modules
├── PICOMAC/
│   └── MAIN.IMG            # your prepared guest disk
├── MacTouch/
│   └── ...                 # touch-desk drawings and notes, created during use
└── picoboot.cfg
```

The native port tries `/PICOMAC/MAIN.IMG`, then `/PICOMAC/SYSTEM32.IMG` as a fallback. The staging tool accepts raw, 512-byte-aligned images from 400 KiB to 16 MiB, but that size check alone does not establish filesystem, boot or application compatibility. The tested working disk was a 2 MiB **MFS** volume with separately supplied System 3.2 and applications.

## Can I just copy a SIT file to SD?

**Not in the current version.** StuffIt `.sit` files are compressed archives. A download can contain an application, a disk image, an installer, another archive or a later program unsuitable for this system. Putting that archive on the FAT32 card does not make Finder see or execute it.

The preparation workflow is:

1. Obtain software you have permission to use. Check its CPU, system and memory requirements.
2. Extract it on a suitable host or Macintosh environment. Preserve the **resource fork, data fork and Finder metadata**; a generic extractor that loses them can leave an unusable application.
3. If the result is a disk image, identify its actual format. An `.img` suffix does not guarantee raw sectors or a supported filesystem. Convert wrappers or unsupported formats in a separate preparation environment if required.
4. Install compatible extracted applications into your working guest disk with tools that preserve Macintosh metadata. A `Games` folder inside that disk is a convenient launcher.
5. Back up the current card image, then transfer the prepared working image while the card is offline or the boot menu is in maintenance mode. Start the Macintosh environment and launch applications through Finder.

**No general archive extractor, disk-image installer or automated conversion pipeline is supplied here.** These steps describe the current preparation process, not a completed drag-and-drop importer. Simply renaming an archive to `.IMG` will not work.

![Applications launched inside the guest Finder](../screenshots/native-12-finder-return.png)

*The prototype's application collection is shown for demonstration. Its disk and applications are not distributed with this source.*

## What software is likely to fit?

Start with small, early monochrome **68000** applications compatible with the supplied early system. This build offers only **192 KiB guest RAM**. Programs needing a normal 1 MiB Macintosh Plus, a later OS, color hardware, unsupported peripherals or substantial audio behavior may fail even if extraction succeeds.

The captured prototype ran Calculator and examples of Blackjack, Brickles, Missile Command, Daleks and BlackBox. Those scenes demonstrate specific interactions, not full regression testing of every version. The automatic Fit profiles are separate from compatibility detection.

## Does SD add RAM?

No. It gives the project room for firmware images, Python modules, guest disks, pictures and notes. It does not turn 192 KiB guest RAM into 1 MiB. SD paging would require a different memory subsystem and would incur slow random access; this port does not implement it.

## Updating without losing work

- Keep a separate backup of the card and internal MicroPython files.
- Preserve the existing `PICOMAC/MAIN.IMG` when updating firmware: it holds the guest's installed software and documents.
- Preserve `MacTouch/` and your calibration. Touch-desk data is outside the guest image.
- Use PicoBoot's `maintenance` command before computer SD access. Do not let the host and a running environment write the same card concurrently.
- `prepare_sd.py` creates a staging directory and refuses to replace an existing destination disk. It never formats a card.

## Not yet implemented

A customer-friendly SD archive inbox with extraction, compatibility checks and installation remains future work. So do persistent application display preferences and an SD-loaded-ROM design. These are possible directions, not available features or delivery commitments.
