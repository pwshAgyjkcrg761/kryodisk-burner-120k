# <img src="KryoDisk-Burner-120K_internal/icons/kryodisk-burner-120k-icon.svg" width="32" height="32"> KryoDisk Burner 120K™ <img src="KryoDisk-Burner-120K_internal/icons/kryodisk-burner-120k-icon.svg" width="32" height="32">
**A high-performance optical disc authoring and burning utility supporting CD, DVD, Blu-ray, and BDXL media formatted in UDF 2.50.**

---

![KryoDisk Burner 120K Dark Mode Main Interface](images/KryoDisk-py_dark_mode_main.png)

## Overview
KryoDisk Burner 120K™ is an optical disc mastering and burning application for Windows. Utilizing the Windows Image Mastering API v2.0 (IMAPI2) engine, it authors compliant **Universal Disk Format (UDF 2.50)** virtual file systems and writes them directly to CD, DVD, Blu-ray (BD-R/RE), and high-density BDXL media (up to 128GB Quad-Layer).

**Primary Environment:** Developed and tested on **Python 3.14.5** using the **PyQt6** framework and **pywin32** COM interfaces. It is designed for archivists, system administrators, and storage specialists who require reliable optical media authoring, flexible multisession management, and seamless post-burn cryptographic integrity verification.

### The Authoring & Burning Engine
The utility couples direct COM-level hardware communication with an intuitive dual-pane disc layout manager and automated post-burn verification.

Key operational features include:
1. **Universal Optical Media Support:** Authors and burns to all standard optical formats: CD-R, CD-RW, DVD-R, DVD+R, DVD-RW, DVD+RW, DVD±R DL (Dual Layer), DVD-RAM, BD-R, BD-RE, BD-R DL (50GB), BD-R TL (100GB BDXL), and BD-R QL (128GB BDXL).
2. **Dual-Pane Staging Browser:** Structure your disc hierarchy using a dedicated left navigation tree and right contents view. Organize files, inspect deep folder structures, and create custom directory layouts before committing to disc.
3. **Dual-Explorer Add Dialog:** Browse local drives and stage multiple files and directories simultaneously through an integrated dual-pane file and folder picker.
4. **Administrator & Hardware Elevation:** Operates with Administrator privileges to secure exclusive hardware access to optical burner drives and prevent `0x80070005 E_ACCESSDENIED` device lock errors. *(Note: Direct drag-and-drop from standard Windows Explorer is restricted by Windows UIPI when running in elevated mode; use the built-in Add dialog or SendTo menu).*
5. **Real-Time Capacity Gauging:** Dynamically gauges staged payload sizes against inserted optical disc capacity, complete with visual color changes and over-capacity warnings.
6. **Multisession & Session Importing:** Supports appending data to open multisession discs. Automatically queries, discovers, and maps previous disc sessions directly into the staging browser.
7. **Disc Finalization Control:** Choose between keeping media appendable or finalizing the disc to lock tracks for maximum playback compatibility on standard ROM drives and consumer players.
8. **Hardware Tray Eject & Motorized Close:** Direct hardware controls to eject (⏏) and close/load (📥) optical drive trays via kernel IOCTL and MCI interfaces.
9. **Dynamic Write Speed Configuration:** Queries the drive's firmware to expose valid write speed descriptors (e.g. 1x, 2x, 4x, 8x, 16x, 24x) alongside automatic maximum speed handling.
10. **Integrated Post-Burn Verification:** When enabled, automatically scans the burned disc for checksum manifests (`.hash`, `.sha256`, `.b3`, `.blake3`, etc.) and launches **KryptDist** to execute bit-level cryptographic verification.
11. **Embedded Progress & Live Telemetry:** Real-time progress monitoring featuring rolling write-speed calculation (MB/s), sector progress, accurate lead-out ETA countdowns, and a detailed scrolling event log.
12. **Themed UI & Notification Preferences:** Full support for Dark, Light, and System-synced palettes, paired with an option under **Tools > Preferences** to mute completion chimes while preserving visual confirmation dialogs.
13. **Persistent UI State:** Remembers window geometry, write speed preferences, disc labels, verification settings, and theme configurations across sessions.

---

## Feature Reference

| Option / Feature | Description |
| :--- | :--- |
| **UDF 2.50 Mastering** | Builds compliant Universal Disk Format 2.50 virtual file systems for universal high-capacity optical compatibility. |
| **BDXL & Multi-Format Support** | Complete support for CD, DVD, Blu-ray, and multi-layer BDXL media up to 128GB Quad-Layer (QL). |
| **Dual-Pane Layout Browser** | Split hierarchical browser for organizing virtual disc directories and staged payloads. |
| **Dual-Explorer Add Dialog** | Simultaneous file and directory picker for quick batch staging. |
| **Live Capacity Meter** | Real-time visual capacity bar displaying payload usage against media capacity with overload warnings. |
| **Multisession Support** | Retains open disc state for appending additional sessions, automatically importing pre-existing disc contents. |
| **Disc Finalization** | Closes and finalizes disc tracks to ensure broad read compatibility across standard optical drives. |
| **Hardware Tray Controls** | Direct software-driven drive tray eject (⏏) and motorized tray close (📥) commands. |
| **Hardware Speed Descriptors** | Dynamically queries drive firmware for supported disc write multipliers. |
| **KryptDist Post-Burn Check** | Scans burned discs for `.hash` containers and verifies 100% data integrity post-burn. |
| **Real-Time Write Telemetry** | Displays rolling write speed (MB/s), sector tracking, elapsed time, and realistic completion countdowns. |
| **Theme Engine** | Full support for Dark, Light, and System-synced palettes via custom `QPalette` implementation. |
| **Sound Suppression Option** | Mutes completion and alert notification sounds while retaining visual status badges. |

---

## Post-Burn Verification Integration

KryoDisk Burner 120K seamlessly pairs with **KryptDist** for end-to-end data integrity validation:
1. Place a `.hash` manifest (or any supported checksum file) inside your staging payload.
2. Ensure `Verify Disc After Burn with KryptDist` is checked.
3. Upon burn completion, KryoDisk Burner detects the container on the optical disc and invokes `KryptDist.py` headlessly or via OSD to verify every file bit-by-bit.
4. If `Eject Disc When Complete` is checked, disc ejection is safely deferred until verification passes with 100% integrity.

---

## Assets & Licensing
This software is released under the **GNU General Public License v3**.

### Icon Credits
* **File:** `kryodisk-burner-120k-icon.svg`
    * **Asset:** Fire SVG Vector
    * **Source:** <a href="https://www.svgrepo.com/svg/506715/fire" target="_blank">https://www.svgrepo.com/svg/506715/fire</a>
    * **License:** <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank">CC0 License</a>
    * **Modifications:** Modified by pwshAgyjkcrg761.

---

## Dependencies
* **OS:** Microsoft Windows 10 / 11 / Windows Server (64-bit).
* **Privileges:** Administrator privileges required for exclusive IMAPI2 optical device access.
* **Python:** 3.14.5+ (Recommended).
* **PyQt6:** Required for the Graphical User Interface framework (`pip install PyQt6`).
* **pywin32:** Required for Windows IMAPI2 COM interfaces (`pip install pywin32`).
* **Hardware:** Any compatible internal (SATA/ATAPI) or external (USB) optical burner drive.
* **Optional Tooling:** `KryptDist.py` (located in the application directory, `C:\scripts\`, or system `PATH`) for automated post-burn cryptographic checksum verification.

## Support & Maintenance
**This repository is provided "as-is" for archival purposes.** The author is not actively looking for feedback, feature requests, or bug reports. The issue tracker is disabled.

## Disclaimer
*KryoDisk Burner 120K™ is an optical disc authoring and burning utility. Burning to write-once optical media (CD-R, DVD-R, BD-R) involves permanent physical modification of the disc. The author is not responsible for failed burns, drive hardware faults, or data loss resulting from hardware failure or improper handling. Always verify critical backups.*

---
> **Document Control**<br>
> *This document is up-to-date with the following version of KryoDisk Burner 120K™.*<br>
> *2026.09.10__16.55.50*