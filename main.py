#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
校园二手交易平台系统
主程序入口
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """启动服务器"""
    try:
        from server.server import Server
        server = Server()
        print("服务器启动中...")
        server.start()
    except Exception as e:
        print(f"启动服务器失败: {e}")

def start_client():
    """启动客户端"""
    try:
        from client.gui import SecondHandSystemGUI
        app = SecondHandSystemGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"启动客户端失败: {e}")

def main():
    """主程序"""
    root = tk.Tk()
    root.title("校园二手交易平台 - 启动器")
    root.geometry("300x200")
    
    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 隐藏主窗口
    root.withdraw()
    
    # 选择启动模式
    choice = messagebox.askyesno(
        "启动选择", 
        "是否启动服务器？\n\n"
        "是：启动服务器\n"
        "否：启动客户端"
    )
    
    root.destroy()
    
    if choice:
        # 启动服务器
        print("正在启动服务器...")
        print("服务器启动后，请在另一个窗口启动客户端")
        print("按 Ctrl+C 停止服务器")
        start_server()
    else:
        # 启动客户端
        print("正在启动客户端...")
        print("请确保服务器已启动")
        start_client()

if __name__ == "__main__":
    main()