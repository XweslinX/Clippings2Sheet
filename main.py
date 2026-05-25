import os
import ClipBackup
import KindleParser
import Convertor

def main():
    """
    主程序流程：
    1. 用户确认连接 Kindle  2. 备份文件  3. 解析 CSV  4. 转换 XLSX  5. 清理临时文件
    """

    # 1. 程序开头提示，等待用户按下回车键继续
    print("\n=========================================================")
    print("Clippings2Sheet —— Kindle摘录笔记一键转换工具 Ver. 0.1")
    print("=========================================================\n\n")
    print("\n请用USB数据线将Kindle阅读器连接电脑，按下回车键继续")
    input()

    try:
        # 2. 按顺序调用三个程序模块
        print("\n--- 1. 正在备份 Kindle 摘录文件 ---")
        if not ClipBackup.main():
            print("\n[提示] 备份模块运行停止，主程序将终止。")
            input("\n按下回车键退出程序...")
            return

        print("\n--- 2. 正在解析摘录数据 ---")
        if not KindleParser.main():
            print("\n[提示] 解析模块运行出错，主程序将终止。")
            input("\n按下回车键退出程序...")
            return

        print("\n--- 3. 正在将数据转换为Excel表格文件 ---")
        if not Convertor.main():
            print("\n[提示] 转换出错，主程序将终止。")
            input("\n按下回车键退出程序...")
            return

        # 3. 执行完成后，清理中间产生的 My Clippings.csv 文件
        csv_file = "My Clippings.csv"
        if os.path.exists(csv_file):
            try:
                os.remove(csv_file)
                print(f"\n[清理] 已删除临时文件: {csv_file}")
            except Exception as e:
                print(f"\n[警告] 清理临时文件 {csv_file} 失败: {e}")

        print("\n-----------------------------------------------------")
        print("全部任务执行完成！请在当前目录下查看生成的 .xlsx 文件。")
        print("-----------------------------------------------------")
        input("\n按下回车键退出程序...")

    except Exception as e:
        # 4. 任何模块出错，显示错误信息并等待回车退出
        print("\n" + "!" * 50)
        print(f"程序出错: {e}")
        print("程序出错，请按回车键退出")
        print("!" * 50)
        input()

if __name__ == "__main__":
    main()
