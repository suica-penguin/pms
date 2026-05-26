import json
import os
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry  # 添加日历控件导入
from typing import List, Dict, Optional
import tkinter as tk
from gui import ProjectManagerGUI
from styles import setup_styles
import logging
from weekly_task_manager import WeeklyTaskManager

def _locate_weekly_data() -> str:
    """查找或创建 weekly_data.json，优先使用历史位置。"""
    base = os.path.dirname(__file__)
    candidates = [
        os.path.join(base, "weekly_data.json"),
        os.path.join(base, "data", "weekly_data.json"),
        os.path.join(os.path.dirname(base), "weekly_data.json"),
        os.path.join(os.path.dirname(base), "data", "weekly_data.json"),
        os.path.join(os.path.dirname(os.path.dirname(base)), "weekly_data.json"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "weekly_data.json")

def _configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger(__name__).info("logging configured")

# 主程序入口
def main():
    """
    项目进度管理系统主入口函数

    初始化Tkinter主窗口并启动应用程序
    """
    _configure_logging()

    root = tk.Tk()  # 创建Tkinter主窗口对象，作为整个应用程序的容器
    setup_styles()  # 调用样式设置函数，配置应用程序的统一样式和外观

    # 定位历史 weekly 数据并注入 WeeklyTaskManager，确保界面读取历史记录
    weekly_file = _locate_weekly_data()
    logging.getLogger(__name__).info("using weekly data file: %s", os.path.abspath(weekly_file))
    weekly_mgr = WeeklyTaskManager(data_file=weekly_file)

    # 诊断信息：打印加载后的数据摘要，帮助定位为什么界面没有历史记录
    try:
        tasks = weekly_mgr.data.get("tasks", [])
        logging.getLogger(__name__).info("weekly tasks loaded: %d", len(tasks))
        weeks = sorted({t.get("week") for t in tasks if t.get("week")})
        logging.getLogger(__name__).info("weeks present in data: %s", weeks)
    except Exception:
        logging.getLogger(__name__).exception("读取 weekly_mgr.data 时出错")

    # 将 weekly_mgr 注入 GUI，确保切换视图时能读取并刷新历史数据
    app = ProjectManagerGUI(root, weekly_task_manager=weekly_mgr)
    root.mainloop()  # 启动Tkinter主事件循环，使应用程序进入交互状态，等待用户操作

if __name__ == "__main__":
    main()

# pyinstaller -F -w -p ./src ./src/main.py --distpath ./output/dist --workpath ./output/build