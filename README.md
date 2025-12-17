# 校园二手交易平台系统

一个功能完整、界面美观、支持并发的校园二手交易平台，基于Python开发

## 功能特性

### 基本功能

#### 1. 用户界面
- **现代化UI设计**：基于 `ttkbootstrap` 框架开发，采用 "cosmo" 主题，界面简洁美观。
- **响应式布局**：窗口自动居中，支持自适应调整。
- **主要模块**：
  - **登录/注册页**：支持表单验证、密码强度检查。
  - **用户主页**：
    - **侧边栏**：实时显示账户余额，提供快捷充值入口。
    - **功能菜单**：发布商品、管理我的商品、查看订单记录。
    - **商品市场**：表格化展示商品信息，支持按列排序。
  - **管理员后台**：
    - **仪表盘**：集成数据可视化图表（Matplotlib绘制）。
    - **管理工具**：用户管理、商品下架、订单监控。
    - **测试工具**：内置数据生成器，可一键生成模拟数据。
- **交互体验**：
  - 关键操作（如购买、删除）具有二次确认弹窗。
  - 操作结果通过消息提示框（MessageBox）即时反馈。
  - 支持中文显示优化。

**界面布局与交互逻辑**

1. **普通用户端布局**
   采用经典的**左右分栏布局**，最大化信息展示效率：
   - **左侧功能区 (Sidebar)**：
     - **个人中心**：顶部醒目展示账户余额，提供快捷充值入口。
     - **导航菜单**：垂直排列的核心功能入口（发布、管理、订单。
   - **右侧主视窗 (Main Content)**：
     - **工具栏**：包含全局搜索和快捷操作按钮。
     - **数据表格**：使用 `Treeview` 组件展示商品市场，支持多列显示和滚动浏览。

2. **管理员后台布局**
   采用**仪表盘 (Dashboard)** 设计风格，强调数据监控：
   - **顶部通栏**：深色主题导航，显示管理员身份和系统状态。
   - **数据概览**：顶部横向排列三个关键指标卡片（用户/商品/订单总数），实时监控系统规模。
   - **功能矩阵**：下方采用网格布局 (Grid) 排列管理入口。

3. **核心交互逻辑**
   - **数据驱动**：所有列表操作（如购买、下架）完成后，自动触发数据刷新，确保界面显示最新状态。
   - **安全防护**：
     - **二次确认**：关键操作（购买、删除、下架）均需通过模态对话框确认。
     - **权限校验**：前端实时校验操作合法性（如禁止购买自己发布的商品、禁止删除管理员账户）。
   - **即时反馈**：所有网络请求均有加载状态或结果提示（Toast/MessageBox），操作闭环完整。

#### 2. 数据库支持
- 使用了SQLite3数据库
- 完整的数据库设计（用户表、商品表、订单表）
- 外键约束和数据完整性
- 索引优化查询性能
- **并发控制**（使用锁机制和WAL模式）

#### 3. 网络模块
- Socket TCP通信
- JSON数据传输
- 多客户端并发支持
- 断线重连机制

#### 4. 用户登录与注销
- 用户注册（密码强度验证）
- 密码SHA256哈希存储
- 登录验证
- 安全退出

#### 5. 用户身份区分

**普通用户功能：**
- 浏览商品市场
- 发布闲置商品
- 购买商品（余额支付）
- 管理我的商品（下架）
- 查看我的订单
- 账户充值
- 商品搜索（关键词+类别）
- 个人余额管理

**管理员功能：**
- 用户管理（查看、删除用户）
- 商品管理（查看、下架商品）
- 订单管理（查看所有订单）
- 数据统计（用户数、商品数、交易额）
- 数据可视化看板
- 虚拟数据生成



## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│              客户端 (Client)                     │
│  ┌──────────────┐         ┌──────────────┐      │
│  │  GUI界面     │ ◄─────► │ NetworkClient│      │
│  │ (ttkbootstrap)│         │  (Socket)    │      │
│  └──────────────┘         └──────────────┘      │
└──────────────────┬─────────────────────────────┘
                   │ TCP/JSON
