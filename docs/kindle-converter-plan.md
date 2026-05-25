# Kindle Note Converter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `Convertor.py` to transform `My Clippings.csv` into a professionally formatted `.xlsx` file with multiple sheets and specific styling.

**Architecture:** A linear data pipeline: Read CSV $\rightarrow$ Group by Book $\rightarrow$ Numeric Sort $\rightarrow$ Format & Export to XLSX using `openpyxl`.

**Tech Stack:** Python 3.x, `openpyxl` (external library), `csv`, `datetime`, `collections`.

---

### Task 1: Project Foundation and Data Grouping

**Files:**
- Create: `Convertor.py`

- [ ] **Step 1: Setup imports and basic structure**
```python
import csv
import openpyxl
from openpyxl.styles import Font, Alignment
from datetime import datetime
from collections import defaultdict
import os

def main():
    input_file = "My Clippings.csv"
    # implementation here
```

- [ ] **Step 2: Implement CSV reading and grouping by book**
Read `My Clippings.csv` using `utf-8-sig`, and group entries by book title.
```python
def group_data_by_book(file_path):
    books_data = defaultdict(list)
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}")
        return None
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book = row.get('书名', 'Unknown Book')
            books_data[book].append(row)
    return books_data
```

- [ ] **Step 3: Implement numeric sorting for '位置'**
Ensure the "位置" field is treated as an integer for sorting.
```python
def sort_entries(entries):
    # Use a lambda that converts '位置' to int if possible, otherwise 0
    return sorted(entries, key=lambda x: int(x['位置']) if x['位置'].isdigit() else 0)
```

---

### Task 2: Excel Generation and Formatting

**Files:**
- Modify: `Convertor.py`

- [ ] **Step 1: Implement dynamic filename generation**
```python
def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"Clippings-{timestamp}.xlsx"
```

- [ ] **Step 2: Implement Workbook and Sheet creation with truncation**
Handle the 31-character limit for sheet names.
```python
def create_workbook(grouped_data):
    wb = openpyxl.Workbook()
    # Remove the default sheet created by openpyxl
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    for book_title, entries in grouped_data.items():
        # Truncate to 31 chars as per requirement
        safe_title = book_title[:31]
        ws = wb.create_sheet(title=safe_title)
        # Process sheet...
    return wb
```

- [ ] **Step 3: Implement Table Layout (Headers and Column Widths)**
Set the 5 columns and their specific widths.
```python
def setup_sheet_layout(ws):
    headers = ["位置", "页码", "摘录", "笔记", "日期"]
    widths = [15, 10, 100, 50, 20]
    
    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = Font(size=14, bold=True)
        
    # Set column widths
    for col_num, width in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = width
```

- [ ] **Step 4: Implement Data Writing and Styling**
Write sorted data, set font size 12, enable wrap text, and dynamic row height.
```python
def write_data_to_sheet(ws, entries):
    # Sort data first
    sorted_entries = sort_entries(entries)
    
    for row_idx, entry in enumerate(sorted_entries, 2):
        row_data = [entry['位置'], entry['页码'], entry['摘录内容'], entry['笔记内容'], entry['日期时间']]
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = Font(size=12)
            # Enable wrap text for Excerpt and Note columns (3 and 4)
            if col_idx in [3, 4]:
                cell.alignment = Alignment(wrapText=True, vertical='top')
        
        # Dynamic Row Height based on '摘录内容'
        # Heuristic: length of text / approx chars per line * line height
        content = entry['摘录内容']
        line_count = (len(content) // 60) + 1 # Crude estimate for wrap
        ws.row_dimensions[row_idx].height = 15 * line_count + 5 # 15 is approx base height
```

- [ ] **Step 5: Implement Freeze Panes and Final Save**
```python
def finalize_sheet(ws):
    ws.freeze_panes = "A2"

# In main:
# wb.save(generate_filename())
```

---

### Task 3: Integration and Verification

**Files:**
- Modify: `Convertor.py`

- [ ] **Step 1: Integrate all functions into `main()` flow**
- [ ] **Step 2: Run the program with `My Clippings.csv`**
- [ ] **Step 3: Verify the output file `.xlsx` matches all 7 requirements**

```bash
python Convertor.py
```

---

### Self-Review Checklist
- [ ] Book $\rightarrow$ Sheet mapping? (Yes)
- [ ] Sheet name $\le 31$ chars? (Yes)
- [ ] Sorted by `位置` numerically? (Yes)
- [ ] 5 columns with specific widths? (Yes)
- [ ] Header: 14pt, Bold? (Yes)
- [ ] Body: 12pt? (Yes)
- [ ] Row height dynamic for Excerpts? (Yes)
- [ ] Top row frozen? (Yes)
- [ ] Filename with timestamp to second? (Yes)
- [ ] `utf-8-sig` used for CSV? (Yes)
- [ ] `openpyxl` used? (Yes)
