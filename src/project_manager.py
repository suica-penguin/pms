from datetime import datetime
import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from task import Task
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectManager:
    """项目管理器，专门负责项目的增删改查和持久化"""
    
    def __init__(self, data_file: str = "project_data.json"):
        """初始化项目管理器"""
        self.data_file = Path(data_file)
        self.projects: List[Task] = []
        self.load_data()
    
    def load_data(self) -> None:
        """从文件加载项目数据"""
        if not self.data_file.exists():
            logger.info("项目数据文件不存在，创建空列表")
            self.projects = []
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.projects = [Task.from_dict(item) for item in data]
            logger.info(f"成功加载 {len(self.projects)} 个项目")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"加载项目信息失败: {e}")
            self.projects = []
        except Exception as e:
            logger.error(f"加载数据时发生未知错误: {e}")
            self.projects = []
    
    def save_data(self) -> bool:
        """保存项目数据到文件"""
        try:
            # 确保目录存在
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            project_data = [task.to_dict() for task in self.projects]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功保存 {len(self.projects)} 个项目")
            return True
        except (IOError, PermissionError) as e:
            logger.error(f"保存项目信息失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存数据时发生未知错误: {e}")
            return False
    
    def add_project(self, title: str, description: str = "", priority: int = 1,
                   due_date: Optional[str] = None, start_date: Optional[str] = None,
                   project_number: Optional[str] = None) -> Optional[Task]:
        """添加新项目"""
        try:
            # 修复参数顺序：使用关键字参数确保正确映射
            task = Task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                start_date=start_date,
                project_number=project_number
            )
            
            self.projects.append(task)
            if self.save_data():
                return task
            return None
        except Exception as e:
            logger.error(f"添加项目失败: {e}")
            return None
    
    # 保留兼容性方法，但重定向到标准方法
    def add_task(self, title: str, description: str = "", priority: int = 1,
                 due_date: Optional[str] = None, start_date: Optional[str] = None,
                 project_number: Optional[str] = None) -> Task:
        """添加新任务（兼容旧版本）"""
        return self.add_project(title, description, priority, due_date, start_date, project_number)
    
    def get_all_projects(self) -> List[Task]:
        """获取所有项目"""
        return self.projects.copy()
    
    def get_project_by_number(self, project_number: str) -> Optional[Task]:
        """根据项目编号获取项目"""
        return next((p for p in self.projects if p.project_number == project_number), None)
    
    def delete_project(self, project_number: str) -> bool:
        """删除项目"""
        initial_count = len(self.projects)
        
        # 添加调试信息
        logger.info(f"尝试删除项目编号: {project_number}")
        logger.info(f"当前项目列表中的编号: {[p.project_number for p in self.projects]}")
        
        self.projects = [p for p in self.projects if p.project_number != project_number]
        
        if len(self.projects) < initial_count:
            logger.info(f"成功找到并删除项目，开始保存数据")
            return self.save_data()
        else:
            logger.warning(f"未找到项目编号为 {project_number} 的项目")
            return False
    
    def update_project(self, project_number: str, updates: Dict[str, Any]) -> bool:
        """更新项目信息"""
        project = self.get_project_by_number(project_number)
        if not project:
            return False
        
        # 应用更新
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        return self.save_data()
    
    def update_project_progress(self, project_number: str, progress: int) -> bool:
        """更新项目进度"""
        project = self.get_project_by_number(project_number)
        if not project:
            return False
        
        try:
            # 调用task对象的update_progress方法，这样会自动更新状态
            project.update_progress(progress)
            return self.save_data()
        except ValueError as e:
            logger.error(f"更新进度失败: {e}")
            return False
    
    # 为了完全兼容旧版本，添加这些别名方法
    load_tasks = load_data
    save_tasks = save_data
    get_all_tasks = get_all_projects