┌──────────────────▼─────────────────────────────┐
│              服务端 (Server)                     │
│  ┌──────────────┐         ┌──────────────┐      │
│  │ Socket Server│ ◄─────► │  Database    │      │
│  │ (多线程)      │         │  (SQLite3)   │      │
│  └──────────────┘         └──────────────┘      │
└─────────────────────────────────────────────────┘
```

##  项目结构

```
campus_secondhand/
├── client/                     # 客户端模块
│   ├── gui.py                 # GUI界面（800行优化代码）
│   └── network_client.py      # 网络客户端
├── server/                    # 服务端模块
│   ├── server.py             # Socket服务器
│   └── database.py           # 数据库操作（支持并发）
├── common/                    # 公共模块
│   ├── config.py             # 配置文件
│   └── utils.py              # 工具函数
├── main.py                   # 主程序入口
├── start_server.py           # 服务器启动脚本
├── start_client.py           # 客户端启动脚本
├── requirements.txt          # 依赖包列表
├── README.md                 # 项目文档（本文件）
└── campus_secondhand.db      # 数据库文件（自动生成）
```

##  配置文件说明

项目的主要配置位于 `common/config.py`，您可以根据需要修改：

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| `SERVER_HOST` | `'localhost'` | 服务器监听地址，局域网联机可改为 `0.0.0.0` |
| `SERVER_PORT` | `8888` | 服务器监听端口，如冲突可修改 |
| `BUFFER_SIZE` | `1048576` | 网络传输缓冲区大小 (1MB) |
| `DATABASE_NAME` | `'campus_secondhand.db'` | SQLite数据库文件名 |

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows / macOS / Linux

### 安装步骤

1. **克隆项目**
```bash
cd campus_secondhand
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

或使用国内镜像加速：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. **启动服务器**
```bash
python start_server.py
```

看到以下输出表示启动成功：
```
校园二手交易平台 - 服务器启动
========================================
服务器地址: localhost:8888
按 Ctrl+C 停止服务器
========================================
服务器启动成功，监听 localhost:8888
默认管理员账户创建成功
```

4. **启动客户端**（新开一个终端窗口）
```bash
python start_client.py
```

5. **开始使用**
- 首次使用：注册新账户
- 管理员登录：`admin` / `admin123`

##  使用指南

### 普通用户操作流程

1. **注册账户**
   - 点击"注册新账号"
   - 填写用户名、密码（至少6位）、联系方式
   - 注册成功后返回登录

2. **充值余额**
   - 登录后点击左侧"充值"按钮
   - 输入金额或使用快捷金额
   - 确认充值

3. **浏览商品**
   - 主界面显示所有在售商品
   - 可使用搜索功能按关键词或类别筛选

4. **发布商品**
   - 点击"发布商品"
   - 填写商品信息（名称、类别、价格、描述）
   - 确认发布

5. **购买商品**
   - 选中心仪商品
   - 点击"购买选中"
   - 确认后自动扣款并生成订单

6. **管理商品和订单**
   - "我的商品"：查看和管理已发布商品
   - "我的订单"：查看购买和出售记录

### 管理员操作指南

1. **登录管理后台**
   - 使用管理员账户登录（admin/admin123）
   - 进入管理仪表盘

2. **用户管理**
   - 查看所有注册用户
   - 删除违规用户（不可删除管理员）

3. **商品管理**
   - 查看所有商品
   - 下架违规或过期商品

4. **订单管理**
   - 查看所有交易订单
   - 统计交易总额

5. **数据看板**
   - 查看商品类别分布图
   - 分析交易额趋势
   - 浏览系统综合统计

6. **数据看板**
   - 查看商品类别分布图
   - 分析交易额趋势
   - 浏览系统综合统计

7. **生成测试数据**
   - 设置生成数量（用户/商品/订单）
   - 一键生成虚拟数据
   - 实时查看生成日志
   - 便于功能测试和演示

