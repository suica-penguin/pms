import json
import os
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry  # 添加日历控件导入
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


# 设置现代主题样式
def setup_styles():
    style = ttk.Style()
    style.theme_use('clam')  # 使用现代主题

    # 配色方案
    primary_color = '#2c3e50'    # 主色调 - 深蓝色
    secondary_color = '#3498db'  # 次要色调 - 蓝色
    success_color = '#27ae60'    # 成功色 - 绿色
    warning_color = '#f39c12'    # 警告色 - 橙色
    danger_color = '#e74c3c'     # 危险色 - 红色
    light_bg = '#ecf0f1'         # 浅色背景
    dark_text = '#2c3e50'        # 深色文字

    # 字体配置优化
    base_font = ('微软雅黑', 10)
    bold_font = ('微软雅黑', 10, 'bold')
    title_font = ('微软雅黑', 14, 'bold')
    large_font = ('微软雅黑', 12)
    small_font = ('微软雅黑', 9)

    # 配置按钮样式 - 优化字体
    style.configure('TButton', padding=8, font=bold_font)
    style.map('TButton',
              background=[('active', secondary_color),
                          ('pressed', primary_color)],
              foreground=[('active', 'white'), ('pressed', 'white')])

    # 配置特殊按钮样式
    style.configure('Primary.TButton', background=primary_color,
                    foreground='white', font=bold_font)
    style.configure('Success.TButton', background=success_color,
                    foreground='white', font=bold_font)
    style.configure('Warning.TButton', background=warning_color,
                    foreground='white', font=bold_font)
    style.configure('Danger.TButton', background=danger_color,
                    foreground='white', font=bold_font)

    # 配置导航按钮样式 - 无边框，选中状态字体加粗带下划线
    style.configure('Nav.TButton', font=base_font, borderwidth=0, relief='flat', padding=(
        10, 5), background=light_bg, foreground=dark_text)

    # 选中状态的导航按钮样式
    style.configure('Nav.Selected.TButton',
                    font=('微软雅黑', 10, 'bold underline'),
                    borderwidth=0,
                    relief='flat',
                    padding=(10, 5),
                    background=light_bg,
                    foreground=primary_color)
    # # 新增：移除导航按钮的焦点虚线边框
    # style.map('Nav.TButton', focus=[('focuscolor', '')])
    # style.map('Nav.Selected.TButton', focus=[('focuscolor', '')])
    # 配置标签样式 - 增加更多字体选项
    style.configure('TLabel', font=base_font, foreground=dark_text)
    style.configure('Title.TLabel', font=title_font, foreground=primary_color)
    style.configure('Large.TLabel', font=large_font, foreground=dark_text)
    style.configure('Small.TLabel', font=small_font, foreground=dark_text)

    # 配置组合框样式
    style.configure('TCombobox', padding=6, font=base_font)

    # 配置树状视图样式 - 优化字体显示
    style.configure('Treeview', font=base_font, rowheight=30,
                    fieldbackground=light_bg, background='white')
    style.configure('Treeview.Heading', font=('微软雅黑', 12, 'bold'),
                    background=primary_color, foreground='white')

    # 配置条目样式（用于输入框等）
    style.configure('TEntry', font=base_font, padding=5)

    # 配置框架样式
    style.configure('TFrame', background=light_bg)

    # 配置滚动条样式
    style.configure('Vertical.TScrollbar', background=secondary_color)
    style.configure('Horizontal.TScrollbar', background=secondary_color)


