# Kindle Note Parser Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a Python tool to parse `My Clippings.txt` and export it to a CSV, merging Highlights and Notes based on their location ranges.

**Architecture:** A pipeline consisting of a state-machine parser, a location-range based merging algorithm, and a `utf-8-sig` CSV exporter.

**Tech Stack:** Python 3.x, Standard Library (`os`, `csv`, `re`, `collections`).

---

### Task 1: Foundation and File IO

**Files:**
- Create: `KindleParser.py`

- [ ] **Step 1: Implement `read_clippings_file` with BOM support**
  Use `utf-8-sig` encoding to handle the Kindle file format.

```python
import os
import csv
import re

def read_clippings_file(file_path):
    """Reads the My Clippings.txt file using utf-8-sig encoding."""
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return f.readlines()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None
```

- [ ] **Step 2: Implement the output cleanup logic**
  Add a function to delete the existing `My Clippings.csv` before processing starts.

```python
def cleanup_output_file(file_path):
    """Deletes the existing output CSV file if it exists."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"清理旧文件失败: {e}")
```

---

### Task 2: State-Machine Parser Implementation

**Files:**
- Modify: `KindleParser.py`

- [ ] **Step 1: Implement the `parse_clippings` state machine**
  Extract raw data into a list of dictionaries.

```python
def parse_clippings(lines):
    """Parses raw lines into a list of raw entry dictionaries using a state machine."""
    entries = []
    state = "IDLE"
    current_entry = {}

    for line in lines:
        clean_line = line.strip()
        if clean_line == "==========":
            if current_entry: entries.append(current_entry)
            current_entry, state = {}, "IDLE"
            continue

        if state == "IDLE" and clean_line:
            current_entry['book'] = clean_line
            state = "METADATA"
        elif state == "METADATA" and clean_line.startswith("- Your"):
            entry_type = "Highlight" if "Highlight" in clean_line else ("Note" if "Note" in clean_line else "Bookmark")
            current_entry['type'] = entry_type
            loc_match = re.search(r"Location (\d+(?:-\d+)?)", clean_line)
            current_entry['location'] = loc_match.group(1) if loc_match else "Unknown"
            page_match = re.search(r"page (\d+)", clean_line)
            current_entry['page'] = page_match.group(1) if page_match else ""
            time_match = re.search(r"Added on (.*)", clean_line)
            current_entry['date'] = time_match.group(1) if time_match else ""
            state = "CONTENT"
        elif state == "CONTENT":
            if not clean_line and not current_entry.get('content'): continue
            if 'content' not in current_entry:
                current_entry['content'] = line.rstrip('\n')
            else:
                current_entry['content'] += "\n" + line.rstrip('\n')
    if current_entry: entries.append(current_entry)
    return entries
```

---

### Task 3: Range-Based Merging Algorithm

**Files:**
- Modify: `KindleParser.py`

- [ ] **Step 1: Implement location range helper**
  Function to convert "200-220" or "210" into `(start, end)` integers.

```python
def get_loc_range(loc_str):
    """Converts a location string into a tuple of (start, end) integers."""
    if loc_str == "Unknown": return (None, None)
    parts = loc_str.split('-')
    try:
        start = int(parts[0])
        end = int(parts[1]) if len(parts) > 1 else start
        return (start, end)
    except ValueError:
        return (None, None)
```

- [ ] **Step 2: Implement `merge_entries` with range matching**
  Iterate through Highlights first to build the base, then merge Notes based on range.

```python
def merge_entries(raw_entries):
    """Merges Notes into Highlights if the Note location is within the Highlight range."""
    merged = {} # key: (book, loc_start, loc_end)
    notes_pending = []

    # Phase 1: Process Highlights and Bookmarks
    for entry in raw_entries:
        if entry['type'] in ["Highlight", "Bookmark"]:
            book = entry.get('book', 'Unknown')
            loc_str = entry.get('location', 'Unknown')
            start, end = get_loc_range(loc_str)
            key = (book, start, end)
            merged[key] = {
                "书名": book, "摘录内容": entry.get('content', '').strip(),
                "笔记内容": "", "日期时间": entry.get('date', ''),
                "页码": entry.get('page', ''), "位置": loc_str
            }
        elif entry['type'] == "Note":
            notes_pending.append(entry)

    # Phase 2: Merge Notes into Highlights via range check
    for note in notes_pending:
        book = note.get('book', 'Unknown')
        note_loc = int(note.get('location', -1)) if note.get('location', '').isdigit() else -1
        
        matched = False
        for key, data in merged.items():
            # Check: Same book AND (Highlight.start <= Note.loc <= Highlight.end)
            if key[0] == book and key[1] is not None and key[1] <= note_loc <= key[2]:
                data["笔记内容"] = note.get('content', '').strip()
                matched = True
                break
        
        if not matched:
            # Create independent entry for notes without corresponding highlights
            key = (book, note.get('location', 'Unknown'), note.get('location', 'Unknown'))
            merged[key] = {
                "书名": book, "摘录内容": "", "笔记内容": note.get('content', '').strip(),
                "日期时间": note.get('date', ''), "页码": "", "位置": note.get('location', 'Unknown')
            }
    return merged
```

---

### Task 4: CSV Export and Main Integration

**Files:**
- Modify: `KindleParser.py`

- [ ] **Step 1: Implement `export_to_csv`**
  Use `utf-8-sig` and `csv.DictWriter`.

```python
def export_to_csv(merged_data, output_path):
    sorted_data = sorted(merged_data.values(), key=lambda x: (x["书名"], x["位置"]))
    fieldnames = ["书名", "摘录内容", "笔记内容", "日期时间", "页码", "位置"]
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_data)
        return True
    except Exception as e:
        print(f"导出 CSV 失败: {e}")
        return False
```

- [ ] **Step 2: Implement `main()` with cleanup and flow**

```python
def main():
    input_file = "My Clippings.txt"
    output_file = "My Clippings.csv"
    
    cleanup_output_file(output_file)
    lines = read_clippings_file(input_file)
    if not lines: return
    
    raw = parse_clippings(lines)
    merged = merge_entries(raw)
    if export_to_csv(merged, output_file):
        print(f"\n成功！已生成: {output_file}")
    else:
        print("\n导出失败。")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: End-to-End Verification**
  Verify a case with `Highlight (200-220)` and `Note (210)` results in a single CSV row.
