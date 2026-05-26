from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import ttk
import platform
import sys

# 检测操作系统
IS_WINDOWS = platform.system() == 'Windows'
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'

# 配置常量 - Apple风格配色
COLOR_SCHEME = {
    'PRIMARY': '#007aff',      # Apple系统蓝色
    'SECONDARY': '#5ac8fa',    # Apple次要蓝色
    'SUCCESS': '#34c759',      # Apple成功绿色
    'WARNING': '#ffcc00',      # Apple警告黄色
    'DANGER': '#ff3b30',       # Apple危险红色
    'LIGHT_BG': '#f2f2f7',     # Apple浅灰背景色
    'DARK_BG': '#e5e5ea',      # Apple深灰背景色
    'DARK_TEXT': '#000000',    # Apple深色文字
    'MEDIUM_TEXT': '#8e8e93',  # Apple中等灰色文字
    'BORDER': '#d1d1d6',       # Apple边框颜色
    'HIGHLIGHT': '#007aff'     # 高亮颜色
}

# Apple风格字体配置
FONT_CONFIG = {
    # 在macOS上使用San Francisco字体，其他系统使用相似的无衬线字体
    'BASE': ('-apple-system', 13) if IS_MACOS else 
            ('Microsoft YaHei UI', 10) if IS_WINDOWS else ('Roboto', 10),
    'BOLD': ('-apple-system', 13, 'bold') if IS_MACOS else 
            ('Microsoft YaHei UI', 10, 'bold') if IS_WINDOWS else ('Roboto', 10, 'bold'),
    'TITLE': ('-apple-system', 17, 'bold') if IS_MACOS else 
             ('Microsoft YaHei UI', 12, 'bold') if IS_WINDOWS else ('Roboto', 12, 'bold'),
    'LARGE': ('-apple-system', 15) if IS_MACOS else 
             ('Microsoft YaHei UI', 11) if IS_WINDOWS else ('Roboto', 11),
    'SMALL': ('-apple-system', 11) if IS_MACOS else 
             ('Microsoft YaHei UI', 9) if IS_WINDOWS else ('Roboto', 9),
    'MONOSPACE': ('SF Mono', 12) if IS_MACOS else 
                 ('Consolas', 10) if IS_WINDOWS else ('Roboto Mono', 10)  # 等宽字体
}

