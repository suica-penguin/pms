from datetime import datetime
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import tkinter as tk
from typing import Optional, Tuple
from project_manager import ProjectManager

# UI配置常量
UI_CONFIG = {
    'dialog_size': "600x450",
    'padding': "10",
    'entry_width': 12,  # 优化：从5调整为12
    'text_height': 8,
    'spinbox_width': 5,
    'date_entry_width': 12  # 优化：从20调整为12
}

class TaskDialog:
    """任务对话框类，用于创建和编辑任务信息"""

    def __init__(self, parent: tk.Tk, title: str, task: Optional[object] = None) -> None:
        """
        初始化任务对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            task: 可选的任务对象，用于编辑模式
        """
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(UI_CONFIG['dialog_size'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.center_dialog(parent)
        self.create_widgets(task)
        self.dialog.wait_window()

    def center_dialog(self, parent: tk.Tk) -> None:
        """将对话框居中显示在父窗口中心"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self, task: Optional[object]) -> None:
        """创建对话框中的所有控件"""
        frame = ttk.Frame(self.dialog, padding=UI_CONFIG['padding'])
        frame.pack(fill=tk.BOTH, expand=True)

        # 项目编号
        self.create_label_entry(frame, "项目编号:", "project_number", 
                               task.project_number if task else "", 0)
        
        # 项目名称
        self.create_label_entry(frame, "项目名称:", "title", 
                               task.title if task else "", 1)
        
        # 描述
        self.create_text_area(frame, "描述:", task.description if task else "", 2)
        
        # 优先级
        self.create_priority_spinbox(frame, task.priority if task else 1, 3)
        
        # 开始日期
        self.create_date_entry(frame, "开始日期:", "start_date", 
                              task.start_date if task else "", 4)
        
        # 截止日期
        self.create_date_entry(frame, "截止日期:", "due_date", 
                              task.due_date if task else "", 5)
        
        # 日期格式提示 - 优化：合并为一行
        ttk.Label(frame, text="日期格式: YYYY-MM-DD").grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # 按钮框架
        self.create_button_frame(frame, 7)
        
        # 配置网格权重 - 修复变形问题
        frame.columnconfigure(0, weight=0)  # 标签列不扩展
        frame.columnconfigure(1, weight=1)   # 输入框列扩展
        frame.columnconfigure(2, weight=0)   # 提示列不扩展
        frame.columnconfigure(3, weight=0)   # 按钮列不扩展

    def create_label_entry(self, parent: ttk.Frame, label_text: str, var_name: str, 
                          default_value: str, row: int) -> ttk.Entry:
        """创建标签和输入框组合"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        entry = ttk.Entry(parent, textvariable=var, width=UI_CONFIG['entry_width'])
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # 优化：添加焦点优化
        entry.bind('<FocusIn>', lambda e: entry.selection_range(0, tk.END))
        return entry

    def create_text_area(self, parent: ttk.Frame, label_text: str, default_text: str, row: int) -> None:
        """创建文本区域控件"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        text_widget = tk.Text(parent, height=UI_CONFIG['text_height'])
        text_widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        if default_text:
            text_widget.insert("1.0", default_text)
        setattr(self, "desc_text", text_widget)

    def create_priority_spinbox(self, parent: ttk.Frame, default_value: int, row: int) -> None:
        """创建优先级微调框"""
        ttk.Label(parent, text="优先级:").grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.IntVar(value=default_value)
        setattr(self, "priority_var", var)
        spinbox = ttk.Spinbox(parent, from_=1, to=5, textvariable=var, 
                             width=UI_CONFIG['spinbox_width'])
        spinbox.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)

    def create_date_entry(self, parent: ttk.Frame, label_text: str, var_name: str, 
                         default_value: str, row: int) -> None:
        """创建日期选择器"""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        
        # 导入datetime用于日期限制
        from datetime import datetime
        
        # 如果是开始日期，限制只能选择当前日期之前
        max_date = None
        if label_text == "开始日期:":
            max_date = datetime.now()
        
        date_entry = DateEntry(parent, textvariable=var, 
                             width=UI_CONFIG['date_entry_width'],
                             date_pattern='yyyy-mm-dd', locale='zh_CN',
                             maxdate=max_date)  # 添加最大日期限制
        
        # 修复：显式设置日期值，确保在编辑模式下显示任务的原始日期
        if default_value:
            try:
                date_entry.set_date(datetime.strptime(default_value, "%Y-%m-%d"))
            except ValueError:
                # 如果日期格式不正确，保持默认值不变
                pass
        
        date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 添加焦点绑定以减少闪烁
        date_entry.bind('<FocusIn>', lambda e: date_entry.selection_range(0, tk.END))

    def create_button_frame(self, parent: ttk.Frame, row: int) -> None:
        """创建按钮框架"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)

    def validate_date_format(self, date_str: str, field_name: str) -> bool:
        """验证日期格式是否正确"""
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return True
            except ValueError:
                messagebox.showwarning("警告", f"{field_name}格式错误，请使用 YYYY-MM-DD 格式")
                return False
        return True

    def validate_inputs(self) -> bool:
        """验证所有输入"""
        title = self.title_var.get().strip()
        
        if not title:
            messagebox.showwarning("警告", "任务标题不能为空")
            return False

        # 验证日期格式
        if not self.validate_date_format(self.start_date_var.get().strip(), "开始日期"):
            return False
        if not self.validate_date_format(self.due_date_var.get().strip(), "截止日期"):
            return False
            
        return True

    def on_ok(self) -> None:
        """确定按钮点击事件 - 验证输入并返回结果"""
        if not self.validate_inputs():
            return

        description = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        
        self.result = (
            self.title_var.get().strip(),
            description,
            priority,
            self.due_date_var.get().strip() or None,
            self.start_date_var.get().strip() or None,
            self.project_number_var.get().strip() or None
        )
        self.dialog.destroy()

    def on_cancel(self) -> None:
        """取消按钮点击事件"""
        self.dialog.destroy()


class WeeklyTaskDialog:
    """每周任务对话框类，用于创建和编辑每周待办事项"""

    def __init__(self, parent, title, task=None, project_names = None):
        """
        初始化每周任务对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            task: 可选的任务对象，用于编辑模式
            project_name: 可选的项目名称，用于创建模式
        """
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")  # 增加对话框高度以容纳描述字段
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.center_dialog(parent)
        self.create_widgets(task, project_names)
        self.dialog.wait_window()

    def center_dialog(self, parent):
        """将对话框居中显示在父窗口中心"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self, task=None, project_names=None):
        """创建对话框中的所有控件"""
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # 任务名称
        ttk.Label(frame, text="任务名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=task.title if task else "")
        title_entry = ttk.Entry(frame, textvariable=self.title_var, width=30)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # 任务描述 - 新增字段
        ttk.Label(frame, text="任务描述:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(frame, height=3, width=30)
        self.desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # 设置默认值（编辑模式）
        if task and task.description:
            self.desc_text.insert("1.0", task.description)

        # 所属项目
        ttk.Label(frame, text="所属项目:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.project_var = tk.StringVar()
        
        # 使用传入的项目名称列表，避免从project_manager加载
        if project_names is None:
            from project_manager import ProjectManager
            manager = ProjectManager()
            projects = manager.get_all_projects()
            project_names = sorted(set(project.title for project in projects if project.title))
        
        project_options = ["无"] + project_names
        
        project_combo = ttk.Combobox(frame, textvariable=self.project_var, 
                                   values=project_options, width=27)
        project_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)

        # 删除以下重复代码（第268-274行）
        # 提取项目名称：假设项目名称是任务标题中特定的格式
        # 这里可以根据实际需求调整项目名称的提取逻辑
        # project_names = sorted(set(project.title for project in projects if project.title))
        # project_options = ["无"] + project_names
        # 
        # project_combo = ttk.Combobox(frame, textvariable=self.project_var, 
        #                            values=project_options, width=27)
        # project_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 设置默认值（编辑模式）
        if task:
            self.project_var.set(task.project_name or "无")
        else:
            self.project_var.set("无")

        # 紧急程度
        ttk.Label(frame, text="紧急程度:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(frame, textvariable=self.priority_var, 
                                    values=["一般", "重要", "核心"], width=27)
        priority_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 设置默认值（编辑模式）
        if task:
            priority_map = {1: "一般", 2: "重要", 3: "核心"}
            self.priority_var.set(priority_map.get(task.priority, "一般"))
        else:
            self.priority_var.set("一般")

        # 是否完成
        ttk.Label(frame, text="是否完成:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.completed_var = tk.StringVar()
        completed_combo = ttk.Combobox(frame, textvariable=self.completed_var, 
                                      values=["未完成", "已完成"], width=27)
        completed_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 设置默认值（编辑模式）- 修复：使用is_completed而不是status
        if task:
            self.completed_var.set("已完成" if task.is_completed else "未完成")
        else:
            self.completed_var.set("未完成")

        # 预期完成时间
        ttk.Label(frame, text="预期完成时间:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.due_date_var = tk.StringVar(value=task.due_date if task and task.due_date else "")
        due_date_entry = DateEntry(frame, textvariable=self.due_date_var, 
                                 width=20, date_pattern='yyyy-mm-dd', locale='zh_CN')
        
        # 修复：显式设置日期值，确保在编辑模式下显示任务的原始截止日期
        if task and task.due_date:
            due_date_entry.set_date(datetime.strptime(task.due_date, "%Y-%m-%d"))
            
        due_date_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.LEFT, padx=10)

        # 配置网格权重
        frame.columnconfigure(1, weight=1)

    def on_ok(self):
        """确定按钮点击事件"""
        title = self.title_var.get().strip()
        
        if not title:
            messagebox.showwarning("警告", "任务名称不能为空")
            return

        # 验证日期格式
        due_date = self.due_date_var.get().strip()
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("警告", "预期完成时间格式错误，请使用 YYYY-MM-DD 格式")
                return

        # 获取任务描述
        description = self.desc_text.get("1.0", tk.END).strip()

        self.result = (
            title,
            description,  # 新增描述字段
            self.project_var.get(),
            self.priority_var.get(),
            self.completed_var.get(),
            due_date if due_date else None
        )
        self.dialog.destroy()

    def on_cancel(self):
        """取消按钮点击事件"""
        self.dialog.destroy()

    def ok(self):
        """确认按钮点击事件"""
        # ...existing code...
        responsible_person_value = self.responsible_person_var.get()
        
        # --- 开始修改 ---
        # 统一负责人ID的类型为整数
        # 检查输入值是否已经是ID（整数）
        responsible_person_id = None
        all_persons = self.manager.get_all_responsible_persons() # {id: name}
        
        # 尝试将输入值转为整数，看是否为有效的ID
        try:
            person_id_candidate = int(responsible_person_value)
            if person_id_candidate in all_persons:
                responsible_person_id = person_id_candidate
        except (ValueError, TypeError):
            # 转换失败，说明是字符串（新输入的负责人姓名）
            pass

        # 如果没找到ID，说明是新输入的姓名或选择了姓名
        if responsible_person_id is None:
            # 反向查找姓名对应的ID
            person_name_to_id = {name: id for id, name in all_persons.items()}
            if responsible_person_value in person_name_to_id:
                responsible_person_id = person_name_to_id[responsible_person_value]
            else:
                # 是一个全新的负责人，添加并获取新ID
                if responsible_person_value.strip(): # 确保不是空字符串
                    new_person = self.manager.add_responsible_person(responsible_person_value.strip())
                    responsible_person_id = new_person['id']

        self.result['responsible_person'] = responsible_person_id
        # --- 结束修改 ---

        self.result['status'] = self.status_var.get()
        self.result['priority'] = self.priority_var.get()
        # ...existing code...