from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import calendar

class TaskStatus(Enum):
    PENDING = "待开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    DELAYED = "已延期"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class WeeklyTask:
    """每周待办事项类，专门处理每周重复任务"""
    
    title: str = ""
    description: str = ""  # 新增：任务描述
    project_name: Optional[str] = None
    priority: int = Priority.LOW.value
    is_completed: bool = False
    due_date: Optional[str] = None
    start_date: Optional[str] = None  # 新增：开始日期
    week_number: Optional[int] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.week_number:
            self.week_number = self._get_current_week_number()
        if not self.start_date:
            self.start_date = datetime.now().strftime("%Y-%m-%d")
    
    def _get_current_week_number(self) -> int:
        """获取当前周数"""
        today = datetime.now()
        return today.isocalendar()[1]
    
    def is_current_week_task(self) -> bool:
        """检查是否是本周任务"""
        return self.week_number == self._get_current_week_number()
    
    def get_weeks_since_start(self) -> int:
        """获取从开始到现在的周数"""
        if not self.start_date:
            return 0
        
        try:
            start_date_obj = datetime.strptime(self.start_date, "%Y-%m-%d")
            current_date = datetime.now()
            weeks = (current_date - start_date_obj).days // 7
            return max(weeks, 0)
        except ValueError:
            return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeeklyTask':
        """从字典创建WeeklyTask实例"""
        return cls(**data)

@dataclass
class Task:
    """任务类，表示单个项目任务"""
    
    title: str
    description: str = ""
    priority: int = Priority.LOW.value
    status: str = TaskStatus.PENDING.value
    progress: int = 0
    start_date: Optional[str] = None
    updated_at: Optional[str] = None
    due_date: Optional[str] = None
    project_number: Optional[str] = None
    project_name: Optional[str] = None
    # is_weekly: bool = False
    # weekly_task: Optional[WeeklyTask] = None
    
    def __post_init__(self):
        """初始化后处理"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.start_date:
            self.start_date = datetime.now().strftime("%Y-%m-%d")
        if not self.updated_at:
            self.updated_at = current_time
        
        # # 如果是每周任务，初始化WeeklyTask
        # if self.is_weekly and self.weekly_task is None:
        #     self.weekly_task = WeeklyTask()
    
    def update_progress(self, progress: int) -> None:
        """更新任务进度"""
        if not 0 <= progress <= 100:
            raise ValueError("进度必须在0-100之间")
            
        self.progress = progress
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._update_status_based_on_progress()
        
        # # 如果是每周任务，处理周进度逻辑
        # if self.is_weekly and self.weekly_task:
        #     current_week = self.weekly_task._get_current_week_number()
        #     if current_week != self.weekly_task.week_number:
        #         self.progress = self.weekly_task.reset_for_new_week(self.progress)
        #         self.weekly_task.week_number = current_week
        #         self.status = TaskStatus.PENDING.value
    
    def _update_status_based_on_progress(self) -> None:
        """根据进度自动更新状态"""
        if self.progress == 100:
            self.status = TaskStatus.COMPLETED.value
        elif self.progress > 0:
            self.status = TaskStatus.IN_PROGRESS.value
        else:
            self.status = TaskStatus.PENDING.value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        # 移除weekly_task对象，只保存其数据
        if 'weekly_task' in data and data['weekly_task']:
            data['weekly_task'] = asdict(data['weekly_task'])
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建任务实例"""
        # 处理weekly_task数据
        weekly_task_data = data.pop('weekly_task', None)
        task = cls(**data)
        
        if weekly_task_data and task.is_weekly:
            task.weekly_task = WeeklyTask(**weekly_task_data)
        
        return task
    
    def is_overdue(self) -> bool:
        """检查任务是否逾期"""
        if not self.due_date:
            return False
        
        try:
            due_date = datetime.strptime(self.due_date, "%Y-%m-%d")
            return datetime.now() > due_date and self.status != TaskStatus.COMPLETED.value
        except ValueError:
            return False