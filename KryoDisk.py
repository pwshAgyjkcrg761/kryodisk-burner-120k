# ==============================================================================
# SCRIPT: KryoDisk.py
# VERSION: 2026.09.10__05.27.37
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
import fnmatch
import re
import ctypes
import ctypes.wintypes

APP_VERSION = "2026.09.10__05.27.37"

def natural_sort_key(s):
    """Sort strings containing numbers in human/natural order safely across types."""
    return [(0, int(t)) if t.isdigit() else (1, t.lower()) for t in re.split(r'(\d+)', str(s))]

DEFAULT_IGNORE_TYPES = "hash,b3,blake3,b2,blake2,blake2b,blake2s,sha512,sha256,sha3,sha3-256,sha3-512,xx3,xxh3,xxh,sha1,sha,md5,sfv,crc32,crc,lnk,url,m3u,m3u8,pls,log,tmp,temp,bak,part,crdownload"
DEFAULT_IGNORE_FILES = "desktop.ini,folder.jpg,.desktop,.directory,thumbs.db,ehthumbs.db,ehthumbs_vista.db,md5sums,md5sum.txt,sha256sums,sha256sum.txt,sha512sums,sha512sum.txt,checksums.txt,hashes.txt,.DS_Store,._.DS_Store,._*,~$*,pagefile.sys,hiberfil.sys,swapfile.sys,dumpstack.log.tmp"
DEFAULT_IGNORE_FOLDERS = "RECYCLER,$Recycle.Bin,System Volume Information,.Spotlight-V100,.Trashes,.fseventsd,.Trash-*,__pycache__,.pytest_cache,.git,.svn,.hg,node_modules"

def matches_pattern_list(name, pattern_csv):
    """Checks if a file/folder name matches any wildcard/extension pattern in a comma-separated string."""
    if not pattern_csv:
        return False
    patterns = [p.strip() for p in pattern_csv.split(",") if p.strip()]
    name_lower = name.lower()
    for pat in patterns:
        pat_lower = pat.lower()
        if fnmatch.fnmatch(name_lower, pat_lower):
            return True
        # Match bare extensions like 'log' against '.log'
        if not pat_lower.startswith("*") and not pat_lower.startswith("."):
            if fnmatch.fnmatch(name_lower, f"*.{pat_lower}"):
                return True
    return False

def is_ignored(item_name, is_dir=False, ignore_types="", ignore_files="", ignore_folders=""):
    """Determines whether a file or directory should be ignored based on user rules."""
    if is_dir:
        return matches_pattern_list(item_name, ignore_folders)
    
    # Check ignored file extensions / types
    if matches_pattern_list(item_name, ignore_types):
        return True
    # Check ignored specific file names / wildcards
    if matches_pattern_list(item_name, ignore_files):
        return True
    return False

def get_user_profile_dir():
    """Retrieves the user profile directory safely via Win32 API."""
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    # CSIDL_PROFILE = 40 (0x0028)
    if ctypes.windll.shell32.SHGetFolderPathW(None, 40, None, 0, buf) == 0:
        return buf.value
    return os.path.expanduser("~")

def get_available_drives():
    """Enumerates available system drives and returns (path, label) pairs."""
    drives = []
    if sys.platform == "win32":
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        type_names = {
            2: "Removable",
            3: "Fixed Disk",
            4: "Network Drive",
            5: "Optical Drive",
            6: "RAM Disk"
        }
        for i in range(26):
            if bitmask & (1 << i):
                drive_letter = f"{chr(65 + i)}:\\"
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_letter)
                desc = type_names.get(drive_type, "Drive")
                drives.append((drive_letter, f"{drive_letter} ({desc})"))
    else:
        drives.append(("/", "/ (Root)"))
    return drives

import shutil
import subprocess

try:
    import win32com.client
    import pythoncom
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

# IMAPI2 Media Physical Types
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
    12: "HD DVD-ROM",
    13: "BD-R",
    14: "BD-RE",
    15: "BD-ROM"
}

def format_byte_size(num_bytes):
    """Formats bytes into human-readable binary units (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"

def get_optical_drives():
    """Enumerates optical disc burner drives connected to the system via Windows IMAPI2."""
    drives = []
    if not HAS_WIN32COM:
        print("IMAPI2 Error: pywin32 (win32com.client) is not installed.")
        return drives

    pythoncom.CoInitialize()
    try:
        disc_master = win32com.client.Dispatch("IMAPI2.MsftDiscMaster2")
        count = int(disc_master.Count)
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
                    print(f"Access Denied on drive index {i}. Note: Running as Administrator may be required by Windows policy.")
                else:
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
            print(f"Successfully detected drive: {drive_name}")

    except Exception as e:
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

            try:
                info["is_blank"] = bool(data_writer.MediaPhysicallyBlank)
            except Exception:
                info["is_blank"] = False

            sector_size = 2048
            try:
                free_sectors = int(data_writer.FreeSectorsOnMedia)
                info["free_capacity_bytes"] = max(0, free_sectors * sector_size)
            except Exception:
                info["free_capacity_bytes"] = 0

            try:
                total_sectors = int(data_writer.TotalSectorsOnMedia)
                info["total_capacity_bytes"] = max(0, total_sectors * sector_size)
            except Exception:
                info["total_capacity_bytes"] = 0

            try:
                speeds = list(data_writer.SupportedWriteSpeeds)
                info["supported_speeds_raw"] = sorted(list(set(speeds)), reverse=True)
            except Exception:
                info["supported_speeds_raw"] = []
    except Exception as e:
        print(f"IMAPI2 media info query error: {e}")
    finally:
        pythoncom.CoUninitialize()
    return info

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDir
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QMessageBox, 
                             QDialog, QCheckBox, QTextBrowser, QDialogButtonBox,
                             QComboBox, QProgressBar, QHBoxLayout, QListWidget,
                             QTabWidget, QLineEdit, QFormLayout, QTreeWidget,
                             QTreeWidgetItem, QSplitter, QHeaderView, QMenu,
                             QInputDialog, QTreeView, QAbstractItemView)
from PyQt6.QtGui import (QActionGroup, QPalette, QColor, QIcon, QPixmap, QPainter, 
                         QPen, QFileSystemModel)
import ctypes

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
        self.resize(560, 320)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Tab 1: File Extensions to Ignore (Blank placeholder)
        ignore_tab = QWidget()
        ignore_layout = QVBoxLayout(ignore_tab)
        ignore_layout.addStretch()
        self.tabs.addTab(ignore_tab, "File Extensions to Ignore")

        # Tab 2: Options
        options_tab = QWidget()
        options_layout = QVBoxLayout(options_tab)
        self.chk_disable_sound = QCheckBox("Disable Notification Sounds")
        self.chk_disable_sound.setToolTip("Mutes all audio chimes and notification sounds for completion alerts.")
        options_layout.addWidget(self.chk_disable_sound)
        options_layout.addStretch()

        self.tabs.addTab(options_tab, "Options")
        main_layout.addWidget(self.tabs)

        # Dialog Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_and_close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.load_values()

    def load_values(self):
        if self.parent_app and hasattr(self.parent_app, 'settings'):
            s = self.parent_app.settings
            self.chk_disable_sound.setChecked(s.value("disable_notification_sounds", False))

    def restore_defaults(self):
        pass

    def save_and_close(self):
        if self.parent_app and hasattr(self.parent_app, 'settings'):
            s = self.parent_app.settings
            s.setValue("disable_notification_sounds", self.chk_disable_sound.isChecked())
        self.accept()


import tempfile

class OpticalBurnWorker(QThread):
    status_update = pyqtSignal(str, str)
    progress_update = pyqtSignal(int, int, str)
    burn_finished = pyqtSignal(bool, str, str)

    def __init__(self, drive_id, staged_paths, volume_label="DATA_DISC", eject_when_done=True,
                 finalize_disc=True, ignore_types="", ignore_files="", ignore_folders=""):
        super().__init__()
        self.drive_id = drive_id
        self.staged_paths = staged_paths
        self.volume_label = volume_label or "DATA_DISC"
        self.eject_when_done = eject_when_done
        self.finalize_disc = finalize_disc
        self.ignore_types = ignore_types
        self.ignore_files = ignore_files
        self.ignore_folders = ignore_folders
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        if not HAS_WIN32COM:
            self.burn_finished.emit(False, "", "pywin32 (win32com) is not installed or available.")
            return

        pythoncom.CoInitialize()
        temp_staging_dir = None
        drive_letter = ""

        try:
            self.status_update.emit("Status: Initializing IMAPI2 optical recorder...", "")
            
            recorder = win32com.client.Dispatch("IMAPI2.MsftDiscRecorder2")
            recorder.InitializeDiscRecorder(self.drive_id)
            
            mount_points = list(recorder.VolumePathNames)
            drive_letter = mount_points[0] if mount_points else ""

            # 1. Prepare Disc Data Writer
            data_writer = win32com.client.Dispatch("IMAPI2.MsftDiscFormat2Data")
            if not data_writer.IsRecorderSupported(recorder):
                self.burn_finished.emit(False, drive_letter, "The selected recorder does not support data writing.")
                return

            data_writer.Recorder = recorder
            data_writer.ClientName = "KryoDisk Burner 120K"
            data_writer.ForceMediaToBeClosed = bool(self.finalize_disc)

            # 2. Initialize File System Image targeting UDF 2.50
            self.status_update.emit("Status: Building UDF 2.50 virtual file system...", "")
            fsi = win32com.client.Dispatch("IMAPI2FS.MsftFileSystemImage")
            
            # FsiFileSystemUDF = 4
            fsi.FileSystemsToCreate = 4
            fsi.UDFRevision = 0x250
            fsi.VolumeName = self.volume_label[:32]

            # Connect multisession interfaces & import previous sessions if disc contains data
            is_blank = False
            try:
                is_blank = bool(data_writer.MediaPhysicallyBlank or data_writer.MediaHeuristicallyBlank)
            except Exception:
                is_blank = False

            if not is_blank:
                try:
                    self.status_update.emit("Status: Importing previous disc session...", "")
                    fsi.MultisessionInterfaces = data_writer.MultisessionInterfaces
                    fsi.ImportFileSystem()
                except Exception as ms_err:
                    print(f"Multisession import notice: {ms_err}")

            root_item = fsi.Root

            # 3. Stage directories and loose files into virtual root
            loose_files = []
            for path in self.staged_paths:
                if not os.path.exists(path):
                    continue
                if os.path.isdir(path):
                    dir_name = os.path.basename(path)
                    self.status_update.emit(f"Status: Staging folder '{dir_name}'...", path)
                    # AddTree: adds directory tree into virtual UDF root
                    root_item.AddTree(path, True)
                else:
                    loose_files.append(path)

            if loose_files:
                temp_staging_dir = tempfile.mkdtemp(prefix="kryodisk_staging_")
                for fpath in loose_files:
                    fname = os.path.basename(fpath)
                    dst = os.path.join(temp_staging_dir, fname)
                    try:
                        # Use hardlink or fast copy
                        os.link(fpath, dst)
                    except Exception:
                        shutil.copy2(fpath, dst)
                self.status_update.emit("Status: Staging loose files into UDF 2.50 image...", "")
                root_item.AddTree(temp_staging_dir, False)

            if self._is_cancelled:
                self.burn_finished.emit(False, drive_letter, "Operation cancelled by user.")
                return

            # 4. Create ISO/UDF result image stream
            self.status_update.emit("Status: Creating disc image stream...", "")
            result_image = fsi.CreateResultImage()
            image_stream = result_image.ImageStream

            if hasattr(self, 'requested_speed_sectors') and self.requested_speed_sectors and self.requested_speed_sectors > 0:
                try:
                    data_writer.SetWriteSpeed(int(self.requested_speed_sectors), False)
                except Exception as speed_err:
                    print(f"Notice: Setting write speed to {self.requested_speed_sectors} failed: {speed_err}")

            self.status_update.emit("Status: Writing UDF 2.50 image to disc...", drive_letter)
            self.progress_update.emit(50, 100, "Burning payload to optical disc...")

            # 5. Execute Write Operation
            data_writer.Write(image_stream)

            if not drive_letter and hasattr(self, 'fallback_drive_letter'):
                drive_letter = self.fallback_drive_letter

            # 6. Optional tray eject (only if verification is not queued)
            if self.eject_when_done and not getattr(self, 'verify_after', False):
                self.status_update.emit("Status: Ejecting disc...", drive_letter)
                try:
                    recorder.EjectMedia()
                except Exception as e:
                    print(f"Error ejecting disc: {e}")

            self.burn_finished.emit(True, drive_letter, "")

        except Exception as e:
            self.burn_finished.emit(False, drive_letter, str(e))
        finally:
            if temp_staging_dir and os.path.exists(temp_staging_dir):
                try:
                    shutil.rmtree(temp_staging_dir, ignore_errors=True)
                except Exception:
                    pass
            pythoncom.CoUninitialize()





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

class DiscBrowserWidget(QWidget):
    payload_changed = pyqtSignal(int)

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
        self.right_table.clear()
        if folder_node is None:
            folder_node = self.get_current_folder_node()
        if not folder_node:
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

            row = QTreeWidgetItem(self.right_table, [
                f"{icon_prefix}{name}",
                size_str,
                type_str,
                orig_path
            ])
            row.setData(0, Qt.ItemDataRole.UserRole, itm)

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


class BurnProgressDialog(QDialog):
    """Dedicated status and progress window shown during optical burning operations."""
    cancel_requested = pyqtSignal()

    def __init__(self, volume_label, drive_name, parent=None):
        super().__init__(parent)
        self._allow_close = False
        self.setWindowTitle("Burning Optical Disc...")
        self.resize(520, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "KryoDisk-Burner-120K_internal", "icons", "kryodisk-burner-120k-icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)

        lbl_info = QLabel(f"<b>Volume:</b> {volume_label} &nbsp;|&nbsp; <b>Drive:</b> {drive_name}")
        lbl_info.setStyleSheet("color: #007acc; font-size: 12px;")
        layout.addWidget(lbl_info)

        self.lbl_status = QLabel("Status: Initializing...")
        self.lbl_status.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self.lbl_status)

        self.lbl_detail = QLabel("")
        self.lbl_detail.setStyleSheet("color: #888888; font-size: 11px;")
        self.lbl_detail.setWordWrap(True)
        layout.addWidget(self.lbl_detail)

        layout.addSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)

        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel Burn")
        self.btn_cancel.setStyleSheet("padding: 4px 18px; font-weight: bold;")
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def update_status(self, status_msg, path_detail=""):
        self.lbl_status.setText(status_msg)
        if path_detail:
            metrics = self.lbl_detail.fontMetrics()
            elided = metrics.elidedText(path_detail, Qt.TextElideMode.ElideMiddle, 480)
            self.lbl_detail.setText(elided)
        else:
            self.lbl_detail.setText("")

    def update_progress(self, current, total, phase_msg):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        if phase_msg:
            self.lbl_status.setText(f"Status: {phase_msg}")

    def on_cancel_clicked(self):
        self.cancel_requested.emit()

    def closeEvent(self, event):
        if self._allow_close:
            event.accept()
        else:
            self.cancel_requested.emit()
            event.ignore()


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
                self.tree_left.setCurrentIndex(left_idx)
                self.tree_left.scrollTo(left_idx)
                self.tree_left.expand(left_idx)

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
        
        drive_layout.addWidget(drive_label)
        drive_layout.addWidget(self.combo_drives, 1)
        drive_layout.addWidget(self.btn_refresh_drives)
        layout.addLayout(drive_layout)

        # Disc Media Info Banner
        self.lbl_disc_info = QLabel("Disc Status: Checking...")
        self.lbl_disc_info.setStyleSheet("font-weight: bold; color: #007acc; padding: 2px 0px;")
        layout.addWidget(self.lbl_disc_info)

        # 2. Disc Staging Area (AnyBurn Split Browser)
        layout.addWidget(QLabel("Disc Staging Layout:"))

        self.path_list = DiscBrowserWidget()
        self.path_list.payload_changed.connect(self.update_capacity_meter)
        if self.target_paths:
            self.path_list.set_paths(self.target_paths)
        layout.addWidget(self.path_list, 1)

        # File List Control Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Add Files & Folders...")
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
        lbl_label = QLabel("Volume Label:")
        self.txt_disc_label = QLineEdit("DATA_DISC")
        self.txt_disc_label.setMaxLength(32)
        self.txt_disc_label.setToolTip("Disc volume label (up to 32 characters for UDF)")
        self.txt_disc_label.textChanged.connect(self.path_list.set_volume_label)
        
        lbl_fs = QLabel("File System: <b>UDF 2.50</b>")
        lbl_fs.setStyleSheet("color: #007acc;")
        
        opts_layout.addWidget(lbl_label)
        opts_layout.addWidget(self.txt_disc_label)
        opts_layout.addSpacing(15)
        opts_layout.addWidget(lbl_fs)
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

        # 6. Burn Execution Button
        layout.addSpacing(6)
        self.btn_run = QPushButton("Burn Disc")
        self.btn_run.setStyleSheet("font-weight: bold; padding: 7px; font-size: 13px;")
        self.btn_run.clicked.connect(self.run_burn)
        layout.addWidget(self.btn_run)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Populate drives on initial load
        self.refresh_drives()

    def refresh_drives(self):
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
            return

        self.current_media_info = get_drive_media_info(drive_id)
        media_name = self.current_media_info["media_type_name"]
        is_blank = self.current_media_info["is_blank"]
        free_bytes = self.current_media_info["free_capacity_bytes"]
        
        if free_bytes > 0:
            status_text = f"Disc: {media_name} ({'Blank' if is_blank else 'Appendable'}) | Free Capacity: {format_byte_size(free_bytes)}"
            self.lbl_disc_info.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            status_text = f"Disc: {media_name} (No Blank Media Inserted)"
            self.lbl_disc_info.setStyleSheet("color: #007acc; font-weight: bold;")
            
        self.lbl_disc_info.setText(f"Disc Status: {status_text}")
        
        # If disc is appendable and has existing sessions, load previous files into browser
        if not is_blank and free_bytes > 0:
            drive_letter = ""
            for d in getattr(self, 'drives', []):
                if d.get("id") == drive_id:
                    drive_letter = d.get("letter", "")
                    break
            if drive_letter:
                self.path_list.load_existing_disc_session(drive_letter)

        self.update_write_speeds()
        self.update_capacity_meter()

    def update_write_speeds(self):
        media_code = getattr(self, 'current_media_info', {}).get("media_type_code", 0)
        raw_speeds = getattr(self, 'current_media_info', {}).get("supported_speeds_raw", [])
        media_name = getattr(self, 'current_media_info', {}).get("media_type_name", "")
        
        self.combo_speed.blockSignals(True)
        self.combo_speed.clear()
        self.combo_speed.addItem("Maximum (Auto)", -1)

        speed_items = []
        if raw_speeds:
            for s in raw_speeds:
                if s <= 0:
                    continue
                if media_code in (1, 2, 3):  # CD (75 sectors/sec = 1x)
                    mult = round(s / 75.0)
                elif media_code in (4, 5, 6, 7, 8, 9, 10, 11):  # DVD (680 sectors/sec = 1x)
                    mult = round(s / 680.0)
                elif media_code in (13, 14, 15):  # BD (2195 sectors/sec = 1x)
                    mult = round(s / 2195.0)
                else:
                    mult = round(s / 2195.0)
                if mult >= 1:
                    speed_label = f"{int(mult)}x"
                    if not any(item[0] == speed_label for item in speed_items):
                        speed_items.append((speed_label, s))

        # Fallback speeds if disc is absent or drive doesn't report discrete speed descriptors
        if not speed_items:
            if media_code in (13, 14, 15) or "BD" in media_name.upper():
                speed_items = [(f"{x}x", int(x * 2195)) for x in [16, 12, 10, 8, 6, 4, 2, 1]]
            elif media_code in (4, 5, 6, 7, 8, 9, 10, 11) or "DVD" in media_name.upper():
                speed_items = [(f"{x}x", int(x * 680)) for x in [16, 12, 8, 6, 4, 2, 1]]
            elif media_code in (1, 2, 3) or "CD" in media_name.upper():
                speed_items = [(f"{x}x", int(x * 75)) for x in [48, 32, 24, 16, 12, 8, 4, 2, 1]]
            else:
                speed_items = [(f"{x}x", -1) for x in [24, 16, 12, 8, 6, 4, 2, 1]]

        for label, sec in speed_items:
            self.combo_speed.addItem(label, sec)

        is_bd = media_code in (13, 14, 15) or "BD" in media_name.upper()
        if is_bd:
            idx_4x = self.combo_speed.findText("4x")
            if idx_4x >= 0:
                self.combo_speed.setCurrentIndex(idx_4x)
            else:
                self.combo_speed.setCurrentIndex(0)
        else:
            saved_speed = self.settings.value("write_speed", "Maximum (Auto)")
            idx_saved = self.combo_speed.findText(saved_speed)
            if idx_saved >= 0:
                self.combo_speed.setCurrentIndex(idx_saved)
            else:
                self.combo_speed.setCurrentIndex(0)

        self.combo_speed.blockSignals(False)

    def update_capacity_meter(self, total_bytes=None):
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
                self.check_finalize.setChecked(self.settings.value("finalize_disc", False))
                saved_speed = self.settings.value("write_speed", "Maximum (Auto)")
                idx_speed = self.combo_speed.findText(saved_speed)
                if idx_speed >= 0:
                    self.combo_speed.setCurrentIndex(idx_speed)
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
        self.settings.setValue("finalize_disc", self.check_finalize.isChecked())
        self.settings.setValue("write_speed", self.combo_speed.currentText())
        if self.combo_drives.currentData():
            self.settings.setValue("selected_drive_id", self.combo_drives.currentData())
        self.settings.setValue("theme", self.current_theme)
        event.accept()

    def add_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory to Add", self.last_directory)
        if dir_path:
            clean_p = os.path.normpath(dir_path).replace('/', os.sep)
            self.last_directory = clean_p
            self.settings.setValue("last_directory", self.last_directory)
            self.path_list.add_paths([clean_p])

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Add", self.last_directory)
        if files:
            self.last_directory = os.path.normpath(os.path.dirname(files[0])).replace('/', os.sep)
            self.settings.setValue("last_directory", self.last_directory)
            files.sort(key=natural_sort_key)
            self.path_list.add_paths(files)

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
        from PyQt6.QtWidgets import QInputDialog
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
        dialog.resize(650, 540)

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
            f"<p>KryptDist is a high-performance checksum generator and integrity verifier designed to produce "
            f"primary and distributed subdirectory checksum sets (<code>.hash</code>).</p>"
            f"<h2>OPERATIONAL MODES &amp; BATCH HASHING</h2>"
            f"<ul>"
            f"<li><b>MultiHash Mode:</b> Generates both a root primary <code>.hash</code> file and individual "
            f"subdirectory hashes within every subfolder in a single scanning pass.</li>"
            f"<li><b>Primary Hash Only Mode:</b> Generates only the root directory's primary <code>.hash</code> file.</li>"
            f"<li><b>Batch Processing:</b> Add multiple folders and files simultaneously via Drag &amp; Drop or Windows <b>SendTo</b>. "
            f"KryptDist processes every root target independently in a single, unified queue.</li>"
            f"<li><b>Execution Control:</b> While generating hashes, the execution button transforms into a <b>Cancel</b> button "
            f"with confirmation, and input controls/options are safely locked until completion or cancellation.</li>"
            f"</ul>"
            f"<h2>HASHING OPTIONS</h2>"
            f"<ul>"
            f"<li><b>Incremental Smart Hashing:</b> KryptDist scans existing primary hash files and skips already verified files, "
            f"only hashing new files and appending them to the hash files.</li>"
            f"<li><b>Delete Primary Hashes First:</b> Deletes any existing root primary <code>.hash</code> file before generating new checksums.</li>"
            f"<li><b>Delete Subdirectory Hashes First:</b> Cleans out existing subhashes across all subfolders prior to generation.</li>"
            f"</ul>"
            f"<h2>PREFERENCES &amp; OPTIONS</h2>"
            f"<ul>"
            f"<li><b>Ignore Rules:</b> Configure ignored file extensions, specific file names, and directories under <b>Tools &gt; Preferences &gt; File Extensions to Ignore</b>.</li>"
            f"<li><b>Disable Notification Sounds:</b> Enable under <b>Tools &gt; Preferences &gt; Options</b> to mute completion and alert chimes while retaining visual badges.</li>"
            f"<li><b>Wildcard Support:</b> Patterns accept wildcards (e.g. <code>*.tmp</code>, <code>Thumbs.*</code>, <code>.Trash-*</code>) to cleanly exclude OS metadata, caches, and unwanted artifacts.</li>"
            f"<li><b>Defaults:</b> Preloaded with comprehensive exclusion sets for existing checksum manifests, system volumes, OS caches, and media companion files.</li>"
            f"</ul>"
            f"<h2>SUPPORTED ALGORITHMS</h2>"
            f"<ul>"
            f"<li><b>Cryptographic:</b> BLAKE3, BLAKE2 (2b/2s), SHA-512, SHA-256, SHA-3 (SHA3-256).</li>"
            f"<li><b>Fast Checksum &amp; Legacy:</b> xx3 (xxHash3), SHA-1, MD5, SFV / CRC32.</li>"
            f"</ul>"
            f"<h2>INTERFACE &amp; THEMES</h2>"
            f"<ul>"
            f"<li><b>Tree Navigation:</b> Target lists and progress indicators display clean file/folder names. Click individual disclosure triangles (<code>▶</code> / <code>▼</code>) to view complete, word-wrapped paths with zero horizontal scrolling.</li>"
            f"<li><b>Header Toggle:</b> Click the triangle icon on the far right of <b>Target Files &amp; Folders</b> to expand or collapse all target paths at once.</li>"
            f"<li><b>Persistent UI State:</b> Expanded/collapsed triangle states are remembered across restarts.</li>"
            f"<li><b>Themes:</b> Switch between Dark, Light, and System themes via <b>Tools &gt; Themes</b>. All views and the verification OSD adapt dynamically to the selected theme.</li>"
            f"</ul>"
            f"<h2>VERIFICATION &amp; OSD</h2>"
            f"<p>Pass checksum files via command line or Windows <b>SendTo</b> menu to trigger instant container verification. "
            f"A lightweight On-Screen Display (OSD) provides real-time progress. Completed checks present clear visual status badges "
            f"(green checkmark on success, red X on mismatch). If errors occur, users are prompted whether to generate and open an error log in <code>KryptDist_internal/logs/</code>.</p>"
            f"<h2>CLI &amp; HEADLESS INTEGRATION</h2>"
            f"<ul>"
            f"<li><b>Single-File Verification:</b> Invoke with <code>-v &lt;file&gt;</code> or <code>--verify-file &lt;file&gt;</code> "
            f"for instant, headless verification against local or parent hash containers.</li>"
            f"<li><b>Exit Codes:</b> Returns <code>0</code> when files match, or <code>2</code> on mismatch, missing files, or errors, "
            f"enabling seamless integration with external managers like HashMan.</li>"
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
            f"<h1>KryoDisk Burner 120K v{APP_VERSION}</h1>"
            "<p>Copyright (C) 2026 <b>pwshAgyjkcrg761</b><br>"
            "Licensed under <b>GPLv3</b></p>"
            "<p>Official License: <a href=\"https://www.gnu.org/licenses/gpl-3.0.html\">gnu.org/licenses/gpl-3.0.html</a></p>"
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
                if hasattr(self, 'burn_dialog') and self.burn_dialog:
                    self.burn_dialog.btn_cancel.setText("Cancelling...")
                    self.burn_dialog.btn_cancel.setEnabled(False)

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
        free_bytes = getattr(self, 'current_media_info', {}).get("free_capacity_bytes", 0)

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

        ignore_types = self.settings.value("ignore_types", DEFAULT_IGNORE_TYPES)
        ignore_files = self.settings.value("ignore_files", DEFAULT_IGNORE_FILES)
        ignore_folders = self.settings.value("ignore_folders", DEFAULT_IGNORE_FOLDERS)

        self.burn_dialog = BurnProgressDialog(vol_label, drive_name, parent=None)
        self.burn_dialog.cancel_requested.connect(self.handle_burn_cancel)

        selected_speed_sec = self.combo_speed.currentData()
        finalize_done = self.check_finalize.isChecked()
        fallback_letter = ""
        for d in getattr(self, 'drives', []):
            if d.get("id") == drive_id:
                fallback_letter = d.get("letter", "")
                break

        self.worker = OpticalBurnWorker(
            drive_id, targets, volume_label=vol_label, eject_when_done=eject_done,
            finalize_disc=finalize_done, ignore_types=ignore_types, ignore_files=ignore_files, ignore_folders=ignore_folders
        )
        self.worker.fallback_drive_letter = fallback_letter
        self.worker.verify_after = self.check_verify.isChecked()
        self.worker.requested_speed_sectors = selected_speed_sec
        self.worker.status_update.connect(self.burn_dialog.update_status)
        self.worker.progress_update.connect(self.burn_dialog.update_progress)
        self.worker.burn_finished.connect(self.handle_burn_finished)

        self.hide()
        self.burn_dialog.show()
        self.worker.start()

    def locate_kryptdist(self):
        """Finds the path to KryptDist.py via PATH, local script dir, or default location."""
        # 1. Check same directory
        local_krypt = os.path.join(os.path.dirname(os.path.realpath(__file__)), "KryptDist.py")
        if os.path.exists(local_krypt):
            return local_krypt

        # 2. Check C:\scripts\KryptDist.py
        default_krypt = r"C:\scripts\KryptDist.py"
        if os.path.exists(default_krypt):
            return default_krypt

        # 3. Check PATH
        which_krypt = shutil.which("KryptDist.py")
        if which_krypt:
            return which_krypt

        return None

    def handle_burn_finished(self, success, drive_letter, error_msg):
        if hasattr(self, 'burn_dialog') and self.burn_dialog:
            self.burn_dialog._allow_close = True
            self.burn_dialog.close()
            self.burn_dialog = None

        self.show()

        if not success:
            self.show_alert("Burn Failed", f"Optical disc burn failed:\n\n{error_msg}", icon_type="error")
            self.refresh_drives()
            return

        # Perform Post-Burn Verification via KryptDist if requested
        if self.check_verify.isChecked() and drive_letter:
            kryptdist_path = self.locate_kryptdist()
            if not kryptdist_path:
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
            import time
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
                try:
                    # Launch KryptDist in OSD mode with the discovered hash container
                    subprocess.Popen([sys.executable, kryptdist_path, first_hash_file])
                except Exception as e:
                    self.show_alert(
                        "Verification Launch Error",
                        f"Burn succeeded, but failed to launch KryptDist for verification:\n{e}",
                        icon_type="warning"
                    )
            else:
                self.show_alert(
                    "Burn Complete",
                    "Disc burn completed successfully!\n\n"
                    "No .hash file was found on the burned disc to perform automated verification.",
                    icon_type="info"
                )
        else:
            self.show_alert(
                "Burn Complete",
                "Disc burn completed successfully!",
                icon_type="success"
            )

        self.refresh_drives()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = KryoDiskBurnerApp()
    window.show()
    sys.exit(app.exec())