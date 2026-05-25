import os
import csv
import re
from collections import defaultdict

def read_clippings_file(file_path):
    """
    以 utf-8-sig 编码读取文件内容，自动处理 UTF-8 BOM 标记。
    """
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            # 返回所有行，以便后续状态机处理
            return f.readlines()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

def cleanup_output_file(file_path):
    """
    在程序运行之初，如果当前目录下已存在 My Clippings.csv，则将其删除。
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"清理旧文件失败: {e}")

def parse_clippings(lines):
    """
    使用状态机解析文本行，将 My Clippings.txt 转换为原始条目列表。
    """
    entries = []
    state = "IDLE" # 初始状态：寻找书名
    current_entry = {}

    for line in lines:
        clean_line = line.strip()

        # 遇到分隔符，结束当前条目，重置状态
        if clean_line == "==========":
            if current_entry:
                entries.append(current_entry)
            current_entry = {}
            state = "IDLE"
            continue

        # 状态 [IDLE]: 寻找书名 (非空行即书名)
        if state == "IDLE" and clean_line:
            current_entry['book'] = clean_line
            state = "METADATA"

        # 状态 [METADATA]: 解析元数据行 (以 '- Your' 开头)
        elif state == "METADATA" and clean_line.startswith("- Your"):
            # 1. 提取类型: Highlight, Note, 或 Bookmark
            if "Highlight" in clean_line:
                entry_type = "Highlight"
            elif "Note" in clean_line:
                entry_type = "Note"
            else:
                entry_type = "Bookmark"
            current_entry['type'] = entry_type

            # 2. 提取位置 (Location): 匹配数字或范围 (例如 123 或 123-124)
            loc_match = re.search(r"Location (\d+(?:-\d+)?)", clean_line)
            current_entry['location'] = loc_match.group(1) if loc_match else "Unknown"

            # 3. 提取页码 (Page): 匹配 'page ' 后跟数字
            page_match = re.search(r"page (\d+)", clean_line)
            current_entry['page'] = page_match.group(1) if page_match else ""

            # 4. 提取时间 (Added on ...): 匹配 'Added on ' 之后的所有内容
            time_match = re.search(r"Added on (.*)", clean_line)
            current_entry['date'] = time_match.group(1) if time_match else ""

            state = "CONTENT"

        # 状态 [CONTENT]: 读取正文内容 (直到遇到分隔符)
        elif state == "CONTENT":
            if not clean_line and not current_entry.get('content'):
                continue

            if 'content' not in current_entry:
                current_entry['content'] = line.rstrip('\n')
            else:
                current_entry['content'] += "\n" + line.rstrip('\n')

    if current_entry:
        entries.append(current_entry)

    return entries

def get_loc_range(loc_str):
    """
    将位置字符串转换为数值区间 (start, end)。
    例如: "200-220" -> (200, 220), "210" -> (210, 210).
    """
    if not loc_str or loc_str == "Unknown":
        return (None, None)

    parts = loc_str.split('-')
    try:
        start = int(parts[0])
        end = int(parts[1]) if len(parts) > 1 else start
        return (start, end)
    except ValueError:
        return (None, None)

def merge_entries(raw_entries):
    """
    根据 (书名, 位置区间) 将高亮摘录 (Highlight) 与用户笔记 (Note) 合并到同一行。
    同位置冲突的 Highlight 各自独立成行，不合并。
    """
    merged = {} # key: (book, start, end, seq)
    notes_pending = []
    collision_counter = {}

    for entry in raw_entries:
        if entry['type'] in ["Highlight", "Bookmark"]:
            book = entry.get('book', 'Unknown')
            loc_str = entry.get('location', 'Unknown')
            start, end = get_loc_range(loc_str)

            base_key = (book, start, end)
            seq = collision_counter.get(base_key, 0)
            collision_counter[base_key] = seq + 1
            key = (book, start, end, seq)

            merged[key] = {
                "书名": book,
                "摘录内容": entry.get('content', '').strip(),
                "笔记内容": "",
                "日期时间": entry.get('date', ''),
                "页码": entry.get('page', ''),
                "位置": loc_str
            }
        elif entry['type'] == "Note":
            notes_pending.append(entry)

    for note in notes_pending:
        book = note.get('book', 'Unknown')
        loc_str = note.get('location', 'Unknown')

        note_val = None
        if loc_str and loc_str.isdigit():
            note_val = int(loc_str)
        elif '-' in loc_str:
            try:
                note_val = int(loc_str.split('-')[0])
            except ValueError:
                pass

        matched = False
        for key, data in merged.items():
            if key[0] == book and key[1] is not None and note_val is not None:
                if key[1] <= note_val <= key[2]:
                    data["笔记内容"] = note.get('content', '').strip()
                    matched = True
                    break

        if not matched:
            start, end = get_loc_range(loc_str)
            key = (book, start, end, "NOTE_ONLY")
            merged[key] = {
                "书名": book,
                "摘录内容": "",
                "笔记内容": note.get('content', '').strip(),
                "日期时间": note.get('date', ''),
                "页码": "",
                "位置": loc_str
            }

    return merged

def export_to_csv(merged_data, output_path):
    """
    将合并后的数据导出为 CSV 文件。
    """
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

def main():
    """
    主程序流程：清理 -> 读取 -> 解析 -> 合并 -> 导出
    返回 True 表示成功，False 表示失败。
    """
    input_file = "My Clippings.txt"
    output_file = "My Clippings.csv"

    cleanup_output_file(output_file)

    print(f"正在读取 {input_file}...")
    lines = read_clippings_file(input_file)
    if not lines:
        return False

    print("正在解析数据...")
    raw_entries = parse_clippings(lines)

    print("正在执行关联合并...")
    merged_data = merge_entries(raw_entries)

    print(f"正在导出至 {output_file}...")
    if export_to_csv(merged_data, output_file):
        print("\n成功！解析完成，已生成结构化文件：My Clippings.csv")
        print(f"共处理 {len(raw_entries)} 条原始记录合并为 {len(merged_data)} 条唯一记录。")
        return True
    else:
        print("\n导出过程中出现错误，请检查文件权限。")
        return False

if __name__ == "__main__":
    main()