## 🗄️ 数据库设计

### 用户表 (users)
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 用户ID
    username TEXT UNIQUE NOT NULL,              -- 用户名
    password TEXT NOT NULL,                     -- 密码（SHA256）
    role TEXT NOT NULL DEFAULT 'user',          -- 角色（user/admin）
    contact TEXT,                               -- 联系方式
    balance REAL DEFAULT 0.0,                   -- 账户余额
    created_at TEXT NOT NULL                    -- 注册时间
);
```

### 商品表 (goods)
```sql
CREATE TABLE goods (
    goods_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 商品ID
    name TEXT NOT NULL,                          -- 商品名称
    category TEXT NOT NULL,                      -- 商品类别
    price REAL NOT NULL CHECK(price > 0),        -- 价格
    description TEXT,                            -- 描述
    seller_id INTEGER NOT NULL,                  -- 卖家ID
    status TEXT NOT NULL DEFAULT 'available',    -- 状态
    publish_time TEXT NOT NULL,                  -- 发布时间
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
);
```

### 订单表 (orders)
```sql
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,                   -- 订单号
    goods_id INTEGER NOT NULL,                   -- 商品ID
    buyer_id INTEGER NOT NULL,                   -- 买家ID
    seller_id INTEGER NOT NULL,                  -- 卖家ID
    price REAL NOT NULL,                         -- 价格
    status TEXT NOT NULL DEFAULT 'pending',      -- 状态
    create_time TEXT NOT NULL,                   -- 创建时间
    FOREIGN KEY (goods_id) REFERENCES goods(goods_id),
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
);
```

### 索引优化
```sql
CREATE INDEX idx_goods_status ON goods(status);
CREATE INDEX idx_goods_seller ON goods(seller_id);
CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_seller ON orders(seller_id);
CREATE INDEX idx_orders_time ON orders(create_time);
```

##  安全特性

1. **密码安全**
   - SHA256哈希存储
   - 不明文保存密码

2. **SQL注入防护**
   - 使用参数化查询
   - 严格的输入验证

3. **并发控制**
   - 线程锁保护关键操作
   - 事务保证数据一致性

4. **权限控制**
   - 角色区分（普通用户/管理员）
   - 操作权限验证

## 性能优化

1. **数据库优化**
   - 索引加速查询
   - WAL模式提升并发
   - 连接池管理

2. **网络优化**
   - JSON数据压缩
   - 批量操作减少请求

3. **界面优化**
   - 异步加载数据
   - 懒加载图表
   - 缓存常用数据

## ❓ 常见问题

### Q1: 启动服务器后提示"地址已被使用"？
**A:** 端口8888被占用，可以：
1. 关闭占用该端口的程序
2. 修改`common/config.py`中的`SERVER_PORT`为其他端口

### Q2: 客户端无法连接服务器？
**A:** 检查以下几点：
1. 确认服务器已启动
2. 检查防火墙是否允许8888端口
3. 确认服务器地址正确（默认localhost）

### Q3: 图表显示中文乱码？
**A:** 系统会自动尝试加载常见中文字体（如微软雅黑、黑体、Arial Unicode MS）。如果仍乱码，请安装相应字体或在代码中修改字体配置。

### Q4: 如何重置数据库？
**A:** 删除项目根目录下的`campus_secondhand.db`文件，重启服务器会自动创建新数据库。

##  技术栈

- **语言**: Python 3.8+
- **GUI**: tkinter + ttkbootstrap
- **数据库**: SQLite3
- **网络**: Socket (TCP)
- **数据可视化**: Matplotlib
- **并发控制**: threading + RLock
- **数据格式**: JSON


## 后续优化方向

1. **功能扩展**
   - 实时聊天功能
   - 商品图片上传
   - 评价系统
   - 收藏功能
   - 真实数据爬虫接入

2. **性能优化**
   - Redis缓存
   - 消息队列
   - 负载均衡

3. **部署优化**
   - Docker容器化
   - 云服务器部署
   - HTTPS加密

---

