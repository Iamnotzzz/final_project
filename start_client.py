#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动客户端脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from client.gui import SecondHandSystemGUI
    print("校园二手交易平台 - 客户端启动")
    print("=" * 40)
    print("请确保服务器已启动")
    print("默认管理员账户: admin/admin123")
    print("=" * 40)
    
    app = SecondHandSystemGUI()
    app.run()