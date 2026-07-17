# Clippings2Sheet —— Kindle摘录笔记一键转换工具

**Clippings2Sheet** 是一款高效的 Kindle 笔记整理工具。它能够自动化地完成从 Kindle 设备备份笔记到解析结构化数据转换为Excel文件的全流程。

它解决了 Kindle 原生 `My Clippings.txt` 文件难以阅读、笔记与高亮分离、缺乏排序等痛点，将碎片化的读书记录转化为一份专业、可筛选、可检索的电子表格文件。

(本项目使用Claude Code + Gemma4制作)

This tool is for exporting and converting Kindle highlights and notes into a single Excel .xlsx file. What you need to do is connecting your kindle to your PC, then launch the .exe file of this tool, and press enter key. It will automatically generate an Excel .xlsx file at the current directory as where the tool is placed.

2026-7-17 update: English version added

## 核心特性

- **一键全流程自动化**：通过 `main.py` 引导，依次完成导出、解析和转换，无需手动操作中间文件。
- **智能关联合并**：采用**位置区间匹配算法**，将同一位置的“高亮摘录 (Highlight)”与“用户笔记 (Note)”智能合并到同一行。
- **导出Excel文件**：
    - **单表结构**：所有笔记汇总至一张以日期命名的工作表，避免多表碎片化。
    - **专业排版**：预设列宽、14号加粗表头、12号正文字体、冻结首行。
    - **阅读优化**：支持摘录内容自动换行，并根据文本长度动态计算行高，确保内容完整可见。
    - **快速检索**：首列“书名”开启自动筛选功能，可一键筛选特定书籍。
- **零依赖部署**：利用Pyinstaller打包为独立 `.exe` 文件，无需在目标电脑安装 Python 环境即可运行，支持32位和64位Win7/8.1/10/11系统。
- **鲁棒性设计**：完美处理 `utf-8-sig` 编码（防止中文乱码）
## 如何使用（任选其一）

### 1：直接运行可执行文件（推荐）
如果您下载的是发布版本（Release）中的 `.exe` 文件：
1. 将 `Clippings2Sheet.exe` 放置在一个文件夹中。
2. 双击运行程序。
3. 根据屏幕提示，用 USB 数据线将 Kindle 连接至电脑。
4. 按下 **回车键**，程序将自动完成所有工作。
5. 完成后，在同目录下查看生成的 `Clippings-YYYYMMDDHHMMSS.xlsx` 文件。

### 2：通过 Python 源代码运行
如果您希望运行源代码，请确保安装了 Python 3.x。

1. **克隆项目**：
   ```bash
   git clone https://github.com/XweslinX/Clippings2Sheet.git
   cd Clippings2Sheet
   ```
2. **安装依赖**：
   ```bash
   pip install openpyxl
   ```
3. **启动程序**：
   ```bash
   python main.py
   ```

## 工作原理

本项目由三个核心模块组成，通过 `main.py` 进行编排：

1.  **`ClipBackup.py`**：通过 Windows API 自动扫描磁盘，寻找卷标为 "Kindle" 的设备，并将 `documents/My Clippings.txt` 备份至本地。
2.  **`KindleParser.py`**：解析非结构化文本，并将高亮与笔记按位置区间进行数值级匹配合并，导出为临时的 `My Clippings.csv`。
3.  **`Convertor.py`**：读取 CSV 数据，执行二级排序，并使用 `openpyxl` 库构建符合专业排版标准的 `.xlsx` 报告。

## 项目结构

```text
.
├── main.py              # 程序主入口 (工作流编排)
├── ClipBackup.py        # 模块1：设备扫描与文件导出
├── KindleParser.py      # 模块2：解析文件与数据合并
└── Convertor.py         # 模块3：Excel格式化转换
```

## 导出表格栏目说明

| 栏目 | 宽度 | 说明 | 对齐方式 |
| :--- | :--- | :--- | :--- |
| **书名** | 30 | 书籍名称 (支持筛选)(自动换行) | 居中 |
| **位置** | 15 | Kindle 内部位置数值 | 居中 |
| **页码** | 10 | 对应的页码信息 | 居中 |
| **摘录** | 100 | 高亮选中的原文内容 (自动换行) | 左对齐 |
| **笔记** | 50 | 针对该高亮所写的笔记 (自动换行) | 左对齐 |
| **日期时间** | 20 | 记录创建的时间 | 居中 |

## 开源协议
[MIT License](LICENSE)

---
**Made with ❤️ for Kindle Readers.**
