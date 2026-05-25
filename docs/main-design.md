# Kindle Workflow Orchestrator Design Specification

## 1. Project Overview
The goal is to create a main entry point `main.py` that coordinates the three existing Kindle utility modules into a single, seamless workflow. This program will handle user interaction, sequential execution, error management, and temporary file cleanup.

## 2. Core Requirements
### 2.1 Workflow Sequence
The program must execute the following modules in strict order:
1. `ClipBackup.py`: Backs up `My Clippings.txt` from the device.
2. `KindleParser.py`: Parses the backup file into `My Clippings.csv`.
3. `Convertor.py`: Converts the CSV into a formatted `.xlsx` file.

### 2.2 User Interaction
- **Start**: Prompt the user: `"请用USB数据线将Kindle阅读器连接电脑，按下回车键继续"` and wait for the Enter key.
- **Error State**: If any module fails, display `"程序出错，请按回车键退出"` and wait for the Enter key before terminating.

### 2.3 Cleanup and Maintenance
- **Temporary File Removal**: After the three modules complete successfully, the program must check for the existence of `My Clippings.csv` in the current directory and delete it to keep the workspace clean.

## 3. Technical Implementation
### 3.1 Architecture (Approach A: Modular Import)
The orchestrator will use Python's `import` system to call the `main()` function of each module. This ensures:
- **Direct Execution**: No overhead of starting new shell processes.
- **Packaging Efficiency**: Full compatibility with `PyInstaller` for creation of a single standalone `.exe`.
- **Centralized Error Handling**: A single `try...except` block can wrap the entire sequence.

### 3.2 Execution Logic
1. **Input Wait**: Use `input()` to pause at the start.
2. **Module Chain**:
   ```python
   import ClipBackup
   import KindleParser
   import Convertor
   
   ClipBackup.main()
   KindleParser.main()
   Convertor.main()
   ```
3. **Post-Processing**: Use `os.path.exists()` and `os.remove()` for the CSV file.
4. **Exception Handling**: Catch all `Exception` types to ensure the user is notified and can press Enter before the window closes.

## 4. Robustness and Packaging
- **Encoding**: Ensure all console outputs are handled correctly for Windows environments.
- **Packaging**: The design ensures that all dependencies (including `openpyxl` inside `Convertor`) are discoverable by the compiler for `.exe` generation.
