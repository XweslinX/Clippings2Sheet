import ctypes
import os
import shutil

def find_kindle_disk():
    """
    扫描电脑所有盘符，寻找卷标名为 'Kindle' 且包含 'documents' 文件夹的磁盘。
    """
    # 遍历 A 到 Z 所有可能的盘符
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{drive}:\\"
        # 检查该盘符是否存在（是否已挂载）
        if not os.path.exists(drive_path):
            continue

        try:
            # 创建一个缓冲区用于存储卷标名称 (Volume Name)
            vol_name_buffer = ctypes.create_unicode_buffer(1024)
            # 调用 Windows API GetVolumeInformationW 获取磁盘详细信息
            success = ctypes.windll.kernel32.GetVolumeInformationW(
                drive_path, vol_name_buffer, 1024, None, None, None, None, 0
            )
            if success and vol_name_buffer.value == "Kindle":
                # 进一步验证该分区根目录下是否存在 documents 文件夹
                if os.path.isdir(os.path.join(drive_path, "documents")):
                    return drive_path # 返回找到的 Kindle 磁盘路径 (如 "G:\")
        except Exception:
            continue
    return None

def backup_clippings(disk_path):
    """
    处理 Kindle 笔记文件的备份逻辑：
    将 Kindle 盘符下的 documents\My Clippings.txt 复制到当前程序目录下。
    """
    target_file = "My Clippings.txt"
    old_file = "My Clippings-old.txt"
    source_path = os.path.join(disk_path, "documents", target_file)

    try:
        # 1. 处理本地已存在的文件：如果当前目录下已有 My Clippings.txt，则将其重命名为 My Clippings-old.txt (覆盖旧备份)
        if os.path.exists(target_file):
            os.replace(target_file, old_file)

        # 2. 从 Kindle 设备复制文件到本地目录
        # 使用 shutil.copy2 以尽可能保留原文件的元数据（如修改时间）
        shutil.copy2(source_path, target_file)
        return True
    except (OSError, IOError) as e:
        # 捕获设备断开、权限不足等 I/O 错误
        print(f"\n[错误] 备份失败: {e}")
        return False

def prompt_connection():
    """
    提示用户连接 Kindle 设备，并处理 Y/N 输入逻辑。
    """
    while True:
        choice = input("\n请将Kindle用USB数据线连接到电脑，然后按下键盘的Y键继续，按N键退出程序: ").strip().upper()
        if choice == 'Y':
            return 'Y'
        elif choice == 'N':
            return 'N'
        else:
            # 处理非预期输入
            print("输入无效，请输入 Y 或 N。")

def wait_for_exit():
    print("\n已导出Kindle笔记\n")

def main():
    """
    主控制流程
    返回 True 表示成功执行备份，False 表示用户选择退出。
    """
    print("正在检测Kindle...")

    # 第一步：连接检查循环
    while True:
        disk = find_kindle_disk()
        if disk:
            break # 成功检测到 Kindle，跳出循环

        # 未检测到，提示用户
        if prompt_connection() == 'N':
            print("用户选择退出。")
            return False # 明确返回 False 表示用户请求停止执行

    # 第二步：执行文件备份
    if backup_clippings(disk):
        # 备份成功
        # 注意：在作为模块被调用时，不再打印 wait_for_exit() 的信息，由 main.py 统一控制
        return True
    else:
        # 备份失败，给出提示并等待回车退出
        print("\n备份过程中发生错误，请检查设备连接或文件权限。")
        input("按回车键退出程序...")
        return False
if __name__ == "__main__":
    main()
