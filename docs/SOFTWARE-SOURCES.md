# Software sources and excluded material

[Project overview](../README.md) · [Assembly and first boot](QUICKSTART.md) · [License map](../LICENSE.md)

The repository and its source archive provide project code, documentation, license texts and reviewed documentary screenshots. They do **not** contain Macintosh ROMs, System/Finder disks, third-party applications or games, downloadable game archives, private working images or ROM-embedded firmware.

## Prototype references

| Material | Source / reference | Repository policy |
|---|---|---|
| Original Picontosh concept and hardware approach | [Simon Boak's article, 30 November 2024](https://unimplementedtrap.com/picontosh-exploring-classic-macintosh-icon-format/) and [Picontosh source](https://github.com/simonboak/Picontosh) | Credit and links retained; blog photography is not copied into this repository. |
| Macintosh Plus V3 ROM | Supplied privately by the prototype owner; no original acquisition URL was recorded. [Mini vMac's ROM guidance](https://www.gryphel.com/c/minivmac/start.html) describes using a ROM from your own Macintosh. | Obtain your own authorized input; no ROM download or embedded firmware is supplied. |
| System 3.2 / Finder working disk | Supplied privately by the owner; no acquisition URL was recorded. | Prepare a suitable disk you have the right to use. It is not attributed to a download site without evidence. |
| Missile Command prototype download | [Macintosh Garden catalog page](https://macintoshgarden.org/games/missile-command-23); downloaded archive named `missilecommand.img_.sit` | Download and prepare independently if permitted. The inspected resource identified version 3.0, despite the page title referring to 2.3. |
| Daleks prototype download | [Macintosh Garden catalog page](https://macintoshgarden.org/games/daleks); downloaded archive named `Daleks.sit` | Not bundled. Prototype resource version was 0.3. |
| Bubba, Break the Bricks, Black Box, Blackjack and Brickles candidates | [E-Maculation's System 6 Hell catalog](https://www.emaculation.com/doku.php/system_6_hell), `games-b.dsk` collection | Not bundled. Its host/System 6 compatibility is not a guarantee for this Pico port. |
| Host archive extraction | [StuffIt-Go](https://github.com/ObsoleteMadness/StuffIt-Go) | Optional external tool, not bundled or executed by the firmware. |
| Host Macintosh preparation | [Mini vMac](https://www.gryphel.com/c/minivmac/start.html) and [ImportFl documentation](https://www.gryphel.com/c/minivmac/extras/importfl/) | Optional external preparation route; supply your own permitted software. |

These links identify provenance and documentation. A catalog listing or an old publication date does not by itself grant redistribution or commercial-bundling permission. Follow the software's actual terms; source attribution is not a substitute for permission.

## What to place on SD

| File | Destination | Meaning |
|---|---|---|
| Locally built `MacTouch.bin` | `/DUALBOOT/MacTouch.bin` | Partitioned MicroPython firmware |
| Locally built `Macintosh.bin` | `/DUALBOOT/Macintosh.bin` | Native emulator with your supplied ROM embedded |
| Touch-desk modules | `/MACAPPS/*.py` | Original/reimplemented desktop programs |
| Your prepared raw guest disk | `/PICOMAC/MAIN.IMG` | The guest's System/Finder, installed applications and documents |
| `.sit`, `.zip`, `.hqx` or a raw ROM | No automatic SD import location in this version | Prepare archives on the computer; the native ROM is embedded during the local build |

Read [the complete installation procedure](QUICKSTART.md) for assembly, firmware loading, archive preparation, bootstrap copying and touch calibration. The card's FAT32 folders and the Macintosh files inside `MAIN.IMG` are different filesystems.

## Screenshots and photographs

The [28 screenshots](SCREENSHOTS.md) were captured from the prototype and are provided to document its behavior. Displayed Apple/game/font/interface artwork remains with the relevant owners and is not relicensed as source code. The blog's original photos are linked at their source rather than included in the source archive. The repository's hardware diagram is an original schematic illustration, not a photograph of the author's or seller's kit.
