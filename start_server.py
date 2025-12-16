#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动服务器脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from server.server import Server
    print("校园二手交易平台 - 服务器启动")
    print("=" * 40)
    print("服务器地址: localhost:8888")
    print("按 Ctrl+C 停止服务器")
    print("=" * 40)
    
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        server.stop()
        print("服务器已关闭")