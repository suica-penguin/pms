# 集中管理常用导入
try:
    import json
    import os
    from datetime import datetime
    from typing import List, Dict, Optional
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
    from tkcalendar import DateEntry
except ImportError as e:
    print(f"导入错误: {e}")