class Task:
    """任务类，表示单个项目任务"""

    def __init__(self, title: str, description: str = "", priority: int = 1,
                 due_date: Optional[str] = None, start_date: Optional[str] = None,
                 project_number: Optional[str] = None):
        self.title = title
        self.description = description
        self.priority = priority  # 1-5，数字越大优先级越高
        self.status = "待开始"  # 待开始、进行中、已完成、已延期
        self.start_date = start_date if start_date else datetime.now().strftime("%Y-%m-%d")
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.due_date = due_date
        self.progress = 0  # 进度百分比
        self.project_number = project_number  # 项目编号

    def update_progress(self, progress: int):
        """更新任务进度"""
        if 0 <= progress <= 100:
            self.progress = progress
            self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if progress == 100:
                self.status = "已完成"
            elif progress > 0:
                self.status = "进行中"
            else:
                self.status = "待开始"

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'progress': self.progress,
            'start_date': self.start_date,
            'updated_at': self.updated_at,
            'due_date': self.due_date,
            'project_number': self.project_number
        }


    def from_dict(cls, data: Dict) -> 'Task':
        """从字典创建任务实例"""
        task = cls(data['title'], data['description'], data['priority'],
                   data['due_date'], data['start_date'], data.get('project_number'))
        task.status = data['status']
        task.progress = data['progress']
        task.updated_at = data['updated_at']
        return task


