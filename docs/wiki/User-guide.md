# User guide

[Documentation home](Home.md) · [Build and install](../BUILD.md) · [Software and storage](Software-and-storage.md)

This guide describes an installed, calibrated device. For a new board, complete the build and bootstrap installation first.

## 1. Choose an environment

At startup, select **MacTouch** for the miniature touch desktop or **Macintosh** for emulation. The prototype's smile and `hello.` screen is shown below; public source uses an original terminal graphic instead.

![Prototype startup selection](../screenshots/boot-01-selector.png)

The menu loads the chosen application from SD into its reserved flash partition. It preserves the boot menu and MicroPython filesystem. Let loading finish before using the stylus. To choose again, reset the board or power-cycle it after saving your work. MacTouch also has a **Boot Menu** icon on its second desktop page; the emulator has a serial `menu` command for development.

## 2. Use MacTouch

Tap an icon to open an application. Follow the on-screen controls and use the window's close control to return to the desktop. On first setup, tap each calibration target at its center and lift the stylus fully between targets.

| Application | Try this |
|---|---|
| **Paint** | Draw with Pen, erase with Rub, use Fill and select a pattern. Save to SD and reopen the result through Gallery. |
| **Paint Zoom** | Zoom to 4x; drag to move the view or use the small navigator to choose a region. Select Pen for editing, then return to 1x for the whole drawing. |
| **Gallery** | Browse drawings saved by Paint and open a stored picture. |
| **Notes** | Enter text with the on-screen keyboard, then Save. Open reads a saved note. |
| **Maze / Puzzle** | Tap an adjacent maze cell or a tile beside the empty space. Maze includes a Hint control. |
| **Cards** | Follow the choices in an original interactive card story. |
| **Puck** | Drag the paddle to return the puck. |
| **Glider** | Hold Lift or touch the sky to gain height; avoid the shelves. |
| **Castle** | Use the Left, Right, Jump and Throw controls. |

| Paint and its navigator | Notes and keyboard |
|---|---|
| ![Paint in zoom mode](../screenshots/touch-05-paint-zoom.png) | ![Notes sample](../screenshots/touch-11-notes.png) |

These are screen-sized original/reimplemented miniatures. They do not load Macintosh applications or share the emulator's guest files.

## 3. Use the Macintosh environment

The stylus acts as the mouse: touch to press, move while touching to drag, and lift to release. Double-tap an application icon to launch it. For an early Macintosh menu, **press the menu title, slide to the item, then lift**. This differs from a modern click-to-open menu.

Applications installed in your guest disk can be grouped in a Finder folder such as `Games`. Opening another program from that folder does not require selecting a different firmware at startup. Quit the current application through its own menu before launching another; the tested system runs applications one at a time.

### Understand the bottom toolbar

| Control | Action |
|---|---|
| **Fit / 1x** | The label is the view you can switch to. Fit shows the entire 512×342 guest screen; 1x shows original pixels in a 320×222 viewport. |
| **Pan** | Enters 1x and toggles drag-to-pan. Turn it off before clicking or drawing inside the guest. |
| **Four arrows** | Move the 1x viewport left, right, up or down. These move the view, not the guest mouse or application window. |
| **Top** | Return to 1x at the desktop's top-left corner and leave Pan. |
| **A / M status** | A means the application's default, M means a manual preference. Tap this area to restore that application's default. |

| Whole scene in Fit | Read a dialog at 1x |
|---|---|
| ![Blackjack full hand](../screenshots/native-03-blackjack-hand-fit.png) | ![Blackjack dialog at original pixel size](../screenshots/native-04-blackjack-hand-detail.png) |

Finder and unknown application names default to 1x. Seven exact-name game profiles default to Fit: `MissileCommand`, `Daleks`, `Bubba`, `Break Bricks`, `BlackBox`, `Blackjack` and `Brickles 5.0`. This is a display preference list, not a bundled collection or a promise of full compatibility. Renaming an application may stop its profile from matching.

Manual mode and viewport origin are remembered per application for the current power-on session. Fit makes text smaller; 1x necessarily shows only part of the guest screen. The controls balance these two constraints without changing the applications themselves.

## 4. Save and switch safely

Save drawings, notes or guest documents before resetting. SD storage is shared by the firmware environments, but their application data has different formats. For computer access to the card, return to PicoBoot and enter serial **`maintenance`** first; this pauses its touch UI. Never write the card from the computer while an application environment is using it.

## Common questions

| Symptom | What to check |
|---|---|
| Touch is offset | Recalibrate your screen. Example coefficients were measured on one prototype and are not universal. Native and boot-menu calibration also need matching configuration. |
| A dialog or game control is outside the view | Select Fit to locate it, or use 1x + Pan/arrows to reach it. Many early applications have fixed layouts rather than modern maximize controls. |
| Dragging moves the view instead of the application | Turn Pan off. |
| MacTouch cannot start | Check FAT32/SPI mode, `/MACAPPS`, and the three internal bootstrap modules. Read the MicroPython serial error; startup failure does not format the card. |
| The Macintosh system reports an error | Record the application, action and any error code. Compatibility is limited by RAM and emulated hardware. The quiet-beep patch prevents the observed volume-preview error; it does not provide sound or fix every system error. |
