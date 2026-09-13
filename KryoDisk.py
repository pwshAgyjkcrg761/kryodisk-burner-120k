# ==============================================================================
# SCRIPT: KryoDisk.py
# VERSION: 2026.09.13__09.03.09
# TARGET: Python 3.14.5
#
# Copyright (C) 2026 pwshAgyjkcrg761
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
# ==============================================================================
# <PROTECTED>
# ==============================================================================
# AI INSTRUCTIONS
# Copyright (c) 2026 pwshAgyjkcrg761
# License: MIT
# Source: https://git.disroot.org/pwshAgyjkcrg761/AI_Instructions
#
# AI INSTRUCTIONS v2026.09.01__04.25.09 : 
#
# 1. MESSAGE STAMP: 
#    - Every response containing code MUST begin with a standalone version stamp.
#    - Use CHICAGO TIME (Central Time), 24-hour clock.
#    - Format: YYYY.MM.DD__HH.MM.SS.
#    - CRITICAL: Use the time provided in the prompt or at 
#      https://www.timeanddate.com/worldclock/usa/chicago. Ensure minutes are exact.
#
# 2. VERSION SNIPPET PROHIBITION:
#    - DO NOT provide code snippets, anchors, or steps to update the script's 
#      internal VERSION comment or $scriptVersion variable. 
#    - The user handles internal file versioning manually based on the Message Stamp.
#
# 3. SCRIPT OUTPUT (SURGICAL FIXES ONLY):
#    - Provide minimal, highly targeted, surgical edits. Do not rewrite large blocks or 
#      entire functions.
#    - Always use a codebox with a copy button.
#    - Multiple modifications MUST be presented strictly ONE step at a time. Wait for 
#      user confirmation before proceeding to the next step. 
#    - DO NOT modify or refactor any code inside <PROTECTED> tags.
#
# 4. VERBATIM ANCHOR PROTOCOL (FOR NOTEPAD++):
#    - To facilitate "Find" in Notepad++, always structure edits with:
#      - "Verbatim Anchor (Before)" - The exact lines of existing code immediately before 
#         the change.
#      - "Verbatim Anchor (After)" - The exact lines of existing code immediately after 
#         the change.
#      - "Snippet to REPLACE" - The exact code block to be deleted.
#      - "What to PASTE in its place" - The new code block to be inserted.
#    - Do not summarize, truncate, or refactor the existing code used as an anchor.
#    - Match spaces, comments, and symbols exactly as they appear in the file.
#
# 5. CONTENT PRESERVATION:
#    - Do not remove, modify, or strip out telemetry data or DevDebug information from any 
#      provided code.
# ==============================================================================
# </PROTECTED>

import sys
import os
import json
import re
import ctypes

APP_VERSION = "2026.09.13__09.03.09"

DEV_DEBUG = any(arg.lower() in ("-devdebug", "--devdebug", "/devdebug") for arg in sys.argv)

NO_DRIVE_SCAN = DEV_DEBUG and any(arg.lower() in (
    "-nodrivescan", "--nodrivescan", "/nodrivescan",
    "-noscan", "--noscan", "/noscan",
    "-skipdrivescan", "--skipdrivescan", "/skipdrivescan"
) for arg in sys.argv)

def natural_sort_key(s):
    """Sort strings containing numbers in human/natural order safely across types."""
    return [(0, int(t)) if t.isdigit() else (1, t.lower()) for t in re.split(r'(\d+)', str(s))]





import shutil
import subprocess

try:
    import win32com.client
    import pythoncom
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

# IMAPI2 Media Physical Types (IMAPI_MEDIA_PHYSICAL_TYPE)
IMAPI_MEDIA_NAMES = {
    0: "Unknown Media",
    1: "CD-ROM",
    2: "CD-R",
    3: "CD-RW",
    4: "DVD-ROM",
    5: "DVD-RAM",
    6: "DVD+R",
    7: "DVD+RW",
    8: "DVD+R Dual Layer",
    9: "DVD-R",
    10: "DVD-RW",
    11: "DVD-R Dual Layer",
    12: "Disk Media",
    13: "DVD+RW Dual Layer",
    14: "HD DVD-ROM",
    15: "HD DVD-R",
    16: "HD DVD-RAM",
    17: "BD-ROM",
    18: "BD-R",
    19: "BD-RE"
}

