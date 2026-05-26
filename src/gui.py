import logging
from datetime import datetime, timedelta
from tkinter import ttk, messagebox, simpledialog
import tkinter as tk
from typing import Any, Dict, Optional

from dialogs import TaskDialog
from project_manager import ProjectManager
from weekly_task_manager import WeeklyTaskManager

# 配置日志
logger = logging.getLogger(__name__)

class ProjectTasksGUI:
    """项目任务管理图形界面"""

    def __init__(self, parent_frame, manager: ProjectManager):
        self.parent = parent_frame
        self.manager = manager
        self.setup_ui()

    def setup_ui(self):
        """设置任务管理界面"""
        # 筛选框架
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(filter_frame, text="状态筛选:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="所有")
        self.status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                         values=["所有", "待开始", "进行中", "已完成", "已延期"], state="readonly")
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        ttk.Label(filter_frame, text="优先级筛选:").pack(side=tk.LEFT, padx=5)
        self.priority_var = tk.StringVar(value="所有")
        self.priority_combo = ttk.Combobox(filter_frame, textvariable=self.priority_var,
                                           values=["所有", "1", "2", "3", "4", "5"], state="readonly")
        self.priority_combo.pack(side=tk.LEFT, padx=5)
        self.priority_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        # 修改为开始年份筛选
        ttk.Label(filter_frame, text="开始年份筛选:").pack(side=tk.LEFT, padx=5)
        self.year_var = tk.StringVar(value="所有")
        self.year_combo = ttk.Combobox(filter_frame, textvariable=self.year_var, state="readonly")
        self.year_combo.pack(side=tk.LEFT, padx=5)
        self.year_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        ttk.Label(filter_frame, text="项目编号筛选:").pack(side=tk.LEFT, padx=5)
        self.project_number_var = tk.StringVar(value="所有")
        self.project_number_combo = ttk.Combobox(filter_frame, textvariable=self.project_number_var, state="readonly")
        self.project_number_combo.pack(side=tk.LEFT, padx=5)
        self.project_number_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        # 任务列表
        tree_container = ttk.Frame(self.parent)
        columns = ("project_number", "title", "progress", "status", "priority", "start_date", "due_date")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)

        headings = {
            "project_number": ("项目编号", 100), "title": ("项目名称", 200), "progress": ("进度", 80),
            "status": ("状态", 80), "priority": ("优先级", 80), "start_date": ("开始日期", 100),
            "due_date": ("截止日期", 100)
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮区放底部并优先 pack，确保在窗口缩小时按钮仍可见
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))
        buttons = {
            "添加项目": (self.add_task, 'Success.TButton'), "编辑项目": (self.edit_task, 'Primary.TButton'),
            "删除项目": (self.delete_task, 'Danger.TButton'), "更新进度": (self.update_progress, 'Warning.TButton'),
            "刷新": (self.refresh_task_list, 'Primary.TButton')
        }
        for text, (command, style) in buttons.items():
            ttk.Button(button_frame, text=text, command=command, style=style).pack(side=tk.LEFT, padx=5)

        # 再将列表容器 pack，保证其在按钮之上可伸缩
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.refresh_task_list()

    def refresh_task_list(self):
        """刷新任务列表"""
        try:
            # 获取项目列表（兼容多种管理器接口）
            if hasattr(self.manager, "get_all_projects"):
                projects = self.manager.get_all_projects()
            elif hasattr(self.manager, "list_projects"):
                projects = self.manager.list_projects()
            else:
                logger.warning("manager 未实现 get_all_projects/list_projects，刷新为空")
                projects = []

            if not hasattr(self, "tree"):
                return

            # 辅助函数：统一从对象或字典取字段
            def _get_field(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                try:
                    return getattr(obj, key, default)
                except Exception:
                    return default

            # 清空旧项并插入新项
            for item in self.tree.get_children():
                self.tree.delete(item)
            for task in projects:
                pn = _get_field(task, "project_number", "无")
                title = _get_field(task, "title", "")
                progress = _get_field(task, "progress", 0) or 0
                status = _get_field(task, "status", "")
                priority = _get_field(task, "priority", "")
                start_date = _get_field(task, "start_date", "")
                due_date = _get_field(task, "due_date", "")
                self.tree.insert("", "end", iid=str(pn), values=(
                    pn or "无", title, f"{progress}%", status, priority, start_date, due_date or "无"
                ))
            
            # 更新开始年份筛选器选项
            if hasattr(self, 'year_combo'):
                years = set()
                for task in projects:
                    start_date = _get_field(task, "start_date", "")
                    if start_date:
                        try:
                            # 尝试从开始日期提取年份
                            if len(start_date) >= 4 and start_date[:4].isdigit():
                                years.add(start_date[:4])
                            else:
                                # 尝试解析日期格式
                                date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                                years.add(str(date_obj.year))
                        except (ValueError, TypeError):
                            continue
                self.year_combo['values'] = ["所有"] + sorted(years)
        except Exception:
            logger.exception("刷新项目列表失败")

    def filter_tasks(self, event=None):
        """筛选任务"""
        # 直接调用已有实现（若不存在则刷新全部）
        try:
            if hasattr(self, "refresh_task_list"):
                # 先刷新全部，再按条件过滤（与原逻辑一致）
                self.refresh_task_list()
            else:
                return
            status = getattr(self, "status_var", tk.StringVar(value="所有")).get()
            priority = getattr(self, "priority_var", tk.StringVar(value="所有")).get()
            year = getattr(self, "year_var", tk.StringVar(value="所有")).get()
            
            for item_id in list(self.tree.get_children()):
                values = self.tree.item(item_id, "values")
                item_status = values[3]
                item_priority = values[4]
                item_start_date = values[5]
                keep = True
                
                if status != "所有" and item_status != status:
                    keep = False
                if priority != "所有" and item_priority != priority:
                    keep = False
                if year != "所有" and item_start_date:
                    try:
                        # 尝试从日期字符串中提取年份
                        if len(item_start_date) >= 4 and item_start_date[:4].isdigit():
                            item_year = item_start_date[:4]
                        else:
                            # 尝试解析标准日期格式
                            date_obj = datetime.strptime(item_start_date, "%Y-%m-%d")
                            item_year = str(date_obj.year)
                        if item_year != year:
                            keep = False
                    except (ValueError, TypeError):
                        # 如果日期格式不正确，则不显示该项
                        keep = False
                
                if not keep:
                    self.tree.delete(item_id)
        except Exception:
            logger.exception("筛选项目时出错")

    def _get_selected_project_number(self):
        """获取Treeview中选中项的项目编号"""
        try:
            selected = getattr(self, "tree", None)
            if not selected:
                messagebox.showwarning("警告", "没有可选择的项目控件")
                return None
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("警告", "请先选择一个项目")
                return None
            return self.tree.item(sel[0], "values")[0]
        except Exception:
            logger.exception("获取选中项目编号时出错")
            return None

    def add_task(self):
        """添加新项目"""
        try:
            dialog = TaskDialog(self.parent, "添加项目")
            if not getattr(dialog, "result", None):
                return
            
            # 使用标准方法，不再需要兼容性检查
            if self.manager.add_project(*dialog.result):
                self.manager.save_data()
                self.refresh_task_list()
                messagebox.showinfo("成功", "项目添加成功!")
            else:
                messagebox.showerror("错误", "保存项目失败")
        except Exception:
            logger.exception("添加项目时出错")
            messagebox.showerror("错误", "添加项目时发生异常")
    
    def edit_task(self):
        """编辑项目"""
        try:
            project_number = self._get_selected_project_number()
            if not project_number or project_number == "无":
                return
            
            # 使用标准方法
            project = self.manager.get_project_by_number(project_number)
            if not project:
                messagebox.showwarning("警告", "未找到选中项目的数据")
                return
                
            dialog = TaskDialog(self.parent, "编辑项目", project)
            if not getattr(dialog, "result", None):
                return
                
            updates = {}
            # 如果 dialog.result 是序列，按已有映射生成 dict
            if isinstance(dialog.result, (list, tuple)):
                keys = ["title", "description", "priority", "due_date", "start_date", "project_number"]
                updates = dict(zip(keys, dialog.result))
            elif isinstance(dialog.result, dict):
                updates = dialog.result
                
            # 使用标准方法
            if self.manager.update_project(project_number, updates):
                self.refresh_task_list()
                messagebox.showinfo("成功", "项目更新成功!")
            else:
                messagebox.showerror("错误", "更新项目失败")
        except Exception:
            logger.exception("编辑项目时出错")
            messagebox.showerror("错误", "编辑项目时发生异常")
    
    def update_progress(self):
        """更新项目进度"""
        try:
            project_number = self._get_selected_project_number()
            if not project_number or project_number == "无":
                return
                
            project = self.manager.get_project_by_number(project_number)
            if not project:
                messagebox.showwarning("警告", "未找到选中项目的数据")
                return
                
            # 修复：只使用getattr获取progress属性，不尝试使用字典的get方法
            current = getattr(project, "progress", 0)
            new_progress = simpledialog.askinteger("更新进度", f"请输入 '{getattr(project,'title', '')}' 的新进度 (0-100):",
                                                   initialvalue=current, minvalue=0, maxvalue=100)
            if new_progress is None:
                return
                
            # 使用标准方法
            if self.manager.update_project_progress(project_number, new_progress):
                self.refresh_task_list()
                messagebox.showinfo("成功", "进度更新成功!")
            else:
                messagebox.showerror("错误", "更新进度失败")
        except Exception:
            logger.exception("更新进度时出错")
            messagebox.showerror("错误", "更新进度时发生异常")

    def delete_task(self):
        """删除项目"""
        try:
            project_number = self._get_selected_project_number()
            if not project_number or project_number == "无":
                return
            if not messagebox.askyesno("确认", f"确定要删除项目 '{project_number}' 吗？"):
                return
            # 调用 manager.delete_project 或 remove_project
            ok = False
            if hasattr(self.manager, "delete_project"):
                ok = self.manager.delete_project(project_number)
            elif hasattr(self.manager, "remove_project"):
                ok = self.manager.remove_project(project_number)
            if ok:
                if hasattr(self.manager, "save"):
                    self.manager.save()
                elif hasattr(self.manager, "_save_data"):
                    self.manager._save_data()
                self.refresh_task_list()
                messagebox.showinfo("成功", "项目删除成功!")
            else:
                messagebox.showerror("错误", "删除项目失败")
        except Exception:
            logger.exception("删除项目时出错")
            messagebox.showerror("错误", "删除项目时发生异常")

class WeeklyTaskView:
    """每周待办视图（优化版）"""

    def __init__(self, parent, manager: WeeklyTaskManager):
        self.frame = ttk.Frame(parent, padding="10")
        self.manager = manager
        self.week_str = self.manager.get_current_week_str()
        self.task_widgets = {}
        self.empty_state_label = None
        self.setup_ui()
        self.refresh_tasks()

    def _get_week_date_range(self, week_str: str) -> str:
        """根据 week_str 返回周起止日期字符串"""
        try:
            y, w = map(int, week_str.split("-W"))
            start = datetime.fromisocalendar(y, w, 1).date()
            end = start + timedelta(days=6)
            return f"{start.strftime('%Y-%m-%d')} — {end.strftime('%Y-%m-%d')}"
        except Exception:
            return ""

    def setup_ui(self):
        # 设置头部
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(header_frame, text="本周待办", style='Header.TLabel').pack(side='left')
        
        date_range = self._get_week_date_range(self.week_str)
        subtitle_text = f" {self.week_str}" + (f" — {date_range}" if date_range else "")
        ttk.Label(header_frame, text=subtitle_text, style='SubHeader.TLabel').pack(side='left', padx=(8, 0))
        
        # 设置按钮
        button_box = ttk.Frame(header_frame)
        button_box.pack(side='right')
        ttk.Button(button_box, text="添加待办", command=self.add_task, style='Accent.TButton').pack(side='right', padx=4)
        ttk.Button(button_box, text="顺延未完成至下周", command=self.rollover_incomplete, style='Primary.TButton').pack(side='right', padx=4)
        
        # 任务列表框架
        self.task_list_frame = ttk.Frame(self.frame)
        self.task_list_frame.pack(fill='both', expand=True)

    def refresh_tasks(self):
        # 清除现有任务和空状态标签
        for widget in self.task_list_frame.winfo_children(): widget.destroy()
        self.task_widgets.clear()
        self.empty_state_label = None
        
        # 获取并显示任务
        tasks = self.manager.get_tasks_by_week(self.week_str)
        if not tasks:
            self.empty_state_label = ttk.Label(
                self.task_list_frame, text="暂无待办事项，点击'添加待办'创建新任务", 
                font=('Microsoft YaHei UI', 10), foreground='#8e8e93')
            self.empty_state_label.pack(pady=20)
        else:
            # 显示任务列表
            for task in sorted(tasks, key=lambda t: t['id']):
                self._create_task_widget(task)

    def _create_task_widget(self, task: Dict[str, Any]):
        task_id = task['id']
        task_frame = ttk.Frame(self.task_list_frame)
        task_frame.pack(fill='x', pady=2)

        # 复选框和输入框
        completed_var = tk.BooleanVar(value=task['completed'])
        ttk.Checkbutton(task_frame, variable=completed_var, command=lambda tid=task_id: self.toggle_task_completion(tid)).pack(side='left')
        
        entry = tk.Entry(task_frame, font=('微软雅黑', 10), fg='gray' if task['completed'] else 'black')
        entry.insert(0, task['content'])
        entry.pack(side='left', fill='x', expand=True, padx=5)
        for event in ("<FocusOut>", "<Return>"):
            entry.bind(event, lambda e, tid=task_id: self.update_task_content(tid))
        
        # 删除按钮
        ttk.Button(task_frame, text="删除", command=lambda tid=task_id: self.delete_task(tid)).pack(side='right')
        
        self.task_widgets[task_id] = {'var': completed_var, 'entry': entry, 'frame': task_frame}
        if task['completed']: entry.config(font=('微软雅黑', 10, 'overstrike'))

    def add_task(self):
        new_task = self.manager.add_task("新待办事项...", self.week_str)
        if self.empty_state_label and self.empty_state_label.winfo_exists():
            self.empty_state_label.destroy()
        self._create_task_widget(new_task)

    def delete_task(self, task_id: int):
        if messagebox.askyesno("确认", "确定要删除这个待办事项吗？"):
            if self.manager.delete_task(task_id) and task_id in self.task_widgets:
                widget_info = self.task_widgets.pop(task_id)
                if widget_info['frame'].winfo_exists(): widget_info['frame'].destroy()
            if not self.task_widgets: self.refresh_tasks()

    def toggle_task_completion(self, task_id: int):
        widget_info = self.task_widgets[task_id]
        is_completed = widget_info['var'].get()
        self.manager.update_task(task_id, {"completed": is_completed})
        widget_info['entry'].config(
            font=('微软雅黑', 10, 'overstrike' if is_completed else 'normal'),
            fg='gray' if is_completed else 'black')

    def update_task_content(self, task_id: int):
        widget_info = self.task_widgets[task_id]
        new_content = widget_info['entry'].get()
        task = self.manager._find_task(task_id)
        if task and task['content'] != new_content:
            self.manager.update_task(task_id, {"content": new_content})

    def rollover_incomplete(self):
        """将本周未完成的任务顺延到下一周并刷新视图。"""
        try:
            next_week = self.manager.get_next_week_str(self.week_str)
            count = self.manager.rollover_incomplete_tasks(self.week_str, next_week)
            if count:
                messagebox.showinfo("顺延完成", f"已将 {count} 个未完成事项顺延到 {next_week}")
            else:
                messagebox.showinfo("没有未完成事项", "当前周没有未完成的待办需要顺延")
            self.refresh_tasks()
        except Exception:
            logger.exception("顺延未完成任务时出错")

class ProjectManagerGUI:
    """项目进度管理图形界面（主控制器，已优化）"""

    def __init__(self, root, manager: Optional[ProjectManager] = None, weekly_task_manager: Optional[WeeklyTaskManager] = None):
        self.root = root
        self.root.title("项目进度管理系统")
        self.root.state('zoomed')
        self.root.configure(bg='#ecf0f1')

        # 使用注入的管理器，或创建默认实例
        self.manager = manager if manager is not None else ProjectManager()
        self.weekly_task_manager = weekly_task_manager if weekly_task_manager is not None else WeeklyTaskManager()
        
        self.views = {}
        self.current_view_name = None
        
        self.setup_ui()
        self.show_view("weekly") # 默认显示每周待办

    def setup_ui(self):
        """设置用户界面"""
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, pady=(10, 0), padx=20)

        self.weekly_btn = ttk.Button(nav_frame, text="每周待办", command=lambda: self.show_view("weekly"), style='Nav.TButton')
        self.weekly_btn.pack(side=tk.LEFT, padx=5)
        self.project_btn = ttk.Button(nav_frame, text="项目管理", command=lambda: self.show_view("project"), style='Nav.TButton')
        self.project_btn.pack(side=tk.LEFT, padx=5)

        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建所有视图
        # 每周视图：直接使用 WeeklyTaskView 的内层 frame 作为可切换视图
        weekly_view = WeeklyTaskView(self.main_container, self.weekly_task_manager)
        self.views["weekly"] = {"frame": weekly_view.frame, "gui": weekly_view}
        # 项目视图：使用独立容器作为项目 GUI 的父容器
        project_frame = ttk.Frame(self.main_container)
        project_gui = ProjectTasksGUI(project_frame, self.manager)
        self.views["project"] = {"frame": project_frame, "gui": project_gui}

    def show_view(self, view_name: str):
        """切换并显示指定视图"""
        if self.current_view_name == view_name:
            return

        # 隐藏当前视图
        if self.current_view_name and self.current_view_name in self.views:
            self.views[self.current_view_name]["frame"].pack_forget()

        # 更新按钮样式
        self.weekly_btn.configure(style='Nav.TButton' if view_name != 'weekly' else 'Nav.Selected.TButton')
        self.project_btn.configure(style='Nav.TButton' if view_name != 'project' else 'Nav.Selected.TButton')

        # 显示新视图
        self.current_view_name = view_name
        self.views[view_name]["frame"].pack(fill=tk.BOTH, expand=True)
        
        # 如果是项目视图，刷新一下以加载最新数据
        if view_name == "project":
            self.views["project"]["gui"].refresh_task_list()
        # 如果是每周视图，刷新任务以确保显示历史数据
        elif view_name == "weekly":
            try:
                self.views["weekly"]["gui"].refresh_tasks()
            except Exception:
                logger.exception("刷新每周待办视图时出错")