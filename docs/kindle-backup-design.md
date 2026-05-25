# Kindle 笔记备份程序 (ClipBackup.py) 设计文档

## 1. 项目概述
本程序旨在实现将 Kindle 设备中的 `My Clippings.txt` 笔记文件自动备份到本地计算机的流程。程序重点在于高通用性（零依赖）、高稳定性（异常处理）以及简单的用户交互。

## 2. 核心需求
- **运行环境**：Windows 系统，Python 3.x。
- **输入文件**：Kindle 盘符 $\rightarrow$ `documents\My Clippings.txt`。
- **输出文件**：程序同级目录下 $\rightarrow$ `My Clippings.txt`。
- **备份机制**：若本地已存在备份，则将其重命名为 `My Clippings-old.txt`（覆盖旧备份）。
- **连接检测**：通过磁盘卷标 `"Kindle"` 和 `documents` 文件夹的存在与否判定设备是否连接。

## 3. 技术实现方案

### 3.1 模块化架构
程序采用模块化功能结构，分为三个核心模块：

#### A. `FindDisk` (磁盘检测模块)
- **实现方式**：使用 `ctypes` 调用 Windows API `GetVolumeInformationW`。
- **检测逻辑**：
    1. 遍历 `A:` 到 `Z:` 盘符。
    2. 获取每个盘符的卷标 (Volume Label)。
    3. 匹配卷标 $\text{==} \text{"Kindle"}$。
    4. 验证该盘符根目录下是否存在 `documents` 文件夹。
- **返回值**：成功则返回盘符根路径 (如 `"G:\"`)，失败返回 `None`。

#### B. `FileLoc` (文件搬运模块)
- **备份逻辑**：
    1. 检查本地当前路径是否存在 `My Clippings.txt`。
    2. 若存在，使用 `os.replace` 将其重命名为 `My Clippings-old.txt` (方案 A：直接覆盖)。
    3. 使用 `shutil.copy2` 将 Kindle 中的文件复制到本地。
- **异常处理**：
    - 捕获 `OSError` (设备意外断开或文件权限被占用)。
- **返回值**：成功返回 `True`，失败返回 `False`。

#### C. `UIHandler` (交互模块)
- **交互流程**：
    1. **连接提示**：输出连接引导信息 $\rightarrow$ 接收 $Y/N$ 输入 $\rightarrow$ 过滤空格并统一大写。
    2. **退出提示**：输出成功信息 $\rightarrow$ 等待用户按下回车键。

### 3.2 数据流向
`main()` $\rightarrow$ `FindDisk` $\rightarrow$ (若未找到) $\rightarrow$ `UIHandler(Y/N)` $\rightarrow$ `FindDisk` $\rightarrow$ (找到) $\rightarrow$ `FileLoc` $\rightarrow$ `UIHandler(Enter)` $\rightarrow$ `Exit`

## 4. 鲁棒性与边界处理
| 场景 | 处理策略 |
| :--- | :--- |
| **Kindle未连接** | 进入 $Y/N$ 循环，直到设备连接或用户选择 $N$ 退出 |
| **非法字符输入** | 对 $Y/N$ 输入进行 `.strip().upper()` 过滤，非 $Y/N$ 提示无效并重新输入 |
| **备份文件被占用** | 捕获 `os.replace` 或 `shutil.copy2` 的权限异常，提示用户关闭占用程序 |
| **设备中途断开** | 捕获复制过程中的 `IOError/OSError`，提示设备断开并引导重启程序 |
| **零依赖保证** | 仅使用 Python 标准库 (`os`, `shutil`, `ctypes`)，无需 `pip install` |

## 5. 成功标准
- 程序启动 $\rightarrow$ 检测到 Kindle $\rightarrow$ 成功复制文件 $\rightarrow$ 按回车结束。
- 程序启动 $\rightarrow$ 未检测到 Kindle $\rightarrow$ 输入 $N$ $\rightarrow$ 程序正常退出。
- 程序启动 $\rightarrow$ 本地有旧备份 $\rightarrow$ 旧备份被更名为 `-old.txt` $\rightarrow$ 新备份存入。
