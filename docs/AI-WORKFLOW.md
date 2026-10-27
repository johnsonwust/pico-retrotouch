# Learning through AI-assisted hardware experiments

[Project overview](../README.md) · [Installation](QUICKSTART.md) · [Architecture](wiki/Architecture.md)

Pico RetroTouch is a small, visible place to practise **AI-assisted hardware and software development**. An inexpensive microcontroller, SPI screen, stylus and SD card make each change tangible: a new button, a saved drawing, a different display mode or a program that responds to touch.

The MicroPython desktop is a useful starting point because its small modules are easy to inspect and change. The native emulator offers a more advanced example involving CPU emulation, constrained RAM, display conversion and firmware partitions. It does not make the Pico a general-purpose computer capable of running arbitrary operating systems.

## A practical loop

1. **Start from a known working version.** Back up the SD card and calibration, then save a source commit.
2. **Give the assistant the actual context.** Share the board model, pin table, relevant source module, intended behavior and a short serial log. Remove private paths, credentials, ROM contents and personal documents.
3. **Ask for one small change.** For example, add a timer control, change a Paint pattern, add a touch mini-game or improve a storage error message.
4. **Read the proposed diff.** Confirm that pin assignments, shared-SPI transactions, flash bounds and existing saves are handled correctly.
5. **Build or upload locally.** An assistant with authorized tools can help edit files, build, transfer files, issue serial commands and inspect captures.
6. **Check the physical result.** A person still connects power, checks assembly, enters BOOTSEL when required, performs touch calibration and judges the actual screen/input behavior.
7. **Keep or revert the change.** Save the successful version before starting the next experiment.

Tools such as ChatGPT or Claude can help explain unfamiliar code, draft small programs, interpret compiler errors and narrow down hardware symptoms. The value is a shorter feedback loop and a manageable learning surface, rather than a promise of unattended debugging or that every generated program will work.

## Example prompts

> Using the pin table and `src/mactouch/` code, add a visual countdown timer control. Keep it within 320×240, reuse the existing button style, and preserve notes and drawings. Explain the changed files and how I should verify it on the device.

> Here is a serial error from the SD save operation. Explain the likely causes, identify the next read-only checks, and suggest the smallest change supported by the log. Do not format the card or replace the working guest disk.

> Explain how `src/viewport/` maps stylus coordinates in Fit and 1x. Propose a small improvement and use the synthetic viewport checks before I build firmware.

## Keep expectations concrete

Small screen-native experiments are good first projects. A later Macintosh game may still need more guest RAM, a different operating system, unsupported input or sound hardware. AI assistance does not remove those limits or grant rights to third-party software. Begin with the original touch applications, then explore lower-level changes as your confidence grows.

No AI subscription or API key is required to run the supplied project code. If you choose an external assistant, its access and costs are separate from the DIY hardware kit.
