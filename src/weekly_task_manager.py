import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WeeklyTaskManager:
    """管理每周待办事项的数据操作（已优化）"""

    def __init__(self, data_file: str = "weekly_data.json"):
        # 统一使用绝对路径，避免相对路径导致文件加载不到
        self.data_file = os.path.abspath(data_file)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """加载数据，若文件不存在则返回默认结构。"""
        logger.info("加载每周数据：%s", self.data_file)
        if not os.path.exists(self.data_file):
            logger.info("每周数据文件不存在，使用默认结构")
            return {"tasks": [], "next_task_id": 1}
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info("成功加载每周数据，tasks=%d", len(data.get("tasks", [])))
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.exception("读取每周数据失败，使用默认结构：%s", e)
            return {"tasks": [], "next_task_id": 1}

    def _save_data(self):
        """保存数据到JSON文件。"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


    def get_tasks_by_week(self, week_str: str) -> List[Dict[str, Any]]:
        """使用列表推导式高效获取指定周的任务，并添加错误处理。"""
        # 添加类型检查确保self.data是字典且包含tasks键
        if not isinstance(self.data, dict) or 'tasks' not in self.data or not isinstance(self.data['tasks'], list):
            # 如果data格式不正确，返回空列表
            return []
        return [task for task in self.data['tasks'] if task.get('week') == week_str]

    def add_task(self, content: str, week_str: str) -> Dict[str, Any]:
        """添加新任务，使用自增ID。"""
        task_id = self.data['next_task_id']
        new_task = {
            "id": task_id,
            "content": content,
            "completed": False,
            "week": week_str
        }
        self.data['tasks'].append(new_task)
        self.data['next_task_id'] += 1
        self._save_data()
        return new_task

    def _find_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """使用生成器表达式查找任务。"""
        return next((task for task in self.data['tasks'] if task['id'] == task_id), None)

    def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新任务信息。"""
        task = self._find_task(task_id)
        if task:
            task.update(updates)
            self._save_data()
        return task

    def delete_task(self, task_id: int) -> bool:
        """使用列表推导式删除任务。"""
        original_count = len(self.data['tasks'])
        self.data['tasks'] = [task for task in self.data['tasks'] if task['id'] != task_id]
        if len(self.data['tasks']) < original_count:
            self._save_data()
            return True
        return False

    def get_next_week_str(self, week_str: Optional[str] = None) -> str:
        """给定 week_str（例如 '2025-W43'）返回下一周的 week_str；若未提供则基于当前周。"""
        if not week_str:
            y, w, _ = datetime.now().isocalendar()
            week_str = f"{y}-W{w:02d}"
        try:
            year, wk = week_str.split("-W")
            year_i = int(year); wk_i = int(wk)
            # Monday of the given ISO week
            d = datetime.fromisocalendar(year_i, wk_i, 1)
            next_d = d + timedelta(days=7)
            y2, w2, _ = next_d.isocalendar()
            return f"{y2}-W{w2:02d}"
        except Exception:
            # 发生解析异常时回退为当前周的下一周
            y, w, _ = datetime.now().isocalendar()
            d = datetime.fromisocalendar(y, w, 1) + timedelta(days=7)
            y2, w2, _ = d.isocalendar()
            return f"{y2}-W{w2:02d}"
    
    def rollover_incomplete_tasks(self, from_week: Optional[str] = None, to_week: Optional[str] = None) -> int:
        """
        将 from_week 中未完成的任务复制为新任务并放到 to_week。
        返回顺延的任务数量。
        """
        if from_week is None:
            from_week = self.get_current_week_str()
        if to_week is None:
            to_week = self.get_next_week_str(from_week)

        incomplete = [t for t in self.data.get("tasks", []) if t.get("week") == from_week and not t.get("completed")]
        if not incomplete:
            return 0

        rolled = 0
        for t in incomplete:
            new_id = self.data.get("next_task_id", 1)
            new_task = {
                "id": new_id,
                "content": t.get("content"),
                "completed": False,
                "week": to_week
            }
            self.data["tasks"].append(new_task)
            self.data["next_task_id"] = new_id + 1
            rolled += 1

        self._save_data()
        return rolled

    @staticmethod
    def get_current_week_str() -> str:
        """获取当前日期所在的周字符串，使用 ISO 周号，格式示例 '2025-W43'。"""
        y, w, _ = datetime.now().isocalendar()
        return f"{y}-W{w:02d}"