class ProjectManager:
    """项目管理器，负责任务的增删改查和持久化"""

    def __init__(self, data_file: str = "project_data.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_tasks()

    def add_task(self, title: str, description: str = "", priority: int = 1,
                 due_date: Optional[str] = None, start_date: Optional[str] = None,
                 project_number: Optional[str] = None) -> Task:
        """添加新任务"""
        task = Task(title, description, priority,
                    due_date, start_date, project_number)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def remove_task(self, task_index: int) -> bool:
        """删除项目"""
        if 0 <= task_index < len(self.tasks):
            del self.tasks[task_index]
            self.save_tasks()
            return True
        return False

    def update_task_progress(self, task_index: int, progress: int) -> bool:
        """更新任务进度"""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].update_progress(progress)
            self.save_tasks()
            return True
        return False

    def get_task(self, task_index: int) -> Optional[Task]:
        """获取指定任务"""
        if 0 <= task_index < len(self.tasks):
            return self.tasks[task_index]
        return None

    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return self.tasks

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """按状态筛选任务"""
        return [task for task in self.tasks if task.status == status]

    def get_tasks_by_priority(self, priority: int) -> List[Task]:
        """按优先级筛选任务"""
        return [task for task in self.tasks if task.priority == priority]

    def get_tasks_by_project_number(self, project_number: str) -> List[Task]:
        """按项目编号筛选任务"""
        return [task for task in self.tasks if task.project_number == project_number]

    def save_tasks(self):
        """保存任务到文件"""
        data = [task.to_dict() for task in self.tasks]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        """从文件加载任务"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Loaded data: {data}")  # 调试信息
                    self.tasks = [Task.from_dict(item) for item in data]
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading tasks: {e}")  # 调试信息
                self.tasks = []
            except Exception as e:
                print(f"Unexpected error: {e}")  # 调试信息
                self.tasks = []
        else:
            self.tasks = []


class ProjectManagerGUI:
    """项目进度管理图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("项目进度管理系统")
        # 设置全屏显示
        self.root.state('zoomed')  # Windows系统全屏
        # 设置窗口背景色
        self.root.configure(bg='#ecf0f1')

        self.manager = ProjectManager()
        self.current_view = "split"  # 当前视图模式: split, weekly, project

        # 保存各个视图的框架引用
        self.views = {}

        self.setup_ui()
        self.refresh_task_list()
        self.refresh_weekly_tasks()

    def setup_ui(self):
        """设置用户界面"""
        # 顶部导航栏
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        # 导航按钮 - 使用新的无边框样式
        self.weekly_btn = ttk.Button(nav_frame, text="每周待办事项",
                                    command=self.show_weekly_view,
                                    style='Nav.TButton')
        self.weekly_btn.pack(side=tk.LEFT, padx=5)

        self.project_btn = ttk.Button(nav_frame, text="项目信息",
                                     command=self.show_project_view,
                                     style='Nav.TButton')
        self.project_btn.pack(side=tk.LEFT, padx=5)

        # 初始选中项目信息按钮
        self.select_button(self.weekly_btn)
     # 导航按钮
        # ttk.Button(nav_frame, text="分屏显示", command=self.show_split_view,
        # #           style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        # ttk.Button(nav_frame, text="每周待办事项", command=self.show_weekly_view,
        #            style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        # ttk.Button(nav_frame, text="项目信息", command=self.show_project_view,
        #            style='Primary.TButton').pack(side=tk.LEFT, padx=5)

        # 主容器框架
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 预先创建所有视图但隐藏
        self.create_all_views()

        # 初始化显示项目信息视图（而不是分屏视图）
        self.show_weekly_view()

    def select_button(self, selected_button):
        """设置按钮选中状态"""
        # 重置所有按钮样式
        self.weekly_btn.configure(style='Nav.TButton')
        self.project_btn.configure(style='Nav.TButton')

        # 设置选中按钮样式
        selected_button.configure(style='Nav.Selected.TButton')

    def create_all_views(self):
        """创建所有视图框架"""
        # 移除分屏视图创建代码

        # 每周待办事项视图
        weekly_frame = ttk.Frame(self.main_container, padding="10")
        self.setup_weekly_tasks_ui(weekly_frame)
        self.views["weekly"] = weekly_frame

        # 项目信息视图
        project_frame = ttk.Frame(self.main_container, padding="10")
        self.setup_task_management_ui(project_frame)
        self.views["project"] = project_frame

        # 初始隐藏所有视图
        for view in self.views.values():
            view.pack_forget()

    # def show_split_view(self):
    #     """显示分屏视图"""
    #     self.switch_view("split")

    def show_weekly_view(self):
        """显示每周待办事项视图"""
        self.switch_view("weekly")

    def show_project_view(self):
        """显示项目信息视图"""
        self.switch_view("project")

    def switch_view(self, view_name):
        """切换视图"""
        # 隐藏当前视图
        if hasattr(self, 'current_view_frame'):
            self.current_view_frame.pack_forget()

        # 显示新视图
        self.current_view_frame = self.views[view_name]
        self.current_view_frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = view_name

        # 刷新数据
        if view_name in ["split", "project"]:
            self.refresh_task_list()
        if view_name in ["split", "weekly"]:
            self.refresh_weekly_tasks()
        # 更新按钮选中状态 - 新增代码
        # 新增代码：更新按钮选中状态
        if view_name == "weekly":
            self.select_button(self.weekly_btn)
        elif view_name == "project":
          self.select_button(self.project_btn)
          
    def setup_weekly_tasks_ui(self, parent):
        """设置每周待办事项界面"""
        # 标题
        title_label = ttk.Label(parent, text="本周待办事项", style='Title.TLabel')
        title_label.pack(pady=(0, 15))

        # 周选择器
        week_frame = ttk.Frame(parent)
        week_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(week_frame, text="选择周:").pack(side=tk.LEFT, padx=(0, 5))

        # 获取当前周数
        current_week = datetime.now().isocalendar()[1]
        week_options = [f"第{i}周" for i in range(1, 53)]

        self.week_var = tk.StringVar(value=f"第{current_week}周")
        week_combo = ttk.Combobox(
            week_frame, textvariable=self.week_var, values=week_options, width=10)
        week_combo.pack(side=tk.LEFT)
        week_combo.bind("<<ComboboxSelected>>", self.refresh_weekly_tasks)

        # 每周任务列表
        weekly_frame = ttk.Frame(parent)
        weekly_frame.pack(fill=tk.BOTH, expand=True)

        # 创建树状视图显示每周任务
        weekly_columns = ("title", "priority", "status", "progress")
        self.weekly_tree = ttk.Treeview(
            weekly_frame, columns=weekly_columns, show="headings", height=15)

        # 设置列标题
        self.weekly_tree.heading("title", text="项目名称")
        self.weekly_tree.heading("priority", text="优先级")
        self.weekly_tree.heading("status", text="状态")
        self.weekly_tree.heading("progress", text="进度")

        # 设置列宽度
        self.weekly_tree.column("title", width=150, anchor='center')
        self.weekly_tree.column("priority", width=80, anchor='center')
        self.weekly_tree.column("status", width=80, anchor='center')
        self.weekly_tree.column("progress", width=80, anchor='center')

        # 滚动条
        weekly_scrollbar = ttk.Scrollbar(
            weekly_frame, orient=tk.VERTICAL, command=self.weekly_tree.yview)
        self.weekly_tree.configure(yscrollcommand=weekly_scrollbar.set)

        self.weekly_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        weekly_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 统计信息
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=(10, 0))

        self.total_label = ttk.Label(stats_frame, text="总任务: 0")
        self.total_label.pack(side=tk.LEFT, padx=(0, 10))

        self.completed_label = ttk.Label(stats_frame, text="已完成: 0")
        self.completed_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_label = ttk.Label(stats_frame, text="总进度: 0%")
        self.progress_label.pack(side=tk.LEFT)

    def setup_task_management_ui(self, parent):
        """设置任务管理界面"""
        # 筛选框架
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(filter_frame, text="状态筛选:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                         values=["所有", "待开始", "进行中", "已完成", "已延期"])
        self.status_combo.set("所有")
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        ttk.Label(filter_frame, text="优先级筛选:").pack(side=tk.LEFT, padx=5)
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(filter_frame, textvariable=self.priority_var,
                                           values=["所有", "1", "2", "3", "4", "5"])
        self.priority_combo.set("所有")
        self.priority_combo.pack(side=tk.LEFT, padx=5)
        self.priority_combo.bind("<<ComboboxSelected>>", self.filter_tasks)

        ttk.Label(filter_frame, text="项目编号筛选:").pack(side=tk.LEFT, padx=5)
        self.project_number_var = tk.StringVar()
        self.project_number_combo = ttk.Combobox(filter_frame, textvariable=self.project_number_var,
                                                 values=["所有"] + sorted(set(task.project_number for task in self.manager.get_all_tasks() if task.project_number)))
        self.project_number_combo.set("所有")
        self.project_number_combo.pack(side=tk.LEFT, padx=5)
        self.project_number_combo.bind(
            "<<ComboboxSelected>>", self.filter_tasks)

        # 任务列表容器框架 - 使用pack布局
        tree_container = ttk.Frame(parent)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 任务列表
        columns = ("project_number", "title", "progress",
                   "status", "priority", "start_date", "due_date")
        self.tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", height=15)

        # 设置列标题
        self.tree.heading("project_number", text="项目编号")
        self.tree.heading("title", text="项目名称")
        self.tree.heading("progress", text="进度")
        self.tree.heading("status", text="状态")
        self.tree.heading("priority", text="优先级")
        self.tree.heading("start_date", text="开始日期")
        self.tree.heading("due_date", text="截止日期")

        # 设置列宽度
        self.tree.column("project_number", width=100, anchor='center')
        self.tree.column("title", width=200, anchor='center')
        self.tree.column("progress", width=80, anchor='center')
        self.tree.column("status", width=80, anchor='center')
        self.tree.column("priority", width=80, anchor='center')
        self.tree.column("start_date", width=100, anchor='center')
        self.tree.column("due_date", width=100, anchor='center')

        # 滚动条
        scrollbar = ttk.Scrollbar(
            tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 使用pack布局（与父容器一致）
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮框架
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(button_frame, text="添加任务", command=self.add_task,
                   style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="编辑任务", command=self.edit_task,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除项目", command=self.delete_task,
                   style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="更新进度", command=self.update_progress,
                   style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_task_list,
                   style='Primary.TButton').pack(side=tk.LEFT, padx=5)

    def refresh_weekly_tasks(self, event=None):
        """刷新每周待办事项"""
        # 清空现有数据
        for item in self.weekly_tree.get_children():
            self.weekly_tree.delete(item)

        # 获取当前周的任务
        current_week = datetime.now().isocalendar()[1]
        selected_week = int(
            self.week_var.get().replace("第", "").replace("周", ""))

        tasks = self.manager.get_all_tasks()
        weekly_tasks = []

        for task in tasks:
            if task.start_date:
                try:
                    task_week = datetime.strptime(
                        task.start_date, "%Y-%m-%d").isocalendar()[1]
                    if task_week == selected_week:
                        weekly_tasks.append(task)
                except ValueError:
                    continue

        # 添加任务到每周列表
        total_tasks = len(weekly_tasks)
        completed_tasks = 0
        total_progress = 0

        for task in weekly_tasks:
            self.weekly_tree.insert("", "end", values=(
                task.title,
                task.priority,
                task.status,
                f"{task.progress}%"
            ))

            if task.status == "已完成":
                completed_tasks += 1
            total_progress += task.progress

        # 更新统计信息
        avg_progress = total_progress / total_tasks if total_tasks > 0 else 0

        self.total_label.config(text=f"总任务: {total_tasks}")
        self.completed_label.config(text=f"已完成: {completed_tasks}")
        self.progress_label.config(text=f"平均进度: {avg_progress:.1f}%")

    def refresh_task_list(self):
        """刷新任务列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 更新项目编号筛选器选项
        project_numbers = sorted(set(
            task.project_number for task in self.manager.get_all_tasks() if task.project_number))
        self.project_number_combo['values'] = ["所有"] + project_numbers

        # 添加新数据
        tasks = self.manager.get_all_tasks()
        for task in tasks:
            self.tree.insert("", "end", values=(
                task.project_number or "无",
                task.title,
                f"{task.progress}%",
                task.status,
                task.priority,
                task.start_date,
                task.due_date or "无"
            ))

    def filter_tasks(self, event=None):
        """筛选任务"""
        status_filter = self.status_var.get()
        priority_filter = self.priority_var.get()
        project_number_filter = self.project_number_var.get()

        tasks = self.manager.get_all_tasks()

        if status_filter != "所有":
            tasks = [t for t in tasks if t.status == status_filter]

        if priority_filter != "所有":
            tasks = [t for t in tasks if t.priority == int(priority_filter)]

        if project_number_filter != "所有":
            tasks = [t for t in tasks if t.project_number ==
                     project_number_filter]

        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加筛选后的数据
        for task in tasks:
            self.tree.insert("", "end", values=(
                task.project_number or "无",
                task.title,
                f"{task.progress}%",
                task.status,
                task.priority,
                task.start_date,
                task.due_date or "无"
            ))

    def add_task(self):
        """添加新任务"""
        dialog = TaskDialog(self.root, "添加任务")
        if dialog.result:
            title, description, priority, due_date, start_date, project_number = dialog.result
            self.manager.add_task(
                title, description, priority, due_date, start_date, project_number)
            self.refresh_task_list()
            messagebox.showinfo("成功", "任务添加成功!")

    def edit_task(self):
        """编辑任务"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return

        item = self.tree.item(selected[0])
        task_index = self.tree.index(selected[0])
        task = self.manager.get_task(task_index)

        if task:
            dialog = TaskDialog(self.root, "编辑任务", task)
            if dialog.result:
                title, description, priority, due_date, start_date, project_number = dialog.result
                # 更新任务信息
                task.title = title
                task.description = description
                task.priority = priority
                task.due_date = due_date
                task.start_date = start_date
                task.project_number = project_number
                task.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.manager.save_tasks()
                self.refresh_task_list()
                messagebox.showinfo("成功", "任务更新成功!")

    def delete_task(self):
        """删除项目"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return

        task_index = self.tree.index(selected[0])

        if messagebox.askyesno("确认", "确定要删除这个任务吗？"):
            if self.manager.remove_task(task_index):
                self.refresh_task_list()
                messagebox.showinfo("成功", "任务删除成功!")
            else:
                messagebox.showerror("错误", "删除项目失败")

    def update_progress(self):
        """更新任务进度"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个任务")
            return

        task_index = self.tree.index(selected[0])
        task = self.manager.get_task(task_index)

        if task:
            progress = simpledialog.askinteger("更新进度",
                                               f"请输入 {task.title} 的进度 (0-100):",
                                               minvalue=0, maxvalue=100,
                                               initialvalue=task.progress)
            if progress is not None:
                self.manager.update_task_progress(task_index, progress)
                self.refresh_task_list()
                messagebox.showinfo("成功", "进度更新成功!")


class TaskDialog:
    """任务对话框"""

    def __init__(self, parent, title, task=None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self.create_widgets(task)

        self.dialog.wait_window()

    def create_widgets(self, task):
        """创建对话框控件"""
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # 项目编号
        ttk.Label(frame, text="项目编号:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.project_number_var = tk.StringVar(
            value=task.project_number if task and task.project_number else "")
        project_number_entry = ttk.Entry(
            frame, textvariable=self.project_number_var, width=40)
        project_number_entry.grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # 标题
        ttk.Label(frame, text="项目名称:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=task.title if task else "")
        title_entry = ttk.Entry(frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # 描述
        ttk.Label(frame, text="描述:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(frame, width=40, height=4)
        self.desc_text.grid(row=2, column=1, sticky=(
            tk.W, tk.E), pady=5, padx=5)
        if task and task.description:
            self.desc_text.insert("1.0", task.description)

        # 优先级
        ttk.Label(frame, text="优先级:").grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.IntVar(value=task.priority if task else 1)
        priority_spin = ttk.Spinbox(
            frame, from_=1, to=5, textvariable=self.priority_var, width=5)
        priority_spin.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)

        # 开始日期
        ttk.Label(frame, text="开始日期:").grid(
            row=4, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar(
            value=task.start_date if task and task.start_date else "")
        start_date_entry = DateEntry(frame, textvariable=self.start_date_var, width=20,
                                     date_pattern='yyyy-mm-dd', locale='zh_CN')
        start_date_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)

        # 截止日期
        ttk.Label(frame, text="截止日期:").grid(
            row=5, column=0, sticky=tk.W, pady=5)
        self.due_date_var = tk.StringVar(
            value=task.due_date if task and task.due_date else "")
        due_date_entry = DateEntry(frame, textvariable=self.due_date_var, width=20,
                                   date_pattern='yyyy-mm-dd', locale='zh_CN')
        due_date_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(frame, text="格式: YYYY-MM-DD").grid(row=5,
                                                     column=2, sticky=tk.W, pady=5)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(
            side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(
            side=tk.LEFT, padx=10)

        # 配置网格权重
        frame.columnconfigure(1, weight=0)

    def on_ok(self):
        """确定按钮点击事件"""
        project_number = self.project_number_var.get().strip()
        title = self.title_var.get().strip()

        if not title:
            messagebox.showwarning("警告", "标题不能为空")
            return

        description = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        start_date = self.start_date_var.get().strip()
        due_date = self.due_date_var.get().strip()

        # 验证日期格式
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("警告", "开始日期格式错误，请使用 YYYY-MM-DD 格式")
                return

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("警告", "截止日期格式错误，请使用 YYYY-MM-DD 格式")
                return
        self.result = (title, description, priority, due_date if due_date else None,
                       start_date if start_date else None, project_number if project_number else None)
        self.dialog.destroy()

    def on_cancel(self):
        """取消按钮点击事件"""
        self.dialog.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    # setup_styles()  # 应用样式
    app = ProjectManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()