def format_byte_size(num_bytes):
    """Formats bytes into human-readable binary units (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"

def locate_cdbxpcmd(custom_path=None):
    """Finds cdbxpcmd.exe (CDBurnerXP CLI) across custom path, PATH, Registry, internal bin, and tools directories."""
    if custom_path and os.path.isfile(custom_path):
        return os.path.normpath(custom_path)

    candidate_names = ["cdbxpcmd.exe"]

    # 1. Check system PATH
    for name in candidate_names:
        found = shutil.which(name)
        if found and os.path.isfile(found):
            return os.path.normpath(found)

    # 2. Check fresh Registry PATH entries
    if sys.platform == "win32":
        try:
            import winreg
            reg_paths = []
            for hkey, subkey in [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                (winreg.HKEY_CURRENT_USER, r"Environment")
            ]:
                try:
                    with winreg.OpenKey(hkey, subkey) as k:
                        val, _ = winreg.QueryValueEx(k, "Path")
                        if val:
                            reg_paths.extend(val.split(os.pathsep))
                except Exception:
                    pass

            for p_dir in reg_paths:
                p_dir_clean = os.path.expandvars(p_dir.strip().strip('"'))
                if p_dir_clean and os.path.isdir(p_dir_clean):
                    candidate = os.path.join(p_dir_clean, "cdbxpcmd.exe")
                    if os.path.isfile(candidate):
                        return os.path.normpath(candidate)
        except Exception:
            pass

    # 3. Check KryoDisk internal bin directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    internal_candidates = [
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "CDBurnerXP", "cdbxpcmd.exe"),
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "cdbxpcmd.exe")
    ]
    for c in internal_candidates:
        if os.path.isfile(c):
            return os.path.normpath(c)

    # 4. Check C:\tools and standard Program Files
    tools_candidates = [
        r"C:\tools\CDBurnerXP\cdbxpcmd.exe",
        r"C:\tools\CDBurnerXPPortable\cdbxpcmd.exe",
        r"C:\Program Files\CDBurnerXP\cdbxpcmd.exe",
        r"C:\Program Files (x86)\CDBurnerXP\cdbxpcmd.exe"
    ]
    for c in tools_candidates:
        if os.path.isfile(c):
            return os.path.normpath(c)

    return None

def locate_imgburn(custom_path=None):
    """Finds ImgBurn / ImgBurnPortable executable across custom path, PATH, Registry, and tool directories."""
    if custom_path and os.path.isfile(custom_path):
        return os.path.normpath(custom_path)

    candidate_names = ["ImgBurnPortable.exe", "ImageBurnPortable.exe", "ImgBurn.exe"]

    # 1. Check system PATH
    for name in candidate_names:
        found = shutil.which(name)
        if found and os.path.isfile(found):
            return os.path.normpath(found)

    # 2. Check fresh Registry PATH entries (handles additions made before system reboot)
    if sys.platform == "win32":
        try:
            import winreg
            reg_paths = []
            for hkey, subkey in [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                (winreg.HKEY_CURRENT_USER, r"Environment")
            ]:
                try:
                    with winreg.OpenKey(hkey, subkey) as k:
                        val, _ = winreg.QueryValueEx(k, "Path")
                        if val:
                            reg_paths.extend(val.split(os.pathsep))
                except Exception:
                    pass

            for p_dir in reg_paths:
                p_dir_clean = os.path.expandvars(p_dir.strip().strip('"'))
                if p_dir_clean and os.path.isdir(p_dir_clean):
                    for name in candidate_names:
                        candidate = os.path.join(p_dir_clean, name)
                        if os.path.isfile(candidate):
                            return os.path.normpath(candidate)
        except Exception:
            pass

    # 3. Check KryoDisk internal bin directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    internal_candidates = [
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "ImgBurnPortable", "ImageBurnPortable.exe"),
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "ImgBurnPortable", "ImgBurnPortable.exe"),
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "ImgBurnPortable", "App", "ImgBurn", "ImgBurn.exe"),
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "ImgBurn", "ImgBurn.exe")
    ]
    for c in internal_candidates:
        if os.path.isfile(c):
            return os.path.normpath(c)

    # 4. Check C:\tools\ImgBurnPortable locations
    tools_candidates = [
        r"C:\tools\ImgBurnPortable\ImgBurnPortable.exe",
        r"C:\tools\ImgBurnPortable\ImageBurnPortable.exe",
        r"C:\tools\ImgBurnPortable\App\ImgBurn\ImgBurn.exe",
        r"C:\tools\ImgBurn\ImgBurn.exe",
        r"C:\Program Files (x86)\ImgBurn\ImgBurn.exe",
        r"C:\Program Files\ImgBurn\ImgBurn.exe"
    ]
    for c in tools_candidates:
        if os.path.isfile(c):
            return os.path.normpath(c)

    return None

def locate_kryptdist(custom_path=None):
    """Finds KryptDist.py script across custom path, script dir, PATH, Registry, and standard tool locations."""
    if custom_path and os.path.isfile(custom_path):
        return os.path.normpath(custom_path)

    # 1. Check same directory as script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    c_local = os.path.join(script_dir, "KryptDist.py")
    if os.path.isfile(c_local):
        return os.path.normpath(c_local)

    # 2. Check system PATH
    found = shutil.which("KryptDist.py")
    if found and os.path.isfile(found):
        return os.path.normpath(found)

    # 3. Check fresh Registry PATH entries (handles additions made before reboot)
    if sys.platform == "win32":
        try:
            import winreg
            reg_paths = []
            for hkey, subkey in [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                (winreg.HKEY_CURRENT_USER, r"Environment")
            ]:
                try:
                    with winreg.OpenKey(hkey, subkey) as k:
                        val, _ = winreg.QueryValueEx(k, "Path")
                        if val:
                            reg_paths.extend(val.split(os.pathsep))
                except Exception:
                    pass

            for p_dir in reg_paths:
                p_dir_clean = os.path.expandvars(p_dir.strip().strip('"'))
                if p_dir_clean and os.path.isdir(p_dir_clean):
                    candidate = os.path.join(p_dir_clean, "KryptDist.py")
                    if os.path.isfile(candidate):
                        return os.path.normpath(candidate)
        except Exception:
            pass

    # 4. Check KryoDisk internal bin directory
    internal_candidates = [
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "KryptDist", "KryptDist.py"),
        os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "bin", "KryptDist.py")
    ]
    for c in internal_candidates:
        if os.path.isfile(c):
            return os.path.normpath(c)

    # 5. Check standard C:\scripts and C:\tools locations
    standard_candidates = [
        r"C:\scripts\KryptDist.py",
        r"C:\tools\KryptDist\KryptDist.py",
        r"C:\tools\KryptDist.py"
    ]
    for c in standard_candidates:
        if os.path.isfile(c):
            return os.path.normpath(c)

    return None

def get_optical_drives():
    """Enumerates optical disc burner drives connected to the system via Windows IMAPI2."""
    drives = []
    if not HAS_WIN32COM:
        if DEV_DEBUG:
            print("IMAPI2 Error: pywin32 (win32com.client) is not installed.")
        return drives

    pythoncom.CoInitialize()
    try:
        disc_master = win32com.client.Dispatch("IMAPI2.MsftDiscMaster2")
        count = int(disc_master.Count)
        if DEV_DEBUG:
            print(f"IMAPI2 DiscMaster reports {count} optical drive(s).")

        for i in range(count):
            unique_id = str(disc_master.Item(i))
            recorder = win32com.client.Dispatch("IMAPI2.MsftDiscRecorder2")
            initialized = False

            # Try primary unique ID initialization
            try:
                recorder.InitializeDiscRecorder(unique_id)
                initialized = True
            except Exception as init_err:
                err_code = getattr(init_err, 'hresult', None) or (init_err.args[2][5] if len(init_err.args) > 2 and isinstance(init_err.args[2], tuple) else None)
                if err_code == -2147024891: # 0x80070005 E_ACCESSDENIED
                    if DEV_DEBUG:
                        print(f"Access Denied on drive index {i}. Note: Running as Administrator may be required by Windows policy.")
                else:
                    if DEV_DEBUG:
                        print(f"Notice: Initializing by Unique ID failed ({init_err}), trying drive letter fallback...")

            # Fallback: scan drive letters (D: through Z:) if unique ID access failed
            if not initialized:
                import string
                for letter in string.ascii_uppercase[3:]:
                    drive_candidate = f"{letter}:"
                    if os.path.exists(drive_candidate):
                        try:
                            recorder.InitializeDiscRecorder(drive_candidate)
                            unique_id = drive_candidate
                            initialized = True
                            break
                        except Exception:
                            continue

            if not initialized:
                if DEV_DEBUG:
                    print(f"Could not initialize optical drive at index {i}.")
                continue

            # Query drive letter(s)
            drive_letter = ""
            try:
                vol_paths = recorder.VolumePathNames
                if vol_paths:
                    drive_letter = str(vol_paths[0]).rstrip('\\')
            except Exception:
                pass

            if not drive_letter:
                drive_letter = f"Drive {i+1}"

            vendor_id = ""
            product_id = ""
            try:
                vendor_id = str(recorder.VendorId).strip()
            except Exception:
                pass
            try:
                product_id = str(recorder.ProductId).strip()
            except Exception:
                pass

            model_str = f"{vendor_id} {product_id}".strip() or "Optical Burner"
            drive_name = f"{drive_letter} [{model_str}]"

            drives.append({
                "id": unique_id,
                "letter": drive_letter,
                "name": drive_name
            })
            if DEV_DEBUG:
                print(f"Successfully detected drive: {drive_name}")

    except Exception as e:
        if DEV_DEBUG:
            print(f"IMAPI2 master initialization error: {e}")
    finally:
        pythoncom.CoUninitialize()
    return drives

def get_drive_media_info(unique_id):
    """Queries optical disc type, blank status, and available capacity for a specific drive."""
    info = {
        "media_type_code": 0,
        "media_type_name": "No Disc / Unknown",
        "is_blank": False,
        "total_capacity_bytes": 0,
        "free_capacity_bytes": 0,
        "supported_speeds_raw": [],
        "is_supported": False
    }
    if not HAS_WIN32COM or not unique_id:
        return info

    pythoncom.CoInitialize()
    try:
        recorder = win32com.client.Dispatch("IMAPI2.MsftDiscRecorder2")
        recorder.InitializeDiscRecorder(unique_id)

        data_writer = win32com.client.Dispatch("IMAPI2.MsftDiscFormat2Data")
        if data_writer.IsRecorderSupported(recorder):
            info["is_supported"] = True
            data_writer.Recorder = recorder

            try:
                media_type = int(data_writer.CurrentPhysicalMediaType)
                info["media_type_code"] = media_type
                info["media_type_name"] = IMAPI_MEDIA_NAMES.get(media_type, f"Media Type {media_type}")
            except Exception:
                info["media_type_name"] = "No Disc Inserted"

            is_blank = False
            try:
                is_blank = bool(getattr(data_writer, 'MediaPhysicallyBlank', False) or getattr(data_writer, 'MediaHeuristicallyBlank', False))
            except Exception:
                try:
                    is_blank = bool(data_writer.MediaPhysicallyBlank)
                except Exception:
                    is_blank = False
            info["is_blank"] = is_blank

            sector_size = 2048
            raw_free_sectors = 0
            raw_total_sectors = 0
            try:
                raw_free_sectors = max(0, int(data_writer.FreeSectorsOnMedia))
            except Exception:
                raw_free_sectors = 0

            try:
                raw_total_sectors = max(0, int(data_writer.TotalSectorsOnMedia))
            except Exception:
                raw_total_sectors = 0

            media_code = info["media_type_code"]
            base_name = IMAPI_MEDIA_NAMES.get(media_code, info["media_type_name"])
            ref_sectors = max(raw_total_sectors, raw_free_sectors)

            # Standard capacity mapping using both media descriptors and sector thresholds
            is_rom = media_code in (1, 4, 14, 17) or "ROM" in base_name.upper()
            
            if media_code in (17, 18, 19) or "BD" in base_name.upper() or ref_sectors > 5_000_000:
                if ref_sectors <= 13_000_000:       # BD SL 25GB (23,866 MB / 23.31 GB)
                    standard_cap = 12_219_392 * sector_size
                    if "BD" not in base_name.upper():
                        info["media_type_name"] = "BD-R SL 25GB"
                elif ref_sectors <= 26_000_000:     # BD DL 50GB (47,732 MB / 46.61 GB)
                    standard_cap = 24_438_784 * sector_size
                    if "BD" not in base_name.upper():
                        info["media_type_name"] = "BD-R DL 50GB"
                elif ref_sectors <= 52_000_000:     # BD TL 100GB (95,464 MB / 93.23 GB)
                    standard_cap = 48_877_568 * sector_size
                    if "BD" not in base_name.upper():
                        info["media_type_name"] = "BD-R TL 100GB (BDXL)"
                else:                               # BD QL 128GB (122,192 MB / 119.33 GB)
                    standard_cap = 62_562_304 * sector_size
                    if "BD" not in base_name.upper():
                        info["media_type_name"] = "BD-R QL 128GB (BDXL)"

                info["total_capacity_bytes"] = standard_cap
                if is_blank:
                    info["free_capacity_bytes"] = standard_cap
                elif is_rom or raw_free_sectors == 0:
                    info["free_capacity_bytes"] = 0
                else:
                    info["free_capacity_bytes"] = raw_free_sectors * sector_size

            elif media_code in (4, 5, 6, 7, 8, 9, 10, 11, 13) or "DVD" in base_name.upper() or ref_sectors > 450_000:
                if media_code in (8, 11, 13) or ref_sectors > 2_500_000: # DVD DL (8.5GB)
                    standard_cap = 4_171_712 * sector_size
                else:                                                     # DVD SL (4.7GB)
                    standard_cap = 2_298_496 * sector_size

                info["total_capacity_bytes"] = standard_cap
                if is_blank:
                    info["free_capacity_bytes"] = standard_cap
                elif is_rom or raw_free_sectors == 0:
                    info["free_capacity_bytes"] = 0
                else:
                    info["free_capacity_bytes"] = raw_free_sectors * sector_size

            elif media_code in (1, 2, 3) or "CD" in base_name.upper() or (0 < ref_sectors <= 450_000):
                standard_cap = 360_000 * sector_size                     # CD 700MB
                info["total_capacity_bytes"] = standard_cap
                if is_blank:
                    info["free_capacity_bytes"] = standard_cap
                elif is_rom or raw_free_sectors == 0:
                    info["free_capacity_bytes"] = 0
                else:
                    info["free_capacity_bytes"] = raw_free_sectors * sector_size

            else:
                info["total_capacity_bytes"] = max(0, ref_sectors * sector_size)
                info["free_capacity_bytes"] = info["total_capacity_bytes"] if is_blank else (0 if is_rom else raw_free_sectors * sector_size)

            # Format detailed media designation across all CD, DVD, and Blu-ray formats
            ref_cap = max(info["total_capacity_bytes"], info["free_capacity_bytes"])

            if media_code in (1, 2, 3) or "CD" in base_name.upper():
                cap_mb = ref_cap / (1024.0 * 1024.0) if ref_cap > 0 else 0
                if 0 < cap_mb <= 250.0:
                    spec = "Mini 210MB"
                elif cap_mb > 750.0:
                    spec = f"{int(round(cap_mb / 50.0) * 50)}MB"
                else:
                    spec = "700MB"
                info["media_type_name"] = f"{base_name} {spec}"

            elif media_code in (4, 5, 6, 7, 8, 9, 10, 11, 13) or "DVD" in base_name.upper():
                cap_gb = ref_cap / (1024.0 ** 3) if ref_cap > 0 else 0
                clean_base = base_name.replace(" Dual Layer", "")
                if 0 < cap_gb <= 1.8:
                    spec = "Mini SL 1.4GB"
                elif 1.8 < cap_gb <= 3.2:
                    spec = "Mini DL 2.8GB"
                elif media_code in (8, 11, 13) or cap_gb > 5.5:
                    spec = "DL 8.5GB"
                elif media_code == 5 and cap_gb > 7.0:
                    spec = "DS 9.4GB"
                else:
                    spec = "SL 4.7GB"
                info["media_type_name"] = f"{clean_base} {spec}"

            elif media_code in (17, 18, 19) or "BD" in base_name.upper():
                cap_gb = ref_cap / (1024.0 ** 3) if ref_cap > 0 else 0
                if 0 < cap_gb <= 10.0:
                    spec = "Mini 7.5GB"
                elif cap_gb > 110.0:
                    spec = "QL 128GB (BDXL)"
                elif cap_gb > 75.0:
                    spec = "TL 100GB (BDXL)"
                elif cap_gb > 35.0:
                    spec = "DL 50GB"
                else:
                    spec = "SL 25GB"
                info["media_type_name"] = f"{base_name} {spec}"

            try:
                speeds = list(data_writer.SupportedWriteSpeeds)
                info["supported_speeds_raw"] = sorted(list(set(speeds)), reverse=True)
            except Exception:
                info["supported_speeds_raw"] = []
    except Exception as e:
        if DEV_DEBUG:
            print(f"IMAPI2 media info query error: {e}")
    finally:
        pythoncom.CoUninitialize()
    return info

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDir, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QMessageBox, 
                             QDialog, QCheckBox, QTextBrowser, QDialogButtonBox,
                             QComboBox, QProgressBar, QHBoxLayout, QListWidget,
                             QTabWidget, QLineEdit, QFormLayout, QTreeWidget,
                             QTreeWidgetItem, QSplitter, QHeaderView, QMenu,
                             QInputDialog, QTreeView, QAbstractItemView,
                             QStackedWidget)
from PyQt6.QtGui import (QActionGroup, QPalette, QColor, QIcon, QPixmap, QPainter, 
                         QPen, QFileSystemModel)


def get_status_pixmap(status="success", size=48):
    """Draws a crisp green checkmark or red X badge for dialog message boxes."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if status == "success":
        painter.setBrush(QColor("#28a745"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)

        pen = QPen(QColor("#ffffff"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(int(size * 0.28), int(size * 0.52), int(size * 0.44), int(size * 0.68))
        painter.drawLine(int(size * 0.44), int(size * 0.68), int(size * 0.72), int(size * 0.34))
    else:
        painter.setBrush(QColor("#dc3545"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)

        pen = QPen(QColor("#ffffff"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        margin = int(size * 0.30)
        painter.drawLine(margin, margin, size - margin, size - margin)
        painter.drawLine(size - margin, margin, margin, size - margin)

    painter.end()
    return pixmap


CHECKSUM_EXTS = (
    ".hash", ".b3", ".blake3", ".b2", ".blake2", ".blake2b", ".blake2s",
    ".sha512", ".sha256", ".sha3", ".sha3-256", ".sha3-512",
    ".xx3", ".xxh3", ".xxh", ".sha1", ".sha", ".md5", ".sfv", ".crc32", ".crc"
)



class SettingsWrapper:
    def __init__(self, config_path):
        self.path = config_path
        self.data = {}
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.data = json.load(f)
            except: pass
    def value(self, key, default):
        return self.data.get(key, default)
    def setValue(self, key, value):
        self.data[key] = value
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except: pass


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("Preferences")
        self.resize(580, 330)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "icons", "kryodisk-burner-120k-icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)

        # Tab 1: Options
        tab_options = QWidget()
        opt_layout = QVBoxLayout(tab_options)
        self.chk_disable_sound = QCheckBox("Disable Notification Sounds")
        self.chk_disable_sound.setToolTip("Mutes all audio chimes and notification sounds for completion alerts.")
        opt_layout.addWidget(self.chk_disable_sound)
        opt_layout.addStretch()
        self.tabs.addTab(tab_options, "Options")

        # Tab 2: Engines
        tab_engines = QWidget()
        eng_layout = QVBoxLayout(tab_engines)

        # CDBurnerXP CLI
        lbl_cdbxp = QLabel("<b>CDBurnerXP CLI (cdbxpcmd.exe):</b>")
        eng_layout.addWidget(lbl_cdbxp)
        cdbxp_row = QHBoxLayout()
        self.txt_cdbxp_path = QLineEdit()
        self.txt_cdbxp_path.setPlaceholderText("Auto-detect (System PATH, Registry, Internal bin, C:\\tools)")
        self.btn_browse_cdbxp = QPushButton("Browse...")
        self.btn_browse_cdbxp.clicked.connect(self.browse_cdbxp)
        self.btn_detect_cdbxp = QPushButton("Auto-Detect")
        self.btn_detect_cdbxp.clicked.connect(self.auto_detect_cdbxp)
        cdbxp_row.addWidget(self.txt_cdbxp_path, 1)
        cdbxp_row.addWidget(self.btn_browse_cdbxp)
        cdbxp_row.addWidget(self.btn_detect_cdbxp)
        eng_layout.addLayout(cdbxp_row)

        eng_layout.addSpacing(10)

        # ImgBurn
        lbl_imgburn = QLabel("<b>ImgBurn / ImgBurnPortable (ImgBurn.exe):</b>")
        eng_layout.addWidget(lbl_imgburn)
        imgburn_row = QHBoxLayout()
        self.txt_imgburn_path = QLineEdit()
        self.txt_imgburn_path.setPlaceholderText("Auto-detect (System PATH, Registry, Internal bin, C:\\tools)")
        self.btn_browse_imgburn = QPushButton("Browse...")
        self.btn_browse_imgburn.clicked.connect(self.browse_imgburn)
        self.btn_detect_imgburn = QPushButton("Auto-Detect")
        self.btn_detect_imgburn.clicked.connect(self.auto_detect_imgburn)
        imgburn_row.addWidget(self.txt_imgburn_path, 1)
        imgburn_row.addWidget(self.btn_browse_imgburn)
        imgburn_row.addWidget(self.btn_detect_imgburn)
        eng_layout.addLayout(imgburn_row)

        eng_layout.addSpacing(10)

        # KryptDist Verification Engine
        lbl_kryptdist = QLabel("<b>KryptDist Verifier (KryptDist.py):</b>")
        eng_layout.addWidget(lbl_kryptdist)
        kryptdist_row = QHBoxLayout()
        self.txt_kryptdist_path = QLineEdit()
        self.txt_kryptdist_path.setPlaceholderText("Auto-detect (System PATH, C:\\scripts, Internal bin, C:\\tools)")
        self.btn_browse_kryptdist = QPushButton("Browse...")
        self.btn_browse_kryptdist.clicked.connect(self.browse_kryptdist)
        self.btn_detect_kryptdist = QPushButton("Auto-Detect")
        self.btn_detect_kryptdist.clicked.connect(self.auto_detect_kryptdist)
        kryptdist_row.addWidget(self.txt_kryptdist_path, 1)
        kryptdist_row.addWidget(self.btn_browse_kryptdist)
        kryptdist_row.addWidget(self.btn_detect_kryptdist)
        eng_layout.addLayout(kryptdist_row)

        eng_layout.addStretch()
        self.tabs.addTab(tab_engines, "Engines")

        main_layout.addWidget(self.tabs)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_and_close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.load_values()

    def browse_cdbxp(self):
        curr = self.txt_cdbxp_path.text().strip() or os.getcwd()
        start_dir = os.path.dirname(curr) if os.path.isfile(curr) else (curr if os.path.isdir(curr) else os.getcwd())
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CDBurnerXP CLI (cdbxpcmd.exe)", start_dir, "Executable (cdbxpcmd.exe);;All Files (*.*)"
        )
        if path:
            self.txt_cdbxp_path.setText(os.path.normpath(path))

    def browse_imgburn(self):
        curr = self.txt_imgburn_path.text().strip() or os.getcwd()
        start_dir = os.path.dirname(curr) if os.path.isfile(curr) else (curr if os.path.isdir(curr) else os.getcwd())
        path, _ = QFileDialog.getOpenFileName(
            self, "Select ImgBurn Executable", start_dir, "Executables (*.exe);;All Files (*.*)"
        )
        if path:
            self.txt_imgburn_path.setText(os.path.normpath(path))

    def browse_kryptdist(self):
        curr = self.txt_kryptdist_path.text().strip() or os.getcwd()
        start_dir = os.path.dirname(curr) if os.path.isfile(curr) else (curr if os.path.isdir(curr) else os.getcwd())
        path, _ = QFileDialog.getOpenFileName(
            self, "Select KryptDist Script (KryptDist.py)", start_dir, "Python Script (KryptDist.py *.py);;All Files (*.*)"
        )
        if path:
            self.txt_kryptdist_path.setText(os.path.normpath(path))

    def auto_detect_cdbxp(self):
        detected = locate_cdbxpcmd()
        if detected:
            self.txt_cdbxp_path.setText(detected)
        else:
            self.txt_cdbxp_path.clear()
            self.txt_cdbxp_path.setPlaceholderText("Not found (Auto-detect failed)")

    def auto_detect_imgburn(self):
        detected = locate_imgburn()
        if detected:
            self.txt_imgburn_path.setText(detected)
        else:
            self.txt_imgburn_path.clear()
            self.txt_imgburn_path.setPlaceholderText("Not found (Auto-detect failed)")

    def auto_detect_kryptdist(self):
        detected = locate_kryptdist()
        if detected:
            self.txt_kryptdist_path.setText(detected)
        else:
            self.txt_kryptdist_path.clear()
            self.txt_kryptdist_path.setPlaceholderText("Not found (Auto-detect failed)")

    def load_values(self):
        if self.parent_app and hasattr(self.parent_app, 'settings'):
            s = self.parent_app.settings
            self.chk_disable_sound.setChecked(s.value("disable_notification_sounds", False))

            saved_cdbxp = s.value("custom_cdbxpcmd_path", "")
            if saved_cdbxp and os.path.isfile(saved_cdbxp):
                self.txt_cdbxp_path.setText(os.path.normpath(saved_cdbxp))
            else:
                detected = locate_cdbxpcmd()
                if detected:
                    self.txt_cdbxp_path.setText(detected)

            saved_imgburn = s.value("custom_imgburn_path", "")
            if saved_imgburn and os.path.isfile(saved_imgburn):
                self.txt_imgburn_path.setText(os.path.normpath(saved_imgburn))
            else:
                detected = locate_imgburn()
                if detected:
                    self.txt_imgburn_path.setText(detected)

            saved_krypt = s.value("custom_kryptdist_path", "")
            if saved_krypt and os.path.isfile(saved_krypt):
                self.txt_kryptdist_path.setText(os.path.normpath(saved_krypt))
            else:
                detected = locate_kryptdist()
                if detected:
                    self.txt_kryptdist_path.setText(detected)

    def save_and_close(self):
        if self.parent_app and hasattr(self.parent_app, 'settings'):
            s = self.parent_app.settings
            s.setValue("disable_notification_sounds", self.chk_disable_sound.isChecked())

            cdbxp_val = self.txt_cdbxp_path.text().strip()
            s.setValue("custom_cdbxpcmd_path", cdbxp_val if os.path.isfile(cdbxp_val) else "")

            imgburn_val = self.txt_imgburn_path.text().strip()
            s.setValue("custom_imgburn_path", imgburn_val if os.path.isfile(imgburn_val) else "")

            krypt_val = self.txt_kryptdist_path.text().strip()
            s.setValue("custom_kryptdist_path", krypt_val if os.path.isfile(krypt_val) else "")
        self.accept()


import tempfile

import time

class OpticalBurnWorker(QThread):
    status_update = pyqtSignal(str, str)
    progress_update = pyqtSignal(int, int, str, int, int)  # current, total, phase_msg, elapsed_sec, remaining_sec
    log_message = pyqtSignal(str)
    burn_finished = pyqtSignal(bool, str, str)

    def __init__(self, drive_id, drive_letter, staged_paths, volume_label="DATA_DISC",
                 udf_revision="2.50", eject_when_done=True, finalize_disc=True,
                 custom_cdbxpcmd_path=None, custom_imgburn_path=None):
        super().__init__()
        self.drive_id = drive_id
        self.drive_letter = drive_letter or ""
        self.staged_paths = staged_paths
        self.volume_label = volume_label or "DATA_DISC"
        self.udf_revision = udf_revision or "2.50"
        self.eject_when_done = eject_when_done
        self.finalize_disc = finalize_disc
        self.custom_cdbxpcmd_path = custom_cdbxpcmd_path
        self.custom_imgburn_path = custom_imgburn_path
        self._is_cancelled = False
        self._proc = None
        self.speed_label = "Maximum (Auto)"
        self.verify_after = False

    def cancel(self):
        self._is_cancelled = True
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass

    def log(self, text):
        t_str = time.strftime("%H:%M:%S")
        self.log_message.emit(f"[{t_str}] {text}")

    def run(self):
        target_dest = self.drive_letter.rstrip('\\')
        selected_engine = getattr(self, 'engine', 'cdbxpcmd').lower()
        start_time = time.time()

        if "cdbxp" in selected_engine:
            cdbxp_exe = locate_cdbxpcmd(self.custom_cdbxpcmd_path)
            if not cdbxp_exe:
                # Fallback to ImgBurn if CDBurnerXP not installed
                img_alt = locate_imgburn(self.custom_imgburn_path)
                if img_alt:
                    self.log("cdbxpcmd.exe not found. Falling back to ImgBurn engine.")
                    selected_engine = "imgburn"
                else:
                    self.burn_finished.emit(
                        False, target_dest,
                        "CDBurnerXP CLI (cdbxpcmd.exe) could not be found.\n\n"
                        "Please configure its path in Preferences -> Engines, place 'cdbxpcmd.exe' in 'C:\\tools\\CDBurnerXP\\' or in "
                        "'KryoDisk-Burner-120K_internal\\bin\\CDBurnerXP\\', or add it to system PATH."
                    )
                    return

        if "cdbxp" in selected_engine:
            cdbxp_exe = locate_cdbxpcmd(self.custom_cdbxpcmd_path)
            self.log(f"Using Burning Engine: CDBurnerXP CLI ({cdbxp_exe})")
            self.log(f"Optical Drive: {target_dest or 'Default'}")
            self.log(f"Volume Label: {self.volume_label} | Format: UDF")
            self.log(f"Write Speed: {self.speed_label}")

            # Query and resolve zero-based integer device index for cdbxpcmd
            device_arg = "0"
            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
                creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)

            if target_dest:
                try:
                    res = subprocess.run(
                        [cdbxp_exe, "--list-drives"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        startupinfo=startupinfo,
                        creationflags=creationflags
                    )
                    for line in res.stdout.splitlines():
                        if target_dest.upper() in line.upper() and "(" in line and ")" in line:
                            idx_str = line.split("(")[1].split(")")[0].strip()
                            if idx_str.isdigit():
                                device_arg = idx_str
                                break
                except Exception:
                    device_arg = "0"

            cmd = [
                cdbxp_exe,
                "--burn-data",
                f"-device:{device_arg}",
                f"-name:{self.volume_label[:32]}",
                "-format:udf"
            ]

            if self.finalize_disc:
                cmd.append("-close")

            if self.eject_when_done and not self.verify_after:
                cmd.append("-eject")

            # Parse speed
            if self.speed_label:
                spd_match = re.search(r'(\d+)\s*x', self.speed_label, re.IGNORECASE)
                if spd_match:
                    cmd.append(f"-speed:{spd_match.group(1)}")

            # Stage folders and loose files into CDBurnerXP arguments
            for p in self.staged_paths:
                clean_p = os.path.normpath(p)
                if not os.path.exists(clean_p):
                    continue
                if os.path.isdir(clean_p):
                    base_d = os.path.basename(clean_p)
                    cmd.append(f"-folder[\\{base_d}]:{clean_p}")
                else:
                    cmd.append(f"-file:{clean_p}")

            cmd_line_str = subprocess.list2cmdline(cmd)
            self.status_update.emit(f"Status: Burning UDF disc via CDBurnerXP...", target_dest)
            self.log(f"Executing: {cmd_line_str}")

            try:
                self._proc = subprocess.Popen(
                    cmd_line_str,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    encoding='utf-8',
                    errors='replace',
                    startupinfo=startupinfo,
                    creationflags=creationflags
                )

                current_pct = 0
                for line in iter(self._proc.stdout.readline, ''):
                    if self._is_cancelled:
                        self._proc.terminate()
                        self.log("Burn cancelled by user.")
                        self.burn_finished.emit(False, target_dest, "Operation cancelled by user.")
                        return

                    line_s = line.strip()
                    if line_s:
                        self.log(f"[cdbxp] {line_s}")
                        
                        # Parse numerical percentage from CDBurnerXP stream
                        pct_match = re.search(r'(\d{1,3})\s*%', line_s)
                        if pct_match:
                            current_pct = max(0, min(100, int(pct_match.group(1))))

                        if "Writing" in line_s or "Closing" in line_s or "Finalizing" in line_s:
                            self.status_update.emit(f"Status: {line_s}", target_dest)
                        elif pct_match:
                            self.status_update.emit(f"Status: Writing tracks ({current_pct}%)", target_dest)

                    elapsed = int(time.time() - start_time)
                    
                    # Calculate dynamic remaining time based on current percent
                    calc_remaining = 0
                    if current_pct > 0 and current_pct < 100:
                        total_est = int(elapsed / (current_pct / 100.0))
                        calc_remaining = max(1, total_est - elapsed)
                    elif current_pct >= 100:
                        calc_remaining = 0

                    phase_msg = f"Writing data ({current_pct}%)" if current_pct < 100 else "Finalizing disc session..."
                    self.progress_update.emit(current_pct, 100, phase_msg, elapsed, calc_remaining)

                self._proc.stdout.close()
                ret = self._proc.wait()

                if ret == 0:
                    elapsed_total = int(time.time() - start_time)
                    mins, secs = divmod(elapsed_total, 60)
                    self.log(f"CDBurnerXP completed successfully in {mins:02d}:{secs:02d}.")
                    self.progress_update.emit(100, 100, "Completed", elapsed_total, 0)
                    self.burn_finished.emit(True, target_dest, "")
                else:
                    self.log(f"CDBurnerXP exited with code {ret}.")
                    self.burn_finished.emit(False, target_dest, f"CDBurnerXP exited with code {ret}.")

            except Exception as e:
                self.log(f"CDBurnerXP burn error: {e}")
                self.burn_finished.emit(False, target_dest, str(e))
            return

        # ----------------- ImgBurn Engine Route -----------------
        imgburn_exe = locate_imgburn(self.custom_imgburn_path)
        if not imgburn_exe:
            self.burn_finished.emit(
                False, self.drive_letter,
                "ImgBurn executable could not be found.\n\n"
                "Please configure its path in Preferences -> Engines, place ImgBurnPortable in 'C:\\tools\\ImgBurnPortable\\' or in "
                "'KryoDisk-Burner-120K_internal\\bin\\ImgBurnPortable\\', or add it to system PATH."
            )
            return

        temp_dir = None
        try:
            if not target_dest:
                self.burn_finished.emit(False, "", "No destination drive letter specified for ImgBurn.")
                return

            self.log(f"Using Burning Engine: {os.path.basename(imgburn_exe)} ({imgburn_exe})")
            self.log(f"Optical Drive: {target_dest}")
            self.log(f"Volume Label: {self.volume_label} | File System: UDF {self.udf_revision}")
            self.log(f"Write Speed: {self.speed_label}")

            temp_dir = tempfile.mkdtemp(prefix="kryodisk_imgburn_")
            srclist_path = os.path.join(temp_dir, "sources.txt")
            log_path = os.path.join(temp_dir, "imgburn_session.log")
            settings_ini_path = os.path.join(temp_dir, "imgburn_settings.ini")

            with open(srclist_path, 'w', encoding='utf-8') as f:
                for p in self.staged_paths:
                    if os.path.exists(p):
                        f.write(f"{p}\n")
                        self.log(f"Staged payload: {os.path.basename(p) or p}")

            clean_speed = "MAX"
            if self.speed_label:
                spd_match = re.search(r'(\d+)\s*x', self.speed_label, re.IGNORECASE)
                if spd_match:
                    clean_speed = f"{spd_match.group(1)}x"
                elif self.speed_label.isdigit():
                    clean_speed = f"{self.speed_label}x"

            eject_flag = "YES" if (self.eject_when_done and not self.verify_after) else "NO"

            real_exe = imgburn_exe
            exe_dir = os.path.dirname(imgburn_exe)
            if os.path.basename(imgburn_exe).lower() in ("imgburnportable.exe", "imageburnportable.exe"):
                app_exe = os.path.join(exe_dir, "App", "ImgBurn", "ImgBurn.exe")
                if os.path.isfile(app_exe):
                    real_exe = app_exe

            cmd = [
                real_exe,
                "/MODE", "BUILD",
                "/BUILDINPUTMODE", "STANDARD",
                "/BUILDOUTPUTMODE", "DEVICE",
                "/SRCLIST", srclist_path,
                "/DEST", target_dest,
                "/FILESYSTEM", "3",                     # UDF only
                "/UDFREVISION", str(self.udf_revision),  # "2.50" or "2.60"
                "/VOLUMELABEL_UDF", self.volume_label[:32],
                "/SPEED", clean_speed,
                "/VERIFY", "NO",                        # Suppress redundant internal sector verify
                "/ROOTFOLDER", "NO",
                "/NOIMAGEDETAILS",
                "/OVERWRITE", "YES",
                "/EJECT", eject_flag,
                "/LOG", log_path,
                "/START",
                "/CLOSESUCCESS"
            ]

            self.status_update.emit(f"Status: Burning UDF {self.udf_revision} disc via ImgBurn...", target_dest)
            self.log(f"Executing ImgBurn: {' '.join(cmd)}")

            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
                creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)

            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            def _poll_and_hide_imgburn(target_pid):
                if sys.platform != "win32":
                    return None
                imgburn_data = {"pct": None, "title": ""}
                try:
                    user32 = ctypes.windll.user32
                    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

                    def _enum_cb(hwnd, _):
                        p_id = ctypes.c_ulong()
                        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p_id))
                        if p_id.value == target_pid:
                            if user32.IsWindowVisible(hwnd):
                                user32.ShowWindow(hwnd, 0)  # SW_HIDE
                                user32.PostMessageW(hwnd, 0x0111, 6, 0)  # IDYES
                                user32.PostMessageW(hwnd, 0x0111, 1, 0)  # IDOK

                            title_buf = ctypes.create_unicode_buffer(512)
                            length = user32.GetWindowTextW(hwnd, title_buf, 512)
                            if length > 0:
                                t_text = title_buf.value
                                pct_m = re.search(r'(\d{1,3})\s*%', t_text)
                                if pct_m:
                                    imgburn_data["pct"] = max(0, min(100, int(pct_m.group(1))))
                                    imgburn_data["title"] = t_text
                                elif "ImgBurn" in t_text and not imgburn_data["title"]:
                                    imgburn_data["title"] = t_text
                        return True

                    user32.EnumWindows(EnumWindowsProc(_enum_cb), 0)
                except Exception:
                    pass
                return imgburn_data

            last_pos = 0
            current_pct = 0
            while self._proc.poll() is None:
                if self._is_cancelled:
                    self._proc.terminate()
                    self.log("Burn cancelled by user.")
                    self.burn_finished.emit(False, target_dest, "Operation cancelled by user.")
                    return

                poll_info = None
                if self._proc and self._proc.pid:
                    poll_info = _poll_and_hide_imgburn(self._proc.pid)

                if poll_info and poll_info.get("pct") is not None:
                    current_pct = poll_info["pct"]

                if os.path.exists(log_path):
                    try:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as lf:
                            lf.seek(last_pos)
                            new_text = lf.read()
                            last_pos = lf.tell()
                            if new_text:
                                for line in new_text.splitlines():
                                    line_s = line.strip()
                                    if line_s:
                                        self.log(f"[ImgBurn] {line_s}")
                                        if "Writing" in line_s or "Filling Buffer" in line_s:
                                            self.status_update.emit(f"Status: {line_s}", target_dest)
                                        elif "Synchronising Cache" in line_s or "Finalising" in line_s:
                                            self.status_update.emit("Status: Finalizing disc session...", target_dest)
                    except Exception:
                        pass

                elapsed = int(time.time() - start_time)
                calc_remaining = 0
                if current_pct > 0 and current_pct < 100:
                    total_est = int(elapsed / (current_pct / 100.0))
                    calc_remaining = max(1, total_est - elapsed)

                phase_title = poll_info.get("title", "") if poll_info else ""
                clean_phase = phase_title.replace(" - ImgBurn", "").strip() if phase_title else ""
                phase_msg = clean_phase if clean_phase else (f"Writing data ({current_pct}%)" if current_pct > 0 else "Burning...")
                self.progress_update.emit(current_pct, 100, phase_msg, elapsed, calc_remaining)
                time.sleep(0.4)

            ret = self._proc.returncode
            if ret == 0:
                elapsed_total = int(time.time() - start_time)
                mins, secs = divmod(elapsed_total, 60)
                self.log(f"ImgBurn completed successfully in {mins:02d}:{secs:02d}.")
                self.progress_update.emit(100, 100, "Completed", elapsed_total, 0)
                self.burn_finished.emit(True, target_dest, "")
            else:
                self.log(f"ImgBurn exited with error code {ret}.")
                self.burn_finished.emit(False, target_dest, f"ImgBurn exited with error code {ret}.")

        except Exception as e:
            self.log(f"Burn process error: {e}")
            self.burn_finished.emit(False, self.drive_letter, str(e))
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass





class DiscEraseWorker(QThread):
    status_update = pyqtSignal(str)
    log_message = pyqtSignal(str)
    erase_finished = pyqtSignal(bool, str)

    def __init__(self, drive_id, drive_letter="", custom_cdbxp_path=None):
        super().__init__()
        self.drive_id = drive_id
        self.drive_letter = drive_letter
        self.custom_cdbxp_path = custom_cdbxp_path

    def run(self):
        target_dest = self.drive_letter.rstrip('\\')
        if not target_dest:
            self.erase_finished.emit(False, "No drive letter specified for erase.")
            return

        self.log_message.emit(f"Starting Quick Erase on BD-RE/Rewritable drive {target_dest}...")

        # 1. Direct raw sector zeroing of Volume Descriptors (LBA 0 to LBA 2048)
        wiped_sectors = False
        try:
            GENERIC_READ = 0x80000000
            GENERIC_WRITE = 0x40000000
            FILE_SHARE_READ = 1
            FILE_SHARE_WRITE = 2
            OPEN_EXISTING = 3
            FSCTL_LOCK_VOLUME = 0x00090018
            FSCTL_DISMOUNT_VOLUME = 0x00090020
            FSCTL_UNLOCK_VOLUME = 0x0009001C

            h_dev = ctypes.windll.kernel32.CreateFileW(
                f"\\\\.\\{target_dest}",
                GENERIC_READ | GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                0,
                None
            )
            if h_dev != -1:
                bytes_ret = ctypes.c_ulong(0)
                ctypes.windll.kernel32.DeviceIoControl(h_dev, FSCTL_LOCK_VOLUME, None, 0, None, 0, ctypes.byref(bytes_ret), None)
                ctypes.windll.kernel32.DeviceIoControl(h_dev, FSCTL_DISMOUNT_VOLUME, None, 0, None, 0, ctypes.byref(bytes_ret), None)

                # Overwrite first 4 MB (2,000 sectors of 2048 bytes) with zeroes
                zero_buf = ctypes.create_string_buffer(2048 * 2000)
                bytes_written = ctypes.c_ulong(0)
                res = ctypes.windll.kernel32.WriteFile(h_dev, zero_buf, len(zero_buf), ctypes.byref(bytes_written), None)
                ctypes.windll.kernel32.DeviceIoControl(h_dev, FSCTL_UNLOCK_VOLUME, None, 0, None, 0, ctypes.byref(bytes_ret), None)
                ctypes.windll.kernel32.CloseHandle(h_dev)
                if res:
                    wiped_sectors = True
                    self.log_message.emit("Primary UDF volume descriptors and anchor pointers zeroed successfully.")
        except Exception as e:
            self.log_message.emit(f"Direct raw sector wipe note: {e}")

        # 2. Native Windows Quick Format fallback if raw write was blocked by drive firmware
        if not wiped_sectors:
            self.log_message.emit("Performing Windows native UDF quick format...")
            try:
                cmd = f"format {target_dest} /FS:UDF /Q /V:DATA_DISC /Y"
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.returncode == 0:
                    wiped_sectors = True
                    self.log_message.emit("Native UDF quick format completed successfully.")
                else:
                    self.log_message.emit(f"Format output: {res.stdout.strip()} {res.stderr.strip()}")
            except Exception as fe:
                self.log_message.emit(f"Native format note: {fe}")

        if wiped_sectors:
            self.erase_finished.emit(True, "")
        else:
            self.erase_finished.emit(False, "Failed to zero volume descriptors on BD-RE media.")


class KryptDistVerifyWorker(QThread):
    status_update = pyqtSignal(str, str)
    progress_update = pyqtSignal(int, int, str, int, int)
    finished = pyqtSignal(bool, int, str)
    log_message = pyqtSignal(str)

    def __init__(self, kryptdist_path, hash_path):
        super().__init__()
        self.kryptdist_path = kryptdist_path
        self.hash_path = hash_path
        self._proc = None
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass

    def run(self):
        try:
            self._proc = subprocess.Popen(
                [sys.executable, self.kryptdist_path, "--headless", self.hash_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )

            for line in iter(self._proc.stdout.readline, ''):
                if self._is_cancelled:
                    self._proc.terminate()
                    self.finished.emit(False, -1, self.hash_path)
                    return

                line_s = line.strip()
                if not line_s:
                    continue

                if line_s.startswith("VERIFY_PROGRESS:"):
                    parts = line_s.split(":", 5)
                    if len(parts) >= 6:
                        try:
                            bytes_done = int(parts[1])
                            total_bytes = int(parts[2])
                            elapsed_sec = int(parts[3])
                            eta_sec = int(parts[4])
                            curr_file = parts[5]

                            pct = int((bytes_done / total_bytes) * 100) if total_bytes > 0 else 0
                            speed_mb = (bytes_done / (1024.0 * 1024.0)) / max(1, elapsed_sec)
                            phase = f"Verifying data ({pct}%) - {speed_mb:.1f} MB/s"
                            self.status_update.emit(f"Status: {phase}", curr_file)
                            self.progress_update.emit(pct, 100, phase, elapsed_sec, eta_sec)
                        except Exception:
                            pass
                else:
                    self.log_message.emit(f"[KryptDist] {line_s}")

            self._proc.stdout.close()
            ret = self._proc.wait()
            self.finished.emit(ret == 0, ret, self.hash_path)
        except Exception as e:
            self.log_message.emit(f"Verification execution error: {e}")
            self.finished.emit(False, -1, self.hash_path)


def compute_path_size(path):
    """Calculates byte size of a file or directory recursively."""
    if not os.path.exists(path):
        return 0
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    except Exception:
        pass
    return total

class DiscTreePane(QTreeWidget):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.DropOnly)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                p = os.path.normpath(url.toLocalFile()).replace('/', os.sep)
                if p and os.path.exists(p):
                    paths.append(p)
            if paths:
                self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

class DiscTableItem(QTreeWidgetItem):
    """Custom QTreeWidgetItem that sorts by natural order and raw byte sizes."""
    def __lt__(self, other):
        tree = self.treeWidget()
        col = tree.sortColumn() if tree else 0
        if col == 1:
            d1 = self.data(0, Qt.ItemDataRole.UserRole) or {}
            d2 = other.data(0, Qt.ItemDataRole.UserRole) or {}
            return d1.get("size_bytes", 0) < d2.get("size_bytes", 0)
        return natural_sort_key(self.text(col)) < natural_sort_key(other.text(col))

class DiscBrowserWidget(QWidget):
    payload_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left Tree: Disc Root & Folders
        self.left_tree = DiscTreePane()
        self.left_tree.setHeaderLabels(["Disc Structure"])
        self.left_tree.header().setStretchLastSection(True)
        self.left_tree.files_dropped.connect(self.add_paths)

        # 2. Right Table: Files & Subfolders in Selected Directory
        self.right_table = DiscTreePane()
        self.right_table.setHeaderLabels(["Name", "Size", "Type", "Original Path"])
        self.right_table.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.right_table.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.right_table.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.right_table.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.right_table.setColumnWidth(0, 200)
        self.right_table.setColumnWidth(1, 90)
        self.right_table.setColumnWidth(2, 80)
        self.right_table.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.right_table.setSortingEnabled(True)
        self.right_table.header().setSectionsClickable(True)
        self.right_table.header().setSortIndicatorShown(True)
        self.right_table.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.right_table.files_dropped.connect(self.add_paths)

        # Root Disc Node
        self.root_node = QTreeWidgetItem(self.left_tree, ["💽 DATA_DISC"])
        self.root_node.setData(0, Qt.ItemDataRole.UserRole, {"is_root": True, "items": []})

        # Connect signals after both widgets are instantiated
        self.left_tree.currentItemChanged.connect(self.on_folder_selected)
        self.right_table.itemDoubleClicked.connect(self.on_right_item_double_clicked)
        self.left_tree.setCurrentItem(self.root_node)

        self.splitter.addWidget(self.left_tree)
        self.splitter.addWidget(self.right_table)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setSizes([240, 480])

        layout.addWidget(self.splitter)

    def set_volume_label(self, label):
        self.volume_label = label.strip() or "DATA_DISC"
        self.root_node.setText(0, f"💽 {self.volume_label}")

    def get_current_folder_node(self):
        current = self.left_tree.currentItem()
        return current if current is not None else self.root_node

    def on_folder_selected(self, current, previous):
        self.refresh_right_table(current)

    def on_right_item_double_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if data.get("is_dir"):
            folder_name = data.get("name")
            target_path = data.get("path")
            current_node = self.get_current_folder_node()
            
            # Find matching child in left tree
            for i in range(current_node.childCount()):
                child = current_node.child(i)
                cdata = child.data(0, Qt.ItemDataRole.UserRole) or {}
                if cdata.get("name") == folder_name or cdata.get("path") == target_path:
                    self.left_tree.setCurrentItem(child)
                    return

            # If not yet added as child node, add and select it
            child_node = QTreeWidgetItem(current_node, [f"📁 {folder_name}"])
            child_node.setData(0, Qt.ItemDataRole.UserRole, data)
            current_node.setExpanded(True)
            self.left_tree.setCurrentItem(child_node)

    def refresh_right_table(self, folder_node=None):
        self.right_table.setSortingEnabled(False)
        self.right_table.clear()
        if folder_node is None:
            folder_node = self.get_current_folder_node()
        if not folder_node:
            self.right_table.setSortingEnabled(True)
            return

        data = folder_node.data(0, Qt.ItemDataRole.UserRole) or {}
        folder_path = data.get("path", "")
        items = list(data.get("items", []))

        # If this node represents a real directory on disk / disc, enumerate its contents
        if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
            existing_names = {it["name"] for it in items}
            try:
                for entry in sorted(os.listdir(folder_path), key=natural_sort_key):
                    if entry in existing_names:
                        continue
                    full_p = os.path.join(folder_path, entry)
                    is_d = os.path.isdir(full_p)
                    size_b = compute_path_size(full_p)
                    is_disc = data.get("is_on_disc", False)
                    items.append({
                        "name": entry,
                        "path": full_p,
                        "is_dir": is_d,
                        "size_bytes": size_b,
                        "is_on_disc": is_disc
                    })
            except Exception:
                pass

        for itm in items:
            name = itm["name"]
            is_dir = itm["is_dir"]
            size_b = itm["size_bytes"]
            orig_path = itm["path"]
            is_on_disc = itm.get("is_on_disc", False)

            if is_on_disc:
                icon_prefix = "💿 " if is_dir else "💿 "
                type_str = "Disc Folder" if is_dir else f"Disc {os.path.splitext(name)[1].upper() or 'File'}"
            else:
                icon_prefix = "📁 " if is_dir else "📄 "
                type_str = "Folder" if is_dir else os.path.splitext(name)[1].upper() or "File"
            
            size_str = format_byte_size(size_b)

            row = DiscTableItem(self.right_table, [
                f"{icon_prefix}{name}",
                size_str,
                type_str,
                orig_path
            ])
            row.setData(0, Qt.ItemDataRole.UserRole, itm)

        self.right_table.setSortingEnabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                p = os.path.normpath(url.toLocalFile()).replace('/', os.sep)
                if p and os.path.exists(p):
                    paths.append(p)
            self.add_paths(paths)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _populate_subfolders_tree(self, parent_tree_item, dir_path, is_on_disc=False):
        """Recursively builds the left tree hierarchy for all subfolders inside a directory."""
        try:
            for entry in sorted(os.listdir(dir_path), key=natural_sort_key):
                sub_path = os.path.join(dir_path, entry)
                if os.path.isdir(sub_path):
                    prefix = f"💿 {entry} [Disc]" if is_on_disc else f"📁 {entry}"
                    sub_node = QTreeWidgetItem(parent_tree_item, [prefix])
                    sub_node.setData(0, Qt.ItemDataRole.UserRole, {
                        "is_root": False,
                        "path": sub_path,
                        "name": entry,
                        "is_dir": True,
                        "is_on_disc": is_on_disc,
                        "items": []
                    })
                    self._populate_subfolders_tree(sub_node, sub_path, is_on_disc)
        except Exception:
            pass

    def add_paths(self, paths):
        target_node = self.get_current_folder_node()
        data = dict(target_node.data(0, Qt.ItemDataRole.UserRole) or {})
        items = list(data.get("items", []))

        for p in paths:
            clean_p = os.path.normpath(os.path.abspath(p)).replace('/', os.sep)
            if not os.path.exists(clean_p):
                continue
            base_name = os.path.basename(clean_p) or clean_p
            is_dir = os.path.isdir(clean_p)
            size_bytes = compute_path_size(clean_p)

            # Prevent duplicate entries in the same virtual folder
            if any(it["path"] == clean_p or it["name"] == base_name for it in items):
                continue

            item_dict = {
                "name": base_name,
                "path": clean_p,
                "is_dir": is_dir,
                "size_bytes": size_bytes
            }
            items.append(item_dict)

            # If directory, create child node and populate all nested subfolders
            if is_dir:
                child_folder = QTreeWidgetItem(target_node, [f"📁 {base_name}"])
                child_folder.setData(0, Qt.ItemDataRole.UserRole, {
                    "is_root": False,
                    "path": clean_p,
                    "name": base_name,
                    "is_dir": True,
                    "is_on_disc": False,
                    "items": []
                })
                self._populate_subfolders_tree(child_folder, clean_p, is_on_disc=False)

        data["items"] = items
        target_node.setData(0, Qt.ItemDataRole.UserRole, data)

        target_node.setExpanded(True)
        self.refresh_right_table(target_node)
        self.payload_changed.emit(self.get_total_bytes())

    def set_paths(self, paths):
        self.clear_all()
        self.add_paths(paths)

    def remove_selected(self):
        target_node = self.get_current_folder_node()
        data = dict(target_node.data(0, Qt.ItemDataRole.UserRole) or {})
        items = list(data.get("items", []))

        selected_table_items = self.right_table.selectedItems()
        if not selected_table_items:
            return

        for sel in selected_table_items:
            itm_data = sel.data(0, Qt.ItemDataRole.UserRole)
            if itm_data:
                name = itm_data["name"]
                items = [it for it in items if it["name"] != name]

                # If directory, also remove from the left tree
                if itm_data["is_dir"]:
                    for i in range(target_node.childCount()):
                        ch = target_node.child(i)
                        if ch and ch.text(0) == f"📁 {name}":
                            target_node.removeChild(ch)
                            break

        data["items"] = items
        target_node.setData(0, Qt.ItemDataRole.UserRole, data)

        self.refresh_right_table(target_node)
        self.payload_changed.emit(self.get_total_bytes())

    def clear_all(self):
        self.left_tree.blockSignals(True)
        self.left_tree.clear()
        vol = getattr(self, 'volume_label', 'DATA_DISC')
        self.root_node = QTreeWidgetItem(self.left_tree, [f"💽 {vol}"])
        self.root_node.setData(0, Qt.ItemDataRole.UserRole, {"is_root": True, "items": []})
        self.left_tree.setCurrentItem(self.root_node)
        self.left_tree.blockSignals(False)
        self.right_table.clear()
        self.payload_changed.emit(0)

    def get_total_bytes(self):
        def _calc_node_bytes(node):
            total = 0
            data = node.data(0, Qt.ItemDataRole.UserRole) or {}
            for itm in data.get("items", []):
                if not itm.get("is_on_disc", False):
                    total += itm.get("size_bytes", 0)
            return total
        return _calc_node_bytes(self.root_node)

    def get_all_paths(self):
        """Returns root-level staged paths for burning (excluding existing on-disc items)."""
        data = self.root_node.data(0, Qt.ItemDataRole.UserRole) or {}
        return [it["path"] for it in data.get("items", []) if not it.get("is_on_disc", False)]

    def load_existing_disc_session(self, drive_letter):
        """Loads and displays existing session files and folders from an appendable optical disc."""
        if not drive_letter:
            return

        disc_root = drive_letter if drive_letter.endswith(os.sep) else f"{drive_letter}\\"
        if not os.path.exists(disc_root):
            return

        # Check if disc contains files/directories from previous sessions
        try:
            entries = os.listdir(disc_root)
        except Exception:
            return

        if not entries:
            return

        data = dict(self.root_node.data(0, Qt.ItemDataRole.UserRole) or {})
        items = list(data.get("items", []))
        existing_names = {it["name"] for it in items}

        for entry in sorted(entries, key=natural_sort_key):
            if entry in existing_names:
                continue
            entry_path = os.path.join(disc_root, entry)
            is_d = os.path.isdir(entry_path)
            size_b = compute_path_size(entry_path)

            item_dict = {
                "name": entry,
                "path": entry_path,
                "is_dir": is_d,
                "size_bytes": size_b,
                "is_on_disc": True
            }
            items.append(item_dict)

            if is_d:
                child_folder = QTreeWidgetItem(self.root_node, [f"💿 {entry} [Disc]"])
                child_folder.setData(0, Qt.ItemDataRole.UserRole, {
                    "is_root": False,
                    "path": entry_path,
                    "name": entry,
                    "is_dir": True,
                    "is_on_disc": True,
                    "items": []
                })
                self._populate_subfolders_tree(child_folder, entry_path, is_on_disc=True)

        data["items"] = items
        self.root_node.setData(0, Qt.ItemDataRole.UserRole, data)
        self.refresh_right_table(self.root_node)





class AddFilesFoldersDialog(QDialog):
    """Dual-pane file & folder explorer picker dialog supporting simultaneous selection."""
    def __init__(self, start_dir=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Files & Folders")
        self.resize(800, 480)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "icons", "kryodisk-burner-120k-icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)

        # 1. Top Navigation Bar
        nav_layout = QHBoxLayout()
        self.btn_up = QPushButton("⬆ Up")
        self.btn_up.setFixedWidth(65)
        self.btn_up.clicked.connect(self.navigate_up)
        nav_layout.addWidget(self.btn_up)

        self.txt_path = QLineEdit()
        self.txt_path.returnPressed.connect(self.navigate_to_text)
        nav_layout.addWidget(self.txt_path, 1)

        layout.addLayout(nav_layout)

        # 2. Splitter: Left (Drives & Folders Tree) and Right (Contents View)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Pane: Drives & Folder Tree
        self.folder_model = QFileSystemModel()
        self.folder_model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)
        self.folder_model.setRootPath("")

        self.tree_left = QTreeView()
        self.tree_left.setModel(self.folder_model)
        self.tree_left.setHeaderHidden(False)
        self.tree_left.header().setStretchLastSection(True)
        # Hide Size, Type, Date Modified columns in left navigation pane
        for col in range(1, 4):
            self.tree_left.hideColumn(col)
        self.tree_left.clicked.connect(self.on_left_item_clicked)

        # Right Pane: Folder Contents View
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        self.file_model.setRootPath("")

        self.tree_right = QTreeView()
        self.tree_right.setModel(self.file_model)
        self.tree_right.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree_right.setSortingEnabled(True)
        self.tree_right.header().setSectionsClickable(True)
        self.tree_right.header().setSortIndicatorShown(True)
        self.tree_right.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree_right.doubleClicked.connect(self.on_right_item_double_clicked)
        self.tree_right.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree_right.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tree_right.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tree_right.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tree_right.setColumnWidth(1, 80)
        self.tree_right.setColumnWidth(2, 90)
        self.tree_right.setColumnWidth(3, 130)

        self.splitter.addWidget(self.tree_left)
        self.splitter.addWidget(self.tree_right)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setSizes([260, 520])

        layout.addWidget(self.splitter, 1)

        # 3. Bottom Action Buttons
        btn_layout = QHBoxLayout()
        lbl_hint = QLabel("<small><i>Hold Ctrl or Shift to select multiple files and folders at once.</i></small>")
        lbl_hint.setStyleSheet("color: #888888;")
        btn_layout.addWidget(lbl_hint)
        btn_layout.addStretch()

        self.btn_add = QPushButton("Add Selected")
        self.btn_add.setStyleSheet("font-weight: bold; padding: 4px 15px;")
        self.btn_add.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_add)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        # Set initial directory
        initial_dir = start_dir if start_dir and os.path.exists(start_dir) else os.path.expanduser("~")
        self.set_current_directory(initial_dir)

    def set_current_directory(self, dir_path):
        clean_path = os.path.normpath(os.path.abspath(dir_path))
        if os.path.exists(clean_path) and os.path.isdir(clean_path):
            self.current_dir = clean_path
            self.txt_path.setText(self.current_dir)

            # Sync right pane contents view
            right_idx = self.file_model.setRootPath(self.current_dir)
            self.tree_right.setRootIndex(right_idx)

            # Sync left tree view selection and expansion
            left_idx = self.folder_model.index(self.current_dir)
            if left_idx.isValid():
                parent = left_idx.parent()
                while parent.isValid():
                    self.tree_left.expand(parent)
                    parent = parent.parent()
                self.tree_left.setCurrentIndex(left_idx)
                self.tree_left.expand(left_idx)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(150, self._initial_scroll_to_selected)

    def _initial_scroll_to_selected(self):
        if hasattr(self, 'current_dir') and os.path.exists(self.current_dir):
            left_idx = self.folder_model.index(self.current_dir)
            if left_idx.isValid():
                parent = left_idx.parent()
                while parent.isValid():
                    self.tree_left.expand(parent)
                    parent = parent.parent()
                self.tree_left.setCurrentIndex(left_idx)
                self.tree_left.expand(left_idx)
                self.tree_left.scrollTo(left_idx, QAbstractItemView.ScrollHint.PositionAtCenter)

    def navigate_up(self):
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir and os.path.exists(parent_dir) and parent_dir != self.current_dir:
            self.set_current_directory(parent_dir)

    def navigate_to_text(self):
        entered = self.txt_path.text().strip()
        if os.path.exists(entered) and os.path.isdir(entered):
            self.set_current_directory(entered)
        else:
            self.txt_path.setText(self.current_dir)

    def on_left_item_clicked(self, index):
        path = self.folder_model.filePath(index)
        if path and os.path.exists(path) and os.path.isdir(path):
            self.set_current_directory(path)

    def on_right_item_double_clicked(self, index):
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            self.set_current_directory(path)
        elif os.path.isfile(path):
            self.accept()

    def get_selected_paths(self):
        selected_indexes = self.tree_right.selectionModel().selectedRows(0)
        paths = []
        for idx in selected_indexes:
            p = self.file_model.filePath(idx)
            if p and os.path.exists(p):
                paths.append(os.path.normpath(p).replace('/', os.sep))
        # If nothing in the right view is highlighted, add the current folder itself
        if not paths and os.path.exists(self.current_dir):
            paths.append(self.current_dir)
        return paths

class DiscExplorerDialog(QDialog):
    """Dual-pane read-only optical disc explorer dialog to inspect files physically on media."""
    def __init__(self, drive_path, volume_label="", parent=None):
        super().__init__(parent)
        self.drive_path = drive_path if drive_path.endswith(os.sep) else f"{drive_path}\\"
        self.setWindowTitle(f"Browse Optical Disc [{self.drive_path}] - {volume_label or 'DATA_DISC'}")
        self.resize(780, 460)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "icons", "kryodisk-burner-120k-icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)

        # 1. Top Navigation Bar
        nav_layout = QHBoxLayout()
        self.btn_up = QPushButton("⬆ Up")
        self.btn_up.setFixedWidth(65)
        self.btn_up.clicked.connect(self.navigate_up)
        nav_layout.addWidget(self.btn_up)

        self.txt_path = QLineEdit(self.drive_path)
        self.txt_path.setReadOnly(True)
        disc_icon = self.style().standardIcon(self.style().StandardPixmap.SP_DriveCDIcon)
        self.txt_path.addAction(disc_icon, QLineEdit.ActionPosition.LeadingPosition)
        nav_layout.addWidget(self.txt_path, 1)

        self.btn_open_explorer = QPushButton("📁 Open in Explorer")
        self.btn_open_explorer.clicked.connect(self.open_in_explorer)
        nav_layout.addWidget(self.btn_open_explorer)
        layout.addLayout(nav_layout)

        # 2. Splitter: Left (Folders Tree) and Right (Contents View)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Pane: Folders Tree
        self.folder_model = QFileSystemModel()
        self.folder_model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self.folder_model.setRootPath(self.drive_path)

        self.tree_left = QTreeView()
        self.tree_left.setModel(self.folder_model)
        self.tree_left.setRootIndex(self.folder_model.index(self.drive_path))
        self.tree_left.setHeaderHidden(False)
        self.tree_left.header().setStretchLastSection(True)
        for col in range(1, 4):
            self.tree_left.hideColumn(col)
        self.tree_left.clicked.connect(self.on_left_item_clicked)

        # Right Pane: Folder Contents View
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        self.file_model.setRootPath(self.drive_path)

        self.tree_right = QTreeView()
        self.tree_right.setModel(self.file_model)
        self.tree_right.setRootIndex(self.file_model.index(self.drive_path))
        self.tree_right.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree_right.setSortingEnabled(True)
        self.tree_right.header().setSectionsClickable(True)
        self.tree_right.header().setSortIndicatorShown(True)
        self.tree_right.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree_right.doubleClicked.connect(self.on_right_item_double_clicked)
        self.tree_right.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree_right.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tree_right.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tree_right.header().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tree_right.setColumnWidth(1, 80)
        self.tree_right.setColumnWidth(2, 90)
        self.tree_right.setColumnWidth(3, 130)

        self.splitter.addWidget(self.tree_left)
        self.splitter.addWidget(self.tree_right)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setSizes([240, 520])

        layout.addWidget(self.splitter, 1)

        # 3. Bottom Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_close = QPushButton("Close")
        self.btn_close.setStyleSheet("padding: 4px 18px;")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        self.current_dir = self.drive_path
        self.set_current_directory(self.drive_path)

    def set_current_directory(self, dir_path):
        clean_path = os.path.normpath(os.path.abspath(dir_path))
        if os.path.exists(clean_path) and os.path.isdir(clean_path):
            self.current_dir = clean_path
            self.txt_path.setText(self.current_dir)
            right_idx = self.file_model.setRootPath(self.current_dir)
            self.tree_right.setRootIndex(right_idx)

            left_idx = self.folder_model.index(self.current_dir)
            if left_idx.isValid():
                self.tree_left.setCurrentIndex(left_idx)
                self.tree_left.scrollTo(left_idx)

    def navigate_up(self):
        if self.current_dir.rstrip('\\') != self.drive_path.rstrip('\\'):
            parent_dir = os.path.dirname(self.current_dir)
            if parent_dir and os.path.exists(parent_dir):
                self.set_current_directory(parent_dir)

    def on_left_item_clicked(self, index):
        path = self.folder_model.filePath(index)
        if path and os.path.exists(path) and os.path.isdir(path):
            self.set_current_directory(path)

    def on_right_item_double_clicked(self, index):
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            self.set_current_directory(path)

    def open_in_explorer(self):
        if os.path.exists(self.current_dir):
            os.startfile(self.current_dir)


class KryoDiskBurnerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"KryoDisk Burner 120K v{APP_VERSION}")
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        internal_dir = os.path.join(script_dir, "KryoDisk-Burner-120K_internal")
        os.makedirs(internal_dir, exist_ok=True)
        self.config_file = os.path.join(internal_dir, "KryoDisk-Burner-120K.config.json")
        
        icon_path = os.path.join(internal_dir, "icons", "kryodisk-burner-120k-icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        if sys.platform == "win32":
            myappid = f"pwshAgyjkcrg761.kryodiskburner120k.{APP_VERSION}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
        # Allow Windows Explorer drag & drop messages across Administrator UIPI boundary
        if sys.platform == "win32":
            try:
                # MSGFLT_ALLOW = 1; WM_DROPFILES = 0x0233; WM_COPYDATA = 0x004A; WM_COPYGLOBALDATA = 0x0049
                for msg in (0x0233, 0x004A, 0x0049):
                    ctypes.windll.user32.ChangeWindowMessageFilter(msg, 1)
            except Exception:
                pass

        self.default_size = (800, 500)
        self.settings = SettingsWrapper(self.config_file)
        self.load_geometry()
        
        self.current_theme = self.settings.value("theme", "System")
        self.apply_theme(self.current_theme)
        self.last_directory = os.path.normpath(self.settings.value("last_directory", os.getcwd()))
        
        # Parse command line inputs (e.g. from SendTo or file drag onto script)
        self.target_paths = []
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                clean_p = os.path.abspath(arg.strip('"\''))
                if os.path.exists(clean_p) and clean_p not in self.target_paths:
                    self.target_paths.append(clean_p)

        self.target_paths.sort(key=natural_sort_key)

        self.init_ui()
        self.load_saved_settings()

    def init_ui(self):
        self.create_menu()
        layout = QVBoxLayout()
        
        # 1. Optical Burner Drive Selection Row
        drive_layout = QHBoxLayout()
        drive_label = QLabel("Optical Burner:")
        drive_label.setFixedWidth(90)
        self.combo_drives = QComboBox()
        self.combo_drives.currentIndexChanged.connect(self.on_drive_selected)
        
        self.btn_refresh_drives = QPushButton("🔄")
        self.btn_refresh_drives.setToolTip("Refresh Optical Drives & Disc Status")
        self.btn_refresh_drives.setFixedWidth(32)
        self.btn_refresh_drives.clicked.connect(self.refresh_drives)
        
        self.btn_eject = QPushButton("⏏")
        self.btn_eject.setToolTip("Open / Eject Disc Tray")
        self.btn_eject.setFixedWidth(32)
        self.btn_eject.clicked.connect(self.open_tray)

        self.btn_close_tray = QPushButton("📥")
        self.btn_close_tray.setToolTip("Close / Load Disc Tray (Motorized)")
        self.btn_close_tray.setFixedWidth(32)
        self.btn_close_tray.clicked.connect(self.close_tray)

        self.btn_browse_disc = QPushButton("💽")
        self.btn_browse_disc.setToolTip("Browse Contents of Disc in Drive")
        self.btn_browse_disc.setFixedWidth(32)
        self.btn_browse_disc.clicked.connect(self.open_disc_browser)

        drive_layout.addWidget(drive_label)
        drive_layout.addWidget(self.combo_drives, 1)
        drive_layout.addWidget(self.btn_refresh_drives)
        drive_layout.addWidget(self.btn_eject)
        drive_layout.addWidget(self.btn_close_tray)
        drive_layout.addWidget(self.btn_browse_disc)
        if DEV_DEBUG:
            self.btn_erase = QPushButton("🧹")
            self.btn_erase.setToolTip("Quick Erase Rewritable Disc [DevDebug Mode]")
            self.btn_erase.setFixedWidth(32)
            self.btn_erase.clicked.connect(self.erase_disc_quick)
            drive_layout.addWidget(self.btn_erase)
        layout.addLayout(drive_layout)

        # Disc Media Info Banner
        self.lbl_disc_info = QLabel("Disc Status: Checking...")
        self.lbl_disc_info.setFixedHeight(22)
        self.lbl_disc_info.setStyleSheet("font-weight: bold; color: #007acc; padding: 2px 0px;")
        layout.addWidget(self.lbl_disc_info)

        # 2. Disc Staging Area (AnyBurn Split Browser)
        layout.addWidget(QLabel("Disc Staging Layout:"))

        self.path_list = DiscBrowserWidget()
        self.path_list.payload_changed.connect(self.update_capacity_meter)
        layout.addWidget(self.path_list, 1)

        # File List Control Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Add Files && Folders...")
        self.btn_add.setStyleSheet("font-weight: bold; padding: 4px 12px;")
        self.btn_add.clicked.connect(self.open_add_dialog)
        btn_layout.addWidget(self.btn_add)

        self.btn_new_folder = QPushButton("📁 New Folder")
        self.btn_new_folder.clicked.connect(self.create_new_folder)
        btn_layout.addWidget(self.btn_new_folder)

        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.clicked.connect(self.remove_selected_path)
        btn_layout.addWidget(self.btn_remove)

        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.clicked.connect(self.clear_paths)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)

        # 3. Disc Label and File System Configuration
        opts_layout = QHBoxLayout()
        lbl_engine = QLabel("Engine:")
        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["CDBurnerXP (cdbxpcmd)", "ImgBurn"])
        self.combo_engine.setToolTip("Select burning engine: CDBurnerXP (true headless CLI) or ImgBurn (supports UDF 2.60)")
        self.combo_engine.currentIndexChanged.connect(self.on_engine_changed)

        lbl_label = QLabel("Volume Label:")
        self.txt_disc_label = QLineEdit("DATA_DISC")
        self.txt_disc_label.setMaxLength(32)
        self.txt_disc_label.setToolTip("Disc volume label (up to 32 characters for UDF)")
        self.txt_disc_label.textChanged.connect(self.path_list.set_volume_label)
        
        lbl_fs = QLabel("File System:")
        self.combo_udf = QComboBox()
        self.combo_udf.addItems(["UDF 2.50", "UDF 2.60"])
        self.combo_udf.setToolTip("Select Universal Disk Format revision (UDF 2.50 standard or UDF 2.60)")
        
        opts_layout.addWidget(lbl_engine)
        opts_layout.addWidget(self.combo_engine)
        opts_layout.addSpacing(10)
        opts_layout.addWidget(lbl_label)
        opts_layout.addWidget(self.txt_disc_label)
        opts_layout.addSpacing(10)
        opts_layout.addWidget(lbl_fs)
        opts_layout.addWidget(self.combo_udf)
        layout.addLayout(opts_layout)

        # 4. Burn Options & Verification
        burn_opts_layout = QHBoxLayout()
        self.check_verify = QCheckBox("Verify Disc After Burn with KryptDist")
        self.check_verify.setChecked(True)
        self.check_verify.setToolTip("Searches for .hash container on the burned disc and verifies 100% integrity using KryptDist.")
        
        self.check_eject = QCheckBox("Eject Disc When Complete")
        self.check_eject.setChecked(True)

        lbl_speed = QLabel("Write Speed:")
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["Maximum (Auto)", "24x", "16x", "12x", "8x", "6x", "4x", "2x", "1x"])
        self.combo_speed.setToolTip("Select optical disc burning speed")
        
        self.check_finalize = QCheckBox("Finalize Disc")
        self.check_finalize.setChecked(False)
        self.check_finalize.setToolTip("Closes and finalizes the disc. Leave unchecked to allow burning additional sessions later (multisession).")

        burn_opts_layout.addWidget(self.check_verify)
        burn_opts_layout.addWidget(self.check_eject)
        burn_opts_layout.addWidget(self.check_finalize)
        burn_opts_layout.addSpacing(10)
        burn_opts_layout.addWidget(lbl_speed)
        burn_opts_layout.addWidget(self.combo_speed)
        layout.addLayout(burn_opts_layout)

        # 5. Disc Capacity Meter
        cap_layout = QHBoxLayout()
        self.lbl_capacity = QLabel("Payload: 0 B / 0 B (0%)")
        self.lbl_capacity.setStyleSheet("font-size: 11px;")
        cap_layout.addWidget(self.lbl_capacity)
        cap_layout.addStretch()
        layout.addLayout(cap_layout)

        self.capacity_bar = QProgressBar()
        self.capacity_bar.setRange(0, 1000)
        self.capacity_bar.setValue(0)
        self.capacity_bar.setTextVisible(False)
        self.capacity_bar.setFixedHeight(12)
        layout.addWidget(self.capacity_bar)

        # 6. Burn Execution Button with Dual-End Icons
        layout.addSpacing(6)
        self.btn_run = QPushButton()
        self.btn_run.setStyleSheet("font-weight: bold; padding: 6px; font-size: 13px;")

        btn_inner_layout = QHBoxLayout(self.btn_run)
        btn_inner_layout.setContentsMargins(8, 2, 8, 2)
        btn_inner_layout.setSpacing(8)
        btn_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        btn_icon_path = os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "icons", "kryodisk-burner-120k-icon.svg")

        if os.path.exists(btn_icon_path):
            pix_left = QIcon(btn_icon_path).pixmap(18, 18)
            lbl_ico_left = QLabel()
            lbl_ico_left.setPixmap(pix_left)
            lbl_ico_left.setStyleSheet("background: transparent;")
            lbl_ico_left.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            btn_inner_layout.addWidget(lbl_ico_left)

        lbl_btn_text = QLabel("Burn Disc")
        lbl_btn_text.setStyleSheet("font-weight: bold; font-size: 13px; background: transparent;")
        lbl_btn_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        btn_inner_layout.addWidget(lbl_btn_text)

        if os.path.exists(btn_icon_path):
            pix_right = QIcon(btn_icon_path).pixmap(18, 18)
            lbl_ico_right = QLabel()
            lbl_ico_right.setPixmap(pix_right)
            lbl_ico_right.setStyleSheet("background: transparent;")
            lbl_ico_right.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            btn_inner_layout.addWidget(lbl_ico_right)

        self.btn_run.clicked.connect(self.run_burn)
        layout.addWidget(self.btn_run)
        
        self.staging_widget = QWidget()
        self.staging_widget.setLayout(layout)

        # Embedded Burn Progress View (Page 1)
        self.burn_progress_widget = QWidget()
        burn_vlayout = QVBoxLayout(self.burn_progress_widget)
        burn_vlayout.setContentsMargins(14, 12, 14, 12)
        burn_vlayout.setSpacing(6)

        self.lbl_burn_info = QLabel("")
        self.lbl_burn_info.setStyleSheet("color: #007acc; font-size: 12px;")
        burn_vlayout.addWidget(self.lbl_burn_info)

        self.lbl_burn_status = QLabel("Status: Initializing...")
        self.lbl_burn_status.setStyleSheet("font-weight: bold; font-size: 13px;")
        burn_vlayout.addWidget(self.lbl_burn_status)

        self.burn_progress_bar = QProgressBar()
        self.burn_progress_bar.setRange(0, 100)
        self.burn_progress_bar.setValue(0)
        self.burn_progress_bar.setFixedHeight(20)
        burn_vlayout.addWidget(self.burn_progress_bar)

        # Time & ETA Indicators Row
        time_layout = QHBoxLayout()
        self.lbl_burn_detail = QLabel("")
        self.lbl_burn_detail.setStyleSheet("color: #888888; font-size: 11px;")
        time_layout.addWidget(self.lbl_burn_detail)
        time_layout.addStretch()

        self.lbl_burn_time = QLabel("Elapsed: 00:00  |  Remaining: --:--")
        self.lbl_burn_time.setStyleSheet("font-size: 11px; font-weight: bold; color: #007acc;")
        time_layout.addWidget(self.lbl_burn_time)
        burn_vlayout.addLayout(time_layout)

        # Embedded Scrolling Operation Log
        lbl_log_title = QLabel("Operation Log:")
        lbl_log_title.setStyleSheet("font-weight: bold; font-size: 11px; margin-top: 4px;")
        burn_vlayout.addWidget(lbl_log_title)

        self.txt_burn_log = QTextBrowser()
        self.txt_burn_log.setStyleSheet("""
            QTextBrowser {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background-color: palette(base);
                color: palette(text);
                border: 1px solid #444444;
                padding: 6px;
            }
        """)
        burn_vlayout.addWidget(self.txt_burn_log, 1)

        # Bottom Cancel Action
        burn_btn_layout = QHBoxLayout()
        burn_btn_layout.addStretch()
        self.btn_burn_cancel = QPushButton("Cancel Burn")
        self.btn_burn_cancel.setStyleSheet("padding: 5px 22px; font-weight: bold; font-size: 12px;")
        self.btn_burn_cancel.clicked.connect(self.handle_burn_cancel)
        burn_btn_layout.addWidget(self.btn_burn_cancel)
        burn_vlayout.addLayout(burn_btn_layout)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.staging_widget)
        self.stacked_widget.addWidget(self.burn_progress_widget)
        self.setCentralWidget(self.stacked_widget)

        # Populate drives on initial load
        if not NO_DRIVE_SCAN:
            self.refresh_drives()
        else:
            self.combo_drives.blockSignals(True)
            self.combo_drives.addItem("Drive query skipped (Click 🔄 to scan)", None)
            self.combo_drives.blockSignals(False)
            self.lbl_disc_info.setText("Disc Status: Drive query skipped (-NoDriveScan). Click 🔄 to scan optical hardware.")
            self.lbl_disc_info.setStyleSheet("color: #888888; font-weight: bold; padding: 2px 0px;")

        if self.target_paths:
            self.path_list.add_paths(self.target_paths)

    def update_filesystem_display(self):
        is_imgburn = "imgburn" in self.combo_engine.currentText().lower()
        self.combo_udf.blockSignals(True)
        if is_imgburn:
            current_choice = self.combo_udf.currentText()
            self.combo_udf.clear()
            self.combo_udf.addItems(["UDF 2.50", "UDF 2.60"])
            self.combo_udf.setEnabled(True)
            self.combo_udf.setToolTip("Select Universal Disk Format revision (UDF 2.50 standard or UDF 2.60)")
            saved_udf = self.settings.value("udf_revision", "UDF 2.50")
            idx = self.combo_udf.findText(current_choice if current_choice in ("UDF 2.50", "UDF 2.60") else saved_udf)
            self.combo_udf.setCurrentIndex(idx if idx >= 0 else 0)

            self.check_finalize.blockSignals(True)
            self.check_finalize.setChecked(True)
            self.check_finalize.setEnabled(False)
            self.check_finalize.setToolTip("ImgBurn builds and finalizes the disc session automatically.")
            self.check_finalize.blockSignals(False)
        else:
            media_code = getattr(self, 'current_media_info', {}).get("media_type_code", 0)
            media_name = getattr(self, 'current_media_info', {}).get("media_type_name", "")

            if media_code in (17, 18, 19) or "BD" in media_name.upper():
                fs_label = "UDF 2.50 (Forced)"
            elif media_code in (4, 5, 6, 7, 8, 9, 10, 11, 13) or "DVD" in media_name.upper():
                fs_label = "ISO/UDF Bridge 1.02 (Forced)"
            elif media_code in (1, 2, 3) or "CD" in media_name.upper():
                fs_label = "UDF Engine Default (Forced)"
            else:
                fs_label = "UDF (Forced)"

            self.combo_udf.clear()
            self.combo_udf.addItem(fs_label)
            self.combo_udf.setEnabled(False)
            self.combo_udf.setToolTip("CDBurnerXP forces UDF automatically based on media format.")

            self.check_finalize.blockSignals(True)
            if DEV_DEBUG:
                self.check_finalize.setEnabled(True)
                self.check_finalize.setChecked(self.settings.value("finalize_disc_devdebug", False))
                self.check_finalize.setToolTip("Closes and finalizes the disc. Leave unchecked to allow burning additional sessions later (multisession). [DevDebug Mode]")
            else:
                self.check_finalize.setChecked(True)
                self.check_finalize.setEnabled(False)
                self.check_finalize.setToolTip("Disc is automatically finalized to ensure maximum compatibility and prevent hidden sessions.")
            self.check_finalize.blockSignals(False)
        self.combo_udf.blockSignals(False)

    def on_engine_changed(self, index):
        self.update_filesystem_display()

    def refresh_drives(self):
        self.lbl_disc_info.setText("Disc Status: Scanning optical drives & media...")
        self.lbl_disc_info.setStyleSheet("font-weight: bold; color: #007acc; padding: 2px 0px;")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        try:
            self.combo_drives.blockSignals(True)
            self.combo_drives.clear()
            
            self.drives = get_optical_drives()
            if not self.drives:
                self.combo_drives.addItem("No Optical Drives Detected", None)
                self.lbl_disc_info.setText("Disc Status: No optical drives found.")
                self.lbl_disc_info.setStyleSheet("color: #dc3545; font-weight: bold;")
            else:
                for drive in self.drives:
                    self.combo_drives.addItem(drive["name"], drive["id"])
                
                saved_drive_id = self.settings.value("selected_drive_id", "")
                idx = self.combo_drives.findData(saved_drive_id)
                if idx >= 0:
                    self.combo_drives.setCurrentIndex(idx)
            
            self.combo_drives.blockSignals(False)
            self.on_drive_selected(self.combo_drives.currentIndex())
        finally:
            QApplication.restoreOverrideCursor()

    def on_drive_selected(self, index):
        drive_id = self.combo_drives.currentData()
        if not drive_id:
            self.current_media_info = {
                "media_type_name": "No Disc",
                "is_blank": False,
                "free_capacity_bytes": 0,
                "total_capacity_bytes": 0,
                "supported_speeds_raw": []
            }
            self.lbl_disc_info.setText("Disc Status: No optical drive selected.")
            self.lbl_disc_info.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.update_write_speeds()
            self.update_capacity_meter()
            self.update_filesystem_display()
            return

        self.current_media_info = get_drive_media_info(drive_id)
        media_name = self.current_media_info["media_type_name"]
        is_blank = self.current_media_info["is_blank"]
        free_bytes = self.current_media_info["free_capacity_bytes"]
        
        self.update_write_speeds()
        rec_str = f" | Recommended: {getattr(self, 'recommended_speed', '4x')}" if free_bytes > 0 else ""

        media_code = self.current_media_info.get("media_type_code", 0)
        is_rewritable = media_code in (3, 5, 7, 10, 13, 16, 19) or any(x in media_name.upper() for x in ("-RE", "REWRITABLE", "-RW", "+RW", "RAM"))
        is_rom = media_code in (1, 4, 14, 17) or "ROM" in media_name.upper()

        if free_bytes > 0:
            status_text = f"Disc: {media_name} ({'Blank' if is_blank else 'Appendable'}) | Free Capacity: {format_byte_size(free_bytes)}{rec_str}"
            self.lbl_disc_info.setStyleSheet("color: #28a745; font-weight: bold; padding: 2px 0px;")
        elif media_code == 0 or "No Disc" in media_name:
            status_text = f"Disc: {media_name} (No Media Inserted)"
            self.lbl_disc_info.setStyleSheet("color: #007acc; font-weight: bold; padding: 2px 0px;")
        elif is_rom or (not is_rewritable and not is_blank):
            status_text = f"Disc: {media_name} (Finalized / Read-Only) | Free Capacity: 0 B"
            self.lbl_disc_info.setStyleSheet("color: #dc3545; font-weight: bold; padding: 2px 0px;")
        elif is_rewritable:
            status_text = f"Disc: {media_name} (Rewritable Full / Erase to Reuse) | Free Capacity: 0 B"
            self.lbl_disc_info.setStyleSheet("color: #e06c00; font-weight: bold; padding: 2px 0px;")
        else:
            status_text = f"Disc: {media_name} (No Blank Media Inserted)"
            self.lbl_disc_info.setStyleSheet("color: #007acc; font-weight: bold; padding: 2px 0px;")
            
        self.lbl_disc_info.setText(f"Disc Status: {status_text}")
        
        self.update_capacity_meter()
        self.update_filesystem_display()

    def update_write_speeds(self):
        media_code = getattr(self, 'current_media_info', {}).get("media_type_code", 0)
        raw_speeds = getattr(self, 'current_media_info', {}).get("supported_speeds_raw", [])
        media_name = getattr(self, 'current_media_info', {}).get("media_type_name", "")

        # Determine optical sweet spot recommendation
        if media_code == 19 or "BD-RE" in media_name.upper() or "RE" in media_name.upper():
            rec_spd = "2x"
        elif media_code in (17, 18, 19) or "BD" in media_name.upper():
            rec_spd = "4x"
        elif media_code in (8, 10, 11, 13) or "DL" in media_name.upper() or "RW" in media_name.upper():
            rec_spd = "4x"
        elif media_code in (4, 5, 6, 7, 9) or "DVD" in media_name.upper():
            rec_spd = "8x"
        elif media_code == 3 or "CD-RW" in media_name.upper():
            rec_spd = "10x"
        elif media_code in (1, 2) or "CD" in media_name.upper():
            rec_spd = "16x"
        else:
            rec_spd = "4x"
        self.recommended_speed = rec_spd

        self.combo_speed.blockSignals(True)
        self.combo_speed.clear()
        self.combo_speed.addItem("Maximum (Auto)", -1)

        speed_items = []
        if raw_speeds:
            for s in raw_speeds:
                if s <= 0:
                    continue
                if media_code in (1, 2, 3):
                    mult = round(s / 75.0)
                elif media_code in (4, 5, 6, 7, 8, 9, 10, 11, 13):
                    mult = round(s / 680.0)
                else:
                    mult = round(s / 2195.0)
                if mult >= 1:
                    speed_label = f"{int(mult)}x"
                    if not any(item[0] == speed_label for item in speed_items):
                        speed_items.append((speed_label, s))

        if not speed_items:
            if media_code in (17, 18, 19) or "BD" in media_name.upper():
                speed_items = [(f"{x}x", int(x * 2195)) for x in [16, 12, 10, 8, 6, 4, 2, 1]]
            elif media_code in (4, 5, 6, 7, 8, 9, 10, 11, 13) or "DVD" in media_name.upper():
                speed_items = [(f"{x}x", int(x * 680)) for x in [16, 12, 8, 6, 4, 2, 1]]
            elif media_code in (1, 2, 3) or "CD" in media_name.upper():
                speed_items = [(f"{x}x", int(x * 75)) for x in [48, 32, 24, 16, 12, 8, 4, 2, 1]]
            else:
                speed_items = [(f"{x}x", -1) for x in [24, 16, 12, 8, 6, 4, 2, 1]]

        rec_idx = -1
        for label, sec in speed_items:
            if label == rec_spd:
                self.combo_speed.addItem(f"{label} (Recommended)", sec)
                rec_idx = self.combo_speed.count() - 1
            else:
                self.combo_speed.addItem(label, sec)

        if rec_idx >= 0:
            self.combo_speed.setCurrentIndex(rec_idx)
        else:
            self.combo_speed.setCurrentIndex(0)

        self.combo_speed.blockSignals(False)

    def update_capacity_meter(self, total_bytes=None):
        if not hasattr(self, 'capacity_bar') or not hasattr(self, 'lbl_capacity'):
            return

        if total_bytes is None:
            total_bytes = self.path_list.get_total_bytes()
            
        free_cap = getattr(self, 'current_media_info', {}).get("free_capacity_bytes", 0)
        
        if free_cap > 0:
            pct = (total_bytes / free_cap) * 100.0
            val = min(int((total_bytes / free_cap) * 1000), 1000)
            self.capacity_bar.setValue(val)
            
            if total_bytes > free_cap:
                self.capacity_bar.setStyleSheet("QProgressBar::chunk { background-color: #dc3545; }")
                self.lbl_capacity.setText(
                    f"Payload: <span style='color:#dc3545; font-weight:bold;'>{format_byte_size(total_bytes)}</span> / "
                    f"{format_byte_size(free_cap)} ({pct:.1f}%) - OVER CAPACITY!"
                )
            else:
                self.capacity_bar.setStyleSheet("QProgressBar::chunk { background-color: #28a745; }")
                self.lbl_capacity.setText(
                    f"Payload: <b>{format_byte_size(total_bytes)}</b> / {format_byte_size(free_cap)} ({pct:.1f}%)"
                )
        else:
            self.capacity_bar.setValue(0)
            self.lbl_capacity.setText(f"Payload: <b>{format_byte_size(total_bytes)}</b> (Insert media to gauge capacity)")

    

    def load_saved_settings(self):
        if os.path.exists(self.config_file):
            try:
                self.txt_disc_label.setText(self.settings.value("disc_label", "DATA_DISC"))
                self.check_verify.setChecked(self.settings.value("verify_disc", True))
                self.check_eject.setChecked(self.settings.value("eject_disc", True))
                if DEV_DEBUG:
                    self.check_finalize.setChecked(self.settings.value("finalize_disc_devdebug", False))
                else:
                    self.check_finalize.setChecked(self.settings.value("finalize_disc", False))
                saved_speed = self.settings.value("write_speed", "")
                if saved_speed and self.combo_speed.currentIndex() <= 0:
                    idx_speed = self.combo_speed.findText(saved_speed)
                    if idx_speed >= 0:
                        self.combo_speed.setCurrentIndex(idx_speed)
                saved_udf = self.settings.value("udf_revision", "UDF 2.50")
                idx_udf = self.combo_udf.findText(saved_udf)
                if idx_udf >= 0:
                    self.combo_udf.setCurrentIndex(idx_udf)
                saved_engine = self.settings.value("burn_engine", "CDBurnerXP (cdbxpcmd)")
                idx_eng = self.combo_engine.findText(saved_engine)
                if idx_eng >= 0:
                    self.combo_engine.setCurrentIndex(idx_eng)
                self.on_engine_changed(self.combo_engine.currentIndex())
            except Exception as e:
                print(f"Error loading saved settings: {e}")

    def load_geometry(self):
        self.resize(*self.default_size)
        if os.path.exists(self.config_file):
            try:
                if "x" in self.settings.data and "y" in self.settings.data:
                    self.move(self.settings.value("x", 100), self.settings.value("y", 100))
                else:
                    self.center_window()
                self.resize(self.settings.value("width", self.default_size[0]),
                            self.settings.value("height", self.default_size[1]))
            except Exception as e:
                print(f"Error loading geometry: {e}")
                self.center_window()
        else:
            self.center_window()

    def center_window(self):
        frame_geo = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame_geo.moveCenter(screen)
        self.move(frame_geo.topLeft())

    def closeEvent(self, event):
        pos = self.pos()
        self.settings.setValue("x", pos.x())
        self.settings.setValue("y", pos.y())
        self.settings.setValue("width", self.width())
        self.settings.setValue("height", self.height())
        self.settings.setValue("disc_label", self.txt_disc_label.text().strip())
        self.settings.setValue("verify_disc", self.check_verify.isChecked())
        self.settings.setValue("eject_disc", self.check_eject.isChecked())
        if DEV_DEBUG:
            self.settings.setValue("finalize_disc_devdebug", self.check_finalize.isChecked())
        else:
            self.settings.setValue("finalize_disc", self.check_finalize.isChecked())
        self.settings.setValue("write_speed", self.combo_speed.currentText())
        self.settings.setValue("udf_revision", self.combo_udf.currentText())
        self.settings.setValue("burn_engine", self.combo_engine.currentText())
        if self.combo_drives.currentData():
            self.settings.setValue("selected_drive_id", self.combo_drives.currentData())
        self.settings.setValue("theme", self.current_theme)
        event.accept()

    

    def remove_selected_path(self):
        self.path_list.remove_selected()

    def clear_paths(self):
        self.path_list.clear_all()

    def open_add_dialog(self):
        dlg = AddFilesFoldersDialog(start_dir=self.last_directory, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            selected_paths = dlg.get_selected_paths()
            if selected_paths:
                self.last_directory = dlg.current_dir
                self.settings.setValue("last_directory", self.last_directory)
                self.path_list.add_paths(selected_paths)

    def create_new_folder(self):
        target_node = self.path_list.get_current_folder_node()
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter new folder name:")
        if ok and folder_name.strip():
            clean_name = folder_name.strip().replace('/', '').replace('\\', '')
            data = dict(target_node.data(0, Qt.ItemDataRole.UserRole) or {})
            items = list(data.get("items", []))
            
            if not any(it["name"] == clean_name for it in items):
                items.append({
                    "name": clean_name,
                    "path": f"virtual://{clean_name}",
                    "is_dir": True,
                    "size_bytes": 0
                })
                data["items"] = items
                target_node.setData(0, Qt.ItemDataRole.UserRole, data)
                
                child_folder = QTreeWidgetItem(target_node, [f"📁 {clean_name}"])
                child_folder.setData(0, Qt.ItemDataRole.UserRole, {"is_root": False, "path": f"virtual://{clean_name}", "items": []})
                target_node.setExpanded(True)
                self.path_list.refresh_right_table(target_node)

    def create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        tools_menu = menu_bar.addMenu("&Tools")
        themes_menu = tools_menu.addMenu("&Themes")
        
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        
        for theme in ["Dark", "Light", "System"]:
            action = themes_menu.addAction(theme)
            action.setCheckable(True)
            self.theme_group.addAction(action)
            action.triggered.connect(lambda checked, t=theme: self.change_theme(t))
            
        saved_theme = self.settings.value("theme", "System")
        for action in self.theme_group.actions():
            if action.text() == saved_theme:
                action.setChecked(True)
        
        tools_menu.addSeparator()
        pref_action = tools_menu.addAction("&Preferences")
        pref_action.triggered.connect(self.show_preferences)

        help_menu = menu_bar.addMenu("&Help")
        manual_action = help_menu.addAction("Manual")
        manual_action.triggered.connect(self.show_manual)
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def show_preferences(self):
        dialog = PreferencesDialog(self)
        dialog.exec()

    def apply_theme(self, theme_name):
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        if theme_name == "System":
            is_dark = app.style().standardPalette().color(QPalette.ColorRole.Window).lightness() < 128
            effective_theme = "Dark" if is_dark else "Light"
        else:
            effective_theme = theme_name

        palette = QPalette(app.style().standardPalette())
        
        if effective_theme == "Dark":
            text_color = "#ffffff"
            palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#2d2d2d"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e1e"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#252526"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#333333"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#aaaaaa"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#007acc"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        else:
            text_color = "#000000"
            palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#fcfcfc"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#e1e1e1"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#777777"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0078d7"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            
        app.setPalette(palette)
        app.setStyleSheet(f"QTreeWidget QLabel {{ color: {text_color}; background: transparent; }}")

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme(theme_name)

    def show_manual(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manual")
        dialog.resize(680, 560)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "icons", "kryodisk-burner-120k-icon.svg")
        if os.path.exists(icon_path):
            dialog.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(dialog)

        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: palette(text);
                background-color: palette(base);
                border: none;
                padding: 20px;
            }
            h1 { color: #007acc; font-size: 22px; margin-bottom: 0px; }
            h2 { color: #007acc; font-size: 18px; border-bottom: 1px solid #444; padding-bottom: 5px; margin-top: 25px; }
            b { color: #007acc; }
            code { font-family: 'Consolas', monospace; background-color: rgba(128, 128, 128, 0.2); padding: 2px 5px; }
        """)

        manual_text = (
            f"<h1>KryoDisk Burner 120K v{APP_VERSION}</h1>"
            f"<p>MANUAL &amp; USAGE GUIDE | Copyright (C) 2026 pwshAgyjkcrg761</p><br>"
            f"<h2>OVERVIEW</h2>"
            f"<p><b>KryoDisk Burner 120K</b> is a high-performance optical disc authoring and burning application for Windows. "
            f"It features dual burning engine support utilizing <b>CDBurnerXP CLI (cdbxpcmd.exe)</b> for headless operation and "
            f"<b>ImgBurn / ImgBurnPortable</b> to author compliant <b>Universal Disk Format (UDF 2.50 / UDF 2.60)</b> file systems "
            f"across CD, DVD, Blu-ray (BD-R/RE), and high-capacity BDXL media (up to 128GB Quad-Layer).</p>"
            f"<h2>BURNING ENGINES &amp; PREFERENCES</h2>"
            f"<ul>"
            f"<li><b>CDBurnerXP CLI (Default):</b> Headless CLI burning engine that formats and burns data discs with live track progress.</li>"
            f"<li><b>ImgBurn Engine:</b> Advanced authoring engine supporting customizable UDF 2.50 / UDF 2.60 file system revisions.</li>"
            f"<li><b>KryptDist Verifier (KryptDist.py):</b> Integrated cryptographic verification engine for post-burn data validation.</li>"
            f"<li><b>Preferences (Tools -&gt; Preferences):</b> Configure custom executable/script paths or click <b>Auto-Detect</b> for CDBurnerXP, ImgBurn, and KryptDist, as well as notification sound toggles.</li>"
            f"<li><b>GUI Themes:</b> Switch between <b>Dark</b>, <b>Light</b>, or <b>System</b> theme under <b>Tools -&gt; Themes</b>.</li>"
            f"</ul>"
            f"<h2>DISC STAGING &amp; LAYOUT</h2>"
            f"<ul>"
            f"<li><b>Dual-Pane Browser:</b> Structure your disc using the left hierarchy tree and right content pane. Navigate virtual folders and arrange files before burning.</li>"
            f"<li><b>Adding Data:</b> Use the <b>➕ Add Files &amp; Folders</b> dual-explorer dialog, send items via Windows <b>SendTo</b>, or pass paths on startup.</li>"
            f"<li><b>Multisession &amp; Session Appending:</b> Leave <i>Finalize Disc</i> unchecked to permit burning additional sessions later. Existing sessions on appendable media are automatically loaded into the staging tree.</li>"
            f"<li><b>Volume Label:</b> Specify a custom disc label (up to 32 characters in accordance with UDF standards).</li>"
            f"<li><b>Capacity Gauging:</b> Real-time capacity bar dynamically compares staged payloads against free disc media space with overload warnings.</li>"
            f"</ul>"
            f"<h2>HARDWARE &amp; MEDIA SUPPORT</h2>"
            f"<ul>"
            f"<li><b>Supported Formats:</b> CD-R/RW, DVD±R/RW, DVD±R DL (Dual Layer), BD-R/RE (25GB), BD-R DL (50GB), BD-R TL (100GB BDXL), and BD-R QL (128GB BDXL).</li>"
            f"<li><b>Write Speeds:</b> Configures optimal hardware burning speeds (Auto Maximum, 1x, 2x, 4x, 8x, 16x, etc.) with automatic media recommendations.</li>"
            f"<li><b>Tray &amp; Disc Controls:</b> Direct hardware controls for disc eject (<code>⏏</code>), motorized tray close (<code>📥</code>), and physical disc inspection (<code>💽</code>).</li>"
            f"</ul>"
            f"<h2>POST-BURN INTEGRITY VERIFICATION</h2>"
            f"<ul>"
            f"<li><b>Automated Verification:</b> When <i>Verify Disc After Burn with KryptDist</i> is checked, KryoDisk scans the burned disc for checksum manifests (<code>.hash</code>, <code>.b3</code>, <code>.sha256</code>, <code>.sha512</code>, <code>.xxh3</code>, <code>.md5</code>, <code>.sfv</code>, etc.) and performs 100% cryptographic validation.</li>"
            f"<li><b>Safe Ejection:</b> If verification is enabled, tray ejection is held until verification completes successfully.</li>"
            f"</ul>"
            f"<h2>COMMAND LINE FLAGS &amp; DEVDEBUG</h2>"
            f"<ul>"
            f"<li><code>-DevDebug</code> &mdash; Enables verbose console logging, unlocks the Quick Erase (<code>🧹</code>) tool for rewritable media, and maintains independent session finalization preferences.</li>"
            f"<li><code>-NoDriveScan</code> (or <code>-NoScan</code> / <code>-SkipDriveScan</code>) &mdash; When used with <code>-DevDebug</code>, bypasses the initial 5-second optical drive query and media spin-up on startup for instantaneous launch.</li>"
            f"</ul>"
            f"<h2>ENGINE &amp; SCRIPT DISCOVERY</h2>"
            f"<ul>"
            f"<li>Engines and scripts are automatically discovered across:</li>"
            f"  <ol>"
            f"    <li>User and System <code>PATH</code> environment variables (including fresh registry additions).</li>"
            f"    <li><code>KryoDisk-Burner-120K_internal\\bin\\</code> directories.</li>"
            f"    <li><code>C:\\tools\\</code> and <code>C:\\scripts\\</code> standard tool directories.</li>"
            f"    <li>Custom configured paths in <b>Tools -&gt; Preferences -&gt; Engines</b>.</li>"
            f"  </ol>"
            f"</ul>"
            f"<h2>SYSTEM REQUIREMENTS &amp; DEPENDENCIES</h2>"
            f"<ul>"
            f"<li><b>Operating System:</b> Windows 10, Windows 11, or Windows Server (64-bit).</li>"
            f"<li><b>Python Runtime:</b> Python 3.14.5 or higher.</li>"
            f"<li><b>Required Python Packages:</b> <code>PyQt6</code> (GUI framework) and <code>pywin32</code> (optical COM interface).</li>"
            f"<li><b>Hardware:</b> Any compatible internal (SATA/ATAPI) or external (USB) optical burner drive.</li>"
            f"</ul>"
        )

        text_browser.setHtml(manual_text)
        layout.addWidget(text_browser)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.exec()

    def show_about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.resize(500, 350)
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "icons", "kryodisk-burner-120k-icon.svg")
        if os.path.exists(icon_path):
            dialog.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                color: palette(text);
                background-color: palette(base);
                border: none;
                padding: 10px;
            }
            h1 { color: #007acc; font-size: 20px; }
            b { color: #007acc; }
        """)
        
        about_text = (
            f"<h1><a href=\"https://git.disroot.org/pwshAgyjkcrg761/kryodisk-burner-120k\" style=\"color: #007acc; text-decoration: none;\">KryoDisk Burner 120K</a> v{APP_VERSION}</h1>"
            "<p>Copyright (C) 2026 <b>pwshAgyjkcrg761</b><br>"
            "Licensed under <b>GPLv3</b></p>"
            "<p>Official License: <a href=\"https://www.gnu.org/licenses/gpl-3.0.html\">gnu.org/licenses/gpl-3.0.html</a></p>"
            "<hr>"
            "<p><b>Icon Credits:</b><br>"
            "'Fire SVG Vector' by <a href=\"https://www.svgrepo.com/author/dstore/\">dstore</a> via <a href=\"https://www.svgrepo.com/svg/506715/fire\">SVGRepo</a>.<br>"
            "Used under CC0 License. Modified by pwshAgyjkcrg761.</p>"
        )
        text_browser.setHtml(about_text)
        layout.addWidget(text_browser)
        
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()

    

    def show_alert(self, title, text, icon_type="info", buttons=QMessageBox.StandardButton.Ok, default_button=None):
        """Displays a dialog box with optional sound suppression and consistent window icons."""
        sound_disabled = False
        if hasattr(self, 'settings'):
            sound_disabled = self.settings.value("disable_notification_sounds", False)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        internal_dir = os.path.join(script_dir, "KryoDisk-Burner-120K_internal")
        icon_path = os.path.join(internal_dir, "icons", "kryodisk-burner-120k-icon.svg")

        msg_box = QMessageBox(self if self.isVisible() else None)
        window_title = title if title.startswith("KryoDisk Burner 120K") else f"KryoDisk Burner 120K - {title}"
        msg_box.setWindowTitle(window_title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        if default_button:
            msg_box.setDefaultButton(default_button)

        if os.path.exists(icon_path):
            msg_box.setWindowIcon(QIcon(icon_path))

        if icon_type == "success":
            msg_box.setIconPixmap(get_status_pixmap("success"))
        elif icon_type == "error":
            msg_box.setIconPixmap(get_status_pixmap("error"))
        elif icon_type == "warning":
            if not sound_disabled:
                msg_box.setIcon(QMessageBox.Icon.Warning)
            else:
                std_icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxWarning)
                msg_box.setIconPixmap(std_icon.pixmap(48, 48))
        elif icon_type == "question":
            if not sound_disabled:
                msg_box.setIcon(QMessageBox.Icon.Question)
            else:
                std_icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxQuestion)
                msg_box.setIconPixmap(std_icon.pixmap(48, 48))
        elif icon_type == "info":
            if not sound_disabled:
                msg_box.setIcon(QMessageBox.Icon.Information)
            else:
                std_icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation)
                msg_box.setIconPixmap(std_icon.pixmap(48, 48))

        return msg_box.exec()

    def append_burn_log(self, msg):
        if not (len(msg) >= 10 and msg[0] == '[' and msg[9] == ']' and msg[3] == ':' and msg[6] == ':'):
            t_str = time.strftime("%H:%M:%S")
            msg = f"[{t_str}] {msg}"
        self.txt_burn_log.append(msg)
        sb = self.txt_burn_log.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def update_burn_status(self, status_msg, path_detail=""):
        self.lbl_burn_status.setText(status_msg)
        if path_detail:
            metrics = self.lbl_burn_detail.fontMetrics()
            elided = metrics.elidedText(path_detail, Qt.TextElideMode.ElideMiddle, 360)
            self.lbl_burn_detail.setText(elided)
        else:
            self.lbl_burn_detail.setText("")

    def update_burn_progress(self, current, total, phase_msg, elapsed_sec, remaining_sec):
        self.burn_progress_bar.setMaximum(total)
        self.burn_progress_bar.setValue(current)
        if phase_msg:
            self.lbl_burn_status.setText(f"Status: {phase_msg}")

        el_m, el_s = divmod(max(0, elapsed_sec), 60)
        elapsed_str = f"{el_m:02d}:{el_s:02d}"

        if remaining_sec > 0:
            rem_m, rem_s = divmod(remaining_sec, 60)
            remaining_str = f"{rem_m:02d}:{rem_s:02d}"
            tot_m, tot_s = divmod(elapsed_sec + remaining_sec, 60)
            total_str = f"  |  Total Est: {tot_m:02d}:{tot_s:02d}"
        else:
            remaining_str = "--:--"
            total_str = ""

        self.lbl_burn_time.setText(f"Elapsed: {elapsed_str}  |  Remaining: {remaining_str}{total_str}")

    def handle_burn_cancel(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            reply = self.show_alert(
                "Cancel Burn Operation",
                "Are you sure you want to cancel the active disc burn?\n\n"
                "Warning: Cancelling mid-burn may render write-once media (CD-R, DVD-R, BD-R) unusable.",
                icon_type="warning",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                default_button=QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                if hasattr(self, 'btn_burn_cancel'):
                    self.btn_burn_cancel.setText("Cancelling...")
                    self.btn_burn_cancel.setEnabled(False)
        elif hasattr(self, 'verify_worker') and self.verify_worker.isRunning():
            reply = self.show_alert(
                "Cancel Verification",
                "Are you sure you want to cancel disc verification?",
                icon_type="question",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                default_button=QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.verify_worker.cancel()
                if hasattr(self, 'btn_burn_cancel'):
                    self.btn_burn_cancel.setText("Cancelling...")
                    self.btn_burn_cancel.setEnabled(False)
        else:
            self.stacked_widget.setCurrentIndex(0)
            self.refresh_drives()

    def run_burn(self):
        drive_id = self.combo_drives.currentData()
        if not drive_id:
            self.show_alert("No Drive", "Please select a valid optical burner drive.", icon_type="warning")
            return

        targets = self.path_list.get_all_paths()
        if not targets:
            self.show_alert("No Files", "Please add files or folders to burn to the disc.", icon_type="warning")
            return

        total_bytes = self.path_list.get_total_bytes()
        media_info = getattr(self, 'current_media_info', {})
        media_code = media_info.get("media_type_code", 0)
        media_name = media_info.get("media_type_name", "Unknown Media")
        is_blank = media_info.get("is_blank", False)
        free_bytes = media_info.get("free_capacity_bytes", 0)

        # Check for missing media
        if media_code == 0 or "No Disc" in media_name:
            self.show_alert(
                "No Media",
                "No recordable disc was detected in the drive.\n\nPlease insert a blank or appendable optical disc.",
                icon_type="warning"
            )
            return

        is_rewritable = media_code in (3, 5, 7, 10, 13, 16, 19) or any(x in media_name.upper() for x in ("-RE", "REWRITABLE", "-RW", "+RW", "RAM"))
        is_rom = media_code in (1, 4, 14, 17) or "ROM" in media_name.upper()

        # Check for finalized / read-only write-once media
        if is_rom or (not is_rewritable and not is_blank and free_bytes == 0):
            self.show_alert(
                "Disc Finalized",
                f"The inserted disc ({media_name}) has already been finalized and cannot be written to.\n\n"
                "Please insert a blank or appendable disc.",
                icon_type="warning"
            )
            return

        if free_bytes > 0 and total_bytes > free_bytes:
            self.show_alert(
                "Capacity Exceeded",
                f"The staged payload ({format_byte_size(total_bytes)}) exceeds the available capacity "
                f"of the disc ({format_byte_size(free_bytes)}).\n\nPlease remove some items before burning.",
                icon_type="error"
            )
            return

        vol_label = self.txt_disc_label.text().strip() or "DATA_DISC"
        drive_name = self.combo_drives.currentText()
        eject_done = self.check_eject.isChecked()

        speed_label = self.combo_speed.currentText()

        # Prepare Embedded Burn View
        self.lbl_burn_info.setText(f"<b>Volume:</b> {vol_label} &nbsp;|&nbsp; <b>Drive:</b> {drive_name} &nbsp;|&nbsp; <b>Speed:</b> {speed_label}")
        self.lbl_burn_status.setText("Status: Initializing...")
        self.lbl_burn_detail.setText("")
        self.lbl_burn_time.setText("Elapsed: 00:00  |  Remaining: --:--")
        self.txt_burn_log.clear()
        self.burn_progress_bar.setMaximum(100)
        self.burn_progress_bar.setValue(0)
        self.btn_burn_cancel.setText("Cancel Burn")
        self.btn_burn_cancel.setEnabled(True)

        selected_speed_sec = self.combo_speed.currentData()
        finalize_done = self.check_finalize.isChecked()
        fallback_letter = ""
        for d in getattr(self, 'drives', []):
            if d.get("id") == drive_id:
                fallback_letter = d.get("letter", "")
                break

        udf_text = self.combo_udf.currentText()
        udf_rev = "2.60" if "2.60" in udf_text else "2.50"

        custom_cdbxp = self.settings.value("custom_cdbxpcmd_path", "")
        custom_img = self.settings.value("custom_imgburn_path", "")

        self.worker = OpticalBurnWorker(
            drive_id, fallback_letter, targets, volume_label=vol_label,
            udf_revision=udf_rev, eject_when_done=eject_done,
            finalize_disc=finalize_done,
            custom_cdbxpcmd_path=custom_cdbxp,
            custom_imgburn_path=custom_img
        )
        engine_str = "cdbxpcmd" if "cdbxp" in self.combo_engine.currentText().lower() else "imgburn"
        self.worker.engine = engine_str
        self.worker.speed_label = speed_label
        self.worker.verify_after = self.check_verify.isChecked()
        self.worker.status_update.connect(self.update_burn_status)
        self.worker.progress_update.connect(self.update_burn_progress)
        self.worker.log_message.connect(self.append_burn_log)
        self.worker.burn_finished.connect(self.handle_burn_finished)

        self.stacked_widget.setCurrentIndex(1)
        self.worker.start()

    def locate_kryptdist(self):
        """Finds the path to KryptDist using preferences custom path and standard locations."""
        custom_krypt = self.settings.value("custom_kryptdist_path", "") if hasattr(self, 'settings') else ""
        return locate_kryptdist(custom_krypt)

    def open_disc_browser(self):
        """Opens the optical disc browser dialog to view files physically on the inserted disc."""
        drive_id = self.combo_drives.currentData()
        if not drive_id:
            self.show_alert("No Drive", "Please select an optical burner drive.", icon_type="warning")
            return

        drive_letter = ""
        for d in getattr(self, 'drives', []):
            if d.get("id") == drive_id:
                drive_letter = d.get("letter", "")
                break

        if not drive_letter or not os.path.exists(drive_letter):
            self.show_alert(
                "No Disc Accessible",
                f"The optical disc in drive {drive_letter or 'selected'} is not accessible or contains no readable volume.",
                icon_type="warning"
            )
            return

        vol_label = self.txt_disc_label.text().strip() or "DATA_DISC"
        dlg = DiscExplorerDialog(drive_letter, volume_label=vol_label, parent=self)
        dlg.exec()

    def open_tray(self):
        """Opens / ejects the optical drive tray."""
        drive_id = self.combo_drives.currentData()
        if not drive_id:
            return
        self.eject_drive(drive_id)

    def close_tray(self):
        """Closes / loads the optical drive tray on motorized drives."""
        drive_id = self.combo_drives.currentData()
        if not drive_id:
            return
        drive_letter = ""
        for d in getattr(self, 'drives', []):
            if d.get("id") == drive_id:
                drive_letter = d.get("letter", "")
                break

        if drive_letter:
            letter_clean = drive_letter.rstrip('\\')
            closed = False
            try:
                GENERIC_READ = 0x80000000
                GENERIC_WRITE = 0x40000000
                FILE_SHARE_READ = 1
                FILE_SHARE_WRITE = 2
                OPEN_EXISTING = 3
                IOCTL_STORAGE_LOAD_MEDIA = 0x002D480C

                h_device = ctypes.windll.kernel32.CreateFileW(
                    f"\\\\.\\{letter_clean}",
                    GENERIC_READ | GENERIC_WRITE,
                    FILE_SHARE_READ | FILE_SHARE_WRITE,
                    None,
                    OPEN_EXISTING,
                    0,
                    None
                )
                if h_device != -1:
                    bytes_returned = ctypes.c_ulong(0)
                    res = ctypes.windll.kernel32.DeviceIoControl(
                        h_device,
                        IOCTL_STORAGE_LOAD_MEDIA,
                        None, 0, None, 0,
                        ctypes.byref(bytes_returned),
                        None
                    )
                    ctypes.windll.kernel32.CloseHandle(h_device)
                    if res:
                        closed = True
            except Exception:
                pass

            if not closed:
                try:
                    alias = f"cdaudio_{letter_clean[0]}"
                    ctypes.windll.winmm.mciSendStringW(f"open {letter_clean} type cdaudio alias {alias}", None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f"set {alias} door closed", None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f"close {alias}", None, 0, None)
                except Exception:
                    pass

        self.refresh_drives()

    def erase_disc_quick(self):
        """Quick erases rewritable media in the selected optical drive (DevDebug)."""
        drive_id = self.combo_drives.currentData()
        if not drive_id:
            self.show_alert("No Drive", "Please select an optical burner drive.", icon_type="warning")
            return

        drive_letter = ""
        for d in getattr(self, 'drives', []):
            if d.get("id") == drive_id:
                drive_letter = d.get("letter", "")
                break

        reply = self.show_alert(
            "Quick Erase Rewritable Disc",
            f"Are you sure you want to Quick Erase the disc in {drive_letter or 'selected drive'}?\n\n"
            "This will blank all existing sessions and volume structures on the disc.",
            icon_type="question",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default_button=QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.lbl_burn_info.setText(f"<b>Operation:</b> Quick Erase &nbsp;|&nbsp; <b>Drive:</b> {self.combo_drives.currentText()}")
        self.lbl_burn_status.setText("Status: Erasing rewritable disc...")
        self.lbl_burn_detail.setText("")
        self.lbl_burn_time.setText("")
        self.txt_burn_log.clear()
        self.burn_progress_bar.setMaximum(0)
        self.btn_burn_cancel.setEnabled(False)

        custom_cdbxp = self.settings.value("custom_cdbxpcmd_path", "")
        self.erase_worker = DiscEraseWorker(drive_id, drive_letter, custom_cdbxp)
        self.erase_worker.log_message.connect(self.append_burn_log)
        self.erase_worker.erase_finished.connect(self.handle_erase_finished)

        self.stacked_widget.setCurrentIndex(1)
        self.erase_worker.start()

    def handle_erase_finished(self, success, error_msg):
        self.btn_burn_cancel.setText("Back")
        self.btn_burn_cancel.setEnabled(True)
        self.burn_progress_bar.setMaximum(100)
        self.burn_progress_bar.setValue(100 if success else 0)

        if success:
            self.lbl_burn_status.setText("Status: Quick erase completed successfully.")
            self.append_burn_log("Quick erase completed successfully.")
            self.show_alert("Erase Complete", "Rewritable disc was erased successfully!", icon_type="success")
        else:
            self.lbl_burn_status.setText("Status: Quick erase failed.")
            self.append_burn_log(f"Quick erase error: {error_msg}")
            self.show_alert("Erase Failed", f"Quick erase failed:\n\n{error_msg}", icon_type="error")
        self.refresh_drives()

    def eject_drive(self, drive_id):
        """Ejects the optical drive tray via IMAPI2."""
        if not HAS_WIN32COM or not drive_id:
            return
        pythoncom.CoInitialize()
        try:
            recorder = win32com.client.Dispatch("IMAPI2.MsftDiscRecorder2")
            recorder.InitializeDiscRecorder(drive_id)
            recorder.EjectMedia()
        except Exception as e:
            self.append_burn_log(f"Tray eject note: {e}")
        finally:
            pythoncom.CoUninitialize()

        self.current_media_info = {
            "media_type_code": 0,
            "media_type_name": "No Disc",
            "is_blank": False,
            "free_capacity_bytes": 0,
            "total_capacity_bytes": 0,
            "supported_speeds_raw": []
        }
        self.lbl_disc_info.setText("Disc Status: Tray Ejected / No Disc Inserted")
        self.lbl_disc_info.setStyleSheet("color: #007acc; font-weight: bold;")
        self.update_write_speeds()
        self.update_capacity_meter()
        self.update_filesystem_display()

    def on_verify_finished(self, passed, returncode, hash_path, drive_id=None):
        """Handles the completion of KryptDist post-burn integrity verification."""
        hash_name = os.path.basename(hash_path) if hash_path else "checksum file"
        self.btn_burn_cancel.setText("Back")
        self.btn_burn_cancel.setEnabled(True)
        self.lbl_burn_detail.setText("")
        if passed:
            self.burn_progress_bar.setValue(100)
            self.lbl_burn_status.setText("Status: Verification Succeeded (100% Match)")
            self.append_burn_log(f"[OK] Verification Passed: All files match checksums in '{hash_name}'.")
            
            if self.check_eject.isChecked() and drive_id:
                self.append_burn_log("Ejecting disc tray...")
                self.eject_drive(drive_id)

            self.show_alert(
                "Burn & Verification Complete",
                f"Disc burn and integrity verification completed successfully!\n\n"
                f"All files verified 100% against '{hash_name}'.",
                icon_type="success"
            )
        else:
            self.burn_progress_bar.setValue(0)
            self.lbl_burn_status.setText("Status: Verification Failed (Mismatch or Read Error)")
            self.append_burn_log(f"[ERROR] Verification Failed (Exit code {returncode}): Checksum mismatch or corruption detected in '{hash_name}'!")
            self.show_alert(
                "Verification Failed",
                f"Burn completed, but post-burn integrity verification failed!\n\n"
                f"KryptDist reported checksum mismatches or file read errors for: {hash_name}",
                icon_type="error"
            )
        self.refresh_drives()

    def handle_burn_finished(self, success, drive_letter, error_msg):
        self.btn_burn_cancel.setText("Back")
        self.btn_burn_cancel.setEnabled(True)

        if not success:
            self.lbl_burn_status.setText("Status: Burn failed.")
            self.show_alert("Burn Failed", f"Optical disc burn failed:\n\n{error_msg}", icon_type="error")
            self.refresh_drives()
            return

        drive_id = self.combo_drives.currentData()

        # Perform Post-Burn Verification via KryptDist if requested
        if self.check_verify.isChecked() and drive_letter:
            self.lbl_burn_status.setText("Status: Verifying disc with KryptDist...")
            self.append_burn_log("Scanning disc for checksum manifests for verification...")
            kryptdist_path = self.locate_kryptdist()
            if not kryptdist_path:
                self.lbl_burn_status.setText("Status: Burn completed (Verification skipped).")
                self.append_burn_log("Warning: KryptDist.py not found. Verification skipped.")
                self.show_alert(
                    "Burn Complete",
                    f"Disc burn completed successfully!\n\n"
                    f"Note: Post-burn verification was skipped because 'KryptDist.py' was not found in "
                    f"C:\\scripts\\ or system PATH.",
                    icon_type="info"
                )
                self.refresh_drives()
                return

            # Find the first .hash container on the disc
            disc_root = drive_letter if drive_letter.endswith(os.sep) else f"{drive_letter}\\"
            first_hash_file = None

            # Allow Windows shell up to 6 seconds to recognize the freshly burned UDF file system
            for _ in range(12):
                if os.path.exists(disc_root):
                    try:
                        for root_dir, _, files in os.walk(disc_root):
                            for f in files:
                                if f.lower().endswith(CHECKSUM_EXTS):
                                    first_hash_file = os.path.join(root_dir, f)
                                    break
                            if first_hash_file:
                                break
                    except Exception:
                        pass
                if first_hash_file:
                    break
                time.sleep(0.5)

            if first_hash_file:
                self.append_burn_log(f"Launching KryptDist verification on: {os.path.basename(first_hash_file)}")
                self.lbl_burn_status.setText("Status: Verifying disc integrity with KryptDist...")
                self.burn_progress_bar.setValue(0)
                self.lbl_burn_time.setText("Elapsed: 00:00  |  Remaining: --:--")
                self.btn_burn_cancel.setText("Cancel Verify")
                self.btn_burn_cancel.setEnabled(True)
                self.verify_worker = KryptDistVerifyWorker(kryptdist_path, first_hash_file)
                self.verify_worker.log_message.connect(self.append_burn_log)
                self.verify_worker.status_update.connect(self.update_burn_status)
                self.verify_worker.progress_update.connect(self.update_burn_progress)
                self.verify_worker.finished.connect(
                    lambda passed, ret, hf: self.on_verify_finished(passed, ret, hf, drive_id)
                )
                self.verify_worker.start()
            else:
                self.lbl_burn_status.setText("Status: Burn completed (No .hash found).")
                self.append_burn_log("No checksum file found on disc to verify.")
                self.show_alert(
                    "Burn Complete",
                    "Disc burn completed successfully!\n\n"
                    "No .hash file was found on the burned disc to perform automated verification.",
                    icon_type="info"
                )
                self.refresh_drives()
        else:
            self.lbl_burn_status.setText("Status: Burn completed successfully.")
            self.append_burn_log("Disc burn completed successfully.")
            self.show_alert(
                "Burn Complete",
                "Disc burn completed successfully!",
                icon_type="success"
            )
            self.refresh_drives()


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                script_path = os.path.abspath(__file__)
                script_dir = os.path.dirname(script_path)
                params = subprocess.list2cmdline([script_path] + sys.argv[1:])
                py_dir = os.path.dirname(sys.executable)
                target_exe_name = "python.exe" if DEV_DEBUG else "pythonw.exe"
                target_exe = os.path.join(py_dir, target_exe_name)
                executable = target_exe if os.path.exists(target_exe) else sys.executable
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", executable, params, script_dir, 1
                )
                sys.exit(0 if ret > 32 else 1)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = KryoDiskBurnerApp()
    window.show()
    sys.exit(app.exec())