def setup_styles() -> ttk.Style:
    """
    设置应用程序的全局样式配置 - Apple风格
    
    Returns:
        ttk.Style: 配置好的样式对象
    """
    style = ttk.Style()
    
    # 应用适合的基础主题
    if IS_MACOS:
        # macOS上使用aqua主题（Apple原生主题）
        style.theme_use('aqua')
    else:
        # Windows和Linux系统使用clam主题作为基础，避免vista主题的兼容性问题
        style.theme_use('clam')

    # 基础样式配置 - Apple风格
    style.configure('.', 
                   background=COLOR_SCHEME['LIGHT_BG'],
                   foreground=COLOR_SCHEME['DARK_TEXT'],
                   font=FONT_CONFIG['BASE'])

    # 配置按钮样式 - Apple扁平化圆角风格
    style.configure('TButton', 
                   borderwidth=0,
                   padding=8,
                   font=FONT_CONFIG['BASE'],
                   foreground=COLOR_SCHEME['DARK_TEXT'],  # 显式设置文本颜色
                   relief='flat',
                   focuscolor='none',  # 隐藏焦点环颜色
                   focusthickness=0)   # 设置焦点环厚度为0

    # 配置特殊按钮样式 - Apple系统颜色
    for style_name, color in [('Primary', 'PRIMARY'), ('Success', 'SUCCESS'),
                              ('Warning', 'WARNING'), ('Danger', 'DANGER')]:
        style.configure(f'{style_name}.TButton',
                        background=COLOR_SCHEME[color],
                        foreground='white',  # 确保在彩色背景上文本为白色
                        font=FONT_CONFIG['BOLD'],
                        focuscolor='none',   # 隐藏焦点环颜色
                        focusthickness=0)    # 设置焦点环厚度为0

    # 配置导航按钮样式 - Apple导航栏风格
    style.configure('Nav.TButton', 
                   font=FONT_CONFIG['BASE'], 
                   borderwidth=0, 
                   relief='flat',
                   padding=(15, 8),
                   background='white',
                   foreground=COLOR_SCHEME['DARK_TEXT'],  # 显式设置文本颜色
                   focuscolor='none',   # 隐藏焦点环颜色
                   focusthickness=0)    # 设置焦点环厚度为0

    style.configure('Nav.Selected.TButton',
                    font=FONT_CONFIG['BOLD'],
                    borderwidth=0,
                    relief='flat',
                    padding=(15, 8),
                    background=COLOR_SCHEME['PRIMARY'],
                    foreground='white',  # 确保在彩色背景上文本为白色
                    focuscolor='none',   # 隐藏焦点环颜色
                    focusthickness=0)    # 设置焦点环厚度为0

    # Apple风格的按钮交互效果 - 强调悬停和点击状态
    if IS_WINDOWS:
        # Windows系统使用不透明颜色，避免渲染问题
        style.map('TButton',
                  background=[('active', '#d1ebff'),  # 不透明的浅蓝色
                              ('pressed', COLOR_SCHEME['SECONDARY']),
                              ('disabled', COLOR_SCHEME['DARK_BG'])],
                  foreground=[('active', COLOR_SCHEME['DARK_TEXT']), 
                              ('pressed', 'white'),
                              ('disabled', COLOR_SCHEME['MEDIUM_TEXT'])],
                  relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
    else:
        # 其他系统可以继续使用带透明度的颜色
        style.map('TButton',
                  background=[('active', COLOR_SCHEME['SECONDARY'] + '80'),
                              ('pressed', COLOR_SCHEME['SECONDARY']),
                              ('disabled', COLOR_SCHEME['DARK_BG'])],
                  foreground=[('active', COLOR_SCHEME['DARK_TEXT']), 
                              ('pressed', 'white'),
                              ('disabled', COLOR_SCHEME['MEDIUM_TEXT'])],
                  relief=[('pressed', 'sunken'), ('!pressed', 'flat')])

    # 配置其他按钮样式 - Apple系统颜色
    for style_name, color in [('Primary', 'PRIMARY'), ('Success', 'SUCCESS'),
                              ('Warning', 'WARNING'), ('Danger', 'DANGER')]:
        style.configure(f'{style_name}.TButton',
                        background=COLOR_SCHEME[color],
                        foreground='white',  # 确保在彩色背景上文本为白色
                        font=FONT_CONFIG['BOLD'])

        # 为特殊按钮也添加系统特定的悬停效果
        if IS_WINDOWS:
            # Windows系统使用不透明的悬停颜色
            hover_color = {'PRIMARY': '#3399ff', 'SUCCESS': '#4cd964', 
                          'WARNING': '#ffd60a', 'DANGER': '#ff6b6b'}[color]
            style.map(f'{style_name}.TButton',
                      background=[('active', hover_color),
                                  ('pressed', COLOR_SCHEME[color]),
                                  ('disabled', COLOR_SCHEME['DARK_BG'])],
                      foreground=[('active', 'white'),
                                  ('pressed', 'white'),
                                  ('disabled', COLOR_SCHEME['MEDIUM_TEXT'])])

    # 配置标签样式 - Apple字体风格
    style.configure('TLabel', 
                   font=FONT_CONFIG['BASE'], 
                   foreground=COLOR_SCHEME['DARK_TEXT'])
    style.configure('Title.TLabel', 
                   font=FONT_CONFIG['TITLE'], 
                   foreground=COLOR_SCHEME['DARK_TEXT'])
    style.configure('Large.TLabel', 
                   font=FONT_CONFIG['LARGE'], 
                   foreground=COLOR_SCHEME['DARK_TEXT'])
    style.configure('Small.TLabel', 
                   font=FONT_CONFIG['SMALL'], 
                   foreground=COLOR_SCHEME['MEDIUM_TEXT'])
    style.configure('Mono.TLabel',
                   font=FONT_CONFIG['MONOSPACE'],
                   foreground=COLOR_SCHEME['DARK_TEXT'])

    # 配置其他组件样式 - Apple风格
    style.configure('TCombobox', 
                   padding=5, 
                   font=FONT_CONFIG['BASE'],
                   fieldbackground='white',
                   relief='flat')
    
    # Apple风格树形视图 - 简约、清晰
    style.configure('Treeview', 
                   font=FONT_CONFIG['BASE'], 
                   rowheight=32,  # Apple标准行高
                   fieldbackground='white', 
                   background='white',
                   relief='flat')
    
    style.configure('Treeview.Heading', 
                   font=('-apple-system', 14, 'bold') if IS_MACOS else 
                        ('Microsoft YaHei UI', 11, 'bold') if IS_WINDOWS else ('Roboto', 11, 'bold'),
                   background=COLOR_SCHEME['DARK_BG'], 
                   foreground=COLOR_SCHEME['DARK_TEXT'],
                   relief='flat')
    
    # 添加树形视图行选择效果 - 增强选中状态可见性
    style.map('Treeview',
              background=[('selected', COLOR_SCHEME['PRIMARY'] + 'C0')],  # 降低透明度以增强可见性
              foreground=[('selected', 'white')])  # 将选中时文本改为白色，增加对比度

    # 对于Windows系统，特别优化选中状态显示
    if IS_WINDOWS:
        style.map('Treeview',
                  background=[('selected', '#0078d7')],  # Windows蓝色主题，不使用透明度
                  foreground=[('selected', 'white')],
                  bordercolor=[('selected', '#0078d7')])  # 增加边框颜色

    style.configure('TEntry', 
                   font=FONT_CONFIG['BASE'], 
                   padding=5,
                   fieldbackground='white',
                   relief='flat')
    
    style.configure('TFrame', 
                   background=COLOR_SCHEME['LIGHT_BG'])
    
    # Apple风格滚动条 - 简约设计
    style.configure('Vertical.TScrollbar', 
                   background=COLOR_SCHEME['DARK_BG'],
                   troughcolor=COLOR_SCHEME['DARK_BG'],
                   borderwidth=0)
    
    style.configure('Horizontal.TScrollbar', 
                   background=COLOR_SCHEME['DARK_BG'],
                   troughcolor=COLOR_SCHEME['DARK_BG'],
                   borderwidth=0)
    
    # 配置进度条样式 - Apple风格
    style.configure('Horizontal.TProgressbar',
                   background=COLOR_SCHEME['PRIMARY'],
                   troughcolor=COLOR_SCHEME['DARK_BG'],
                   borderwidth=0)

    return style