# Kindle Note Backup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-dependency Python utility to backup `My Clippings.txt` from a Kindle device to the local directory.

**Architecture:** Modular functional structure consisting of `FindDisk` (Windows API via ctypes), `FileLoc` (File operations), and `UIHandler` (User interaction).

**Tech Stack:** Python 3.x, Standard Library (`ctypes`, `os`, `shutil`, `sys`).

---

### Task 1: FindDisk Module Implementation

**Files:**
- Create: `ClipBackup.py`

- [ ] **Step 1: Implement `find_kindle_disk` using `ctypes`**
  Use `ctypes.windll.kernel32.GetVolumeInformationW` to iterate through drives `A:` to `Z:`, matching the volume label "Kindle".

```python
import ctypes
import os

def find_kindle_disk():
    """Scans for a disk with the label 'Kindle' and a 'documents' folder."""
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{drive}:\\"
        if not os.path.exists(drive_path):
            continue
        
        try:
            # Buffer for the volume name
            vol_name_buffer = ctypes.create_unicode_buffer(1024)
            # GetVolumeInformationW(rootPath, volumeName, volumeNameSize, ...)
            success = ctypes.windll.kernel32.GetVolumeInformationW(
                drive_path, vol_name_buffer, 1024, None, None, None, None, 0
            )
            if success and vol_name_buffer.value == "Kindle":
                # Verify documents folder exists
                if os.path.isdir(os.path.join(drive_path, "documents")):
                    return drive_path
        except Exception:
            continue
    return None
```

- [ ] **Step 2: Verify disk detection logic**
  (Manual Test: Connect Kindle $\rightarrow$ Run script $\rightarrow$ Verify return value. Mock Test: Create a mock function returning "G:\\" to verify the rest of the flow).

---

### Task 2: FileLoc Module Implementation

**Files:**
- Modify: `ClipBackup.py`

- [ ] **Step 1: Implement `backup_clippings` logic**
  Handle renaming of the old file and copying the new one with error handling.

```python
import shutil

def backup_clippings(disk_path):
    """Handles the backup of My Clippings.txt from Kindle to local dir."""
    target_file = "My Clippings.txt"
    old_file = "My Clippings-old.txt"
    source_path = os.path.join(disk_path, "documents", target_file)

    try:
        # 1. Handle existing local file (Option A: Direct Overwrite)
        if os.path.exists(target_file):
            os.replace(target_file, old_file)
        
        # 2. Copy from Kindle to local
        shutil.copy2(source_path, target_file)
        return True
    except (OSError, IOError) as e:
        print(f"\n[Error] 备份失败: {e}")
        return False
```

---

### Task 3: UIHandler Module Implementation

**Files:**
- Modify: `ClipBackup.py`

- [ ] **Step 1: Implement interaction functions**

```python
def prompt_connection():
    """Prompts user to connect Kindle and choice to continue or exit."""
    while True:
        choice = input("\n请将Kindle用USB数据线连接到电脑，然后按下键盘的Y键继续，按N键退出程序: ").strip().upper()
        if choice == 'Y':
            return 'Y'
        elif choice == 'N':
            return 'N'
        else:
            print("输入无效，请输入 Y 或 N。")

def wait_for_exit():
    """Wait for user to press Enter before exiting."""
    input("\n已复制My Clippings.txt文件保存，按回车键结束程序")
```

---

### Task 4: Integration and Main Loop

**Files:**
- Modify: `ClipBackup.py`

- [ ] **Step 1: Implement the `main()` orchestrator**

```python
def main():
    print("=== Kindle 笔记备份工具 ===")
    
    while True:
        disk = find_kindle_disk()
        if disk:
            break
        
        if prompt_connection() == 'N':
            print("程序已退出。")
            return
            
    if backup_clippings(disk):
        wait_for_exit()
    else:
        print("\n备份过程中发生错误，请检查设备连接或文件权限。")
        input("按回车键退出程序...")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Final End-to-End Test**
  1. Run without Kindle $\rightarrow$ Verify $Y/N$ prompt $\rightarrow$ Verify $N$ exits.
  2. Connect Kindle $\rightarrow$ Run $\rightarrow$ Verify `My Clippings.txt` copied.
  3. Run again $\rightarrow$ Verify `My Clippings.txt` moved to `My Clippings-old.txt` and new one copied.
  4. Disconnect Kindle during copy $\rightarrow$ Verify graceful error message.
