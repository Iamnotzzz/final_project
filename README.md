# 🎓 校园二手交易平台系统

一个功能完整、界面美观、支持并发的校园二手交易平台，基于Python开发，满足课程项目的所有基本需求和附加功能要求。

## ✨ 功能特性

### 📋 基本功能（必备）

#### 1. 用户界面
- ✅ 现代化GUI界面（使用ttkbootstrap）
- ✅ 响应式布局设计
- ✅ 美观的配色方案和图标
- ✅ 流畅的用户交互体验

#### 2. 数据库支持
- ✅ SQLite3数据库
- ✅ 完整的数据库设计（用户表、商品表、订单表）
- ✅ 外键约束和数据完整性
- ✅ 索引优化查询性能
- ✅ **并发控制**（使用锁机制和WAL模式）

#### 3. 网络模块
- ✅ Socket TCP通信
- ✅ JSON数据传输
- ✅ 多客户端并发支持
- ✅ 断线重连机制

#### 4. 用户登录与注销
- ✅ 用户注册（密码强度验证）
- ✅ 密码SHA256哈希存储
- ✅ 登录验证
- ✅ 安全退出

#### 5. 用户身份区分

**普通用户功能：**
- ✅ 浏览商品市场
- ✅ 发布闲置商品
- ✅ 购买商品（余额支付）
- ✅ 管理我的商品（下架）
- ✅ 查看我的订单
- ✅ 账户充值
- ✅ 商品搜索（关键词+类别）
- ✅ 个人余额管理

**管理员功能：**
- ✅ 用户管理（查看、删除用户）
- ✅ 商品管理（查看、下架商品）
- ✅ 订单管理（查看所有订单）
- ✅ 数据统计（用户数、商品数、交易额）
- ✅ 数据可视化看板
- ✅ 数据爬取工具

### 🎯 附加功能（差异化）

#### 1. 数据可视化 ⭐⭐⭐
- ✅ **商品类别分布饼图** - 直观展示各类商品占比
- ✅ **每日交易额柱状图** - 展示近7天交易趋势
- ✅ **综合统计面板** - 多维度数据展示
- ✅ 使用Matplotlib绘制专业图表

#### 2. 测试数据生成 ⭐⭐
- ✅ 一键生成虚拟测试数据
- ✅ 可配置用户、商品、订单数量
- ✅ 实时日志显示生成过程
- ✅ 便于功能测试和演示

#### 3. 数据库并发控制 ⭐⭐⭐
- ✅ **线程锁机制**（RLock递归锁）
- ✅ **WAL模式**（Write-Ahead Logging）提升并发性能
- ✅ **事务处理**（ACID特性保证）
- ✅ **乐观锁**（防止余额并发修改）
- ✅ 超时重试机制

#### 4. 数据分析
- ✅ 销售排行榜统计
- ✅ 热门商品类别分析
- ✅ 交易趋势预测（基础）
- ✅ 用户活跃度统计

#### 5. 其他优化
- ✅ 完善的错误处理
- ✅ 输入验证和安全检查
- ✅ 代码模块化设计
- ✅ 详细的注释文档
- ✅ 快捷充值金额按钮
- ✅ 商品状态颜色区分

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

## 📁 项目结构

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

## 💻 使用指南

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

## 🔒 安全特性

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

## 📊 性能优化

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

## 🛠️ 技术栈

- **语言**: Python 3.8+
- **GUI**: tkinter + ttkbootstrap
- **数据库**: SQLite3
- **网络**: Socket (TCP)
- **数据可视化**: Matplotlib
- **并发控制**: threading + RLock
- **数据格式**: JSON

## 📝 课程要求对照表

| 需求类别 | 具体要求 | 实现情况 | 代码位置 |
|---------|---------|---------|---------|
| **基本功能** | | | |
| 用户界面 | GUI界面 | ✅ 完成 | `client/gui.py` |
| 数据库支持 | 数据库设计与操作 | ✅ 完成 | `server/database.py` |
| 网络模块 | 远程登录访问 | ✅ 完成 | `client/network_client.py`, `server/server.py` |
| 用户登录注销 | 注册/登录/注销 | ✅ 完成 | 各模块 |
| 身份区分 | 普通用户/管理员 | ✅ 完成 | 基于role字段 |
| 个人信息维护 | 余额管理等 | ✅ 完成 | 充值、消费功能 |
| 数据检索 | 多维度查询 | ✅ 完成 | 搜索、筛选功能 |
| 数据统计 | 多条件统计 | ✅ 完成 | 管理员看板 |
| 数据维护 | 增删改查 | ✅ 完成 | CRUD完整实现 |
| **附加功能** | | | |
| 数据可视化 | 图表绘制 | ✅ 完成 | 饼图、柱状图 |
| 并发控制 | 数据库并发 | ✅ 完成 | 锁机制、WAL模式 |
| 测试数据生成 | 虚拟数据 | ✅ 完成 | `generate_mock_data_window()` |

## ❓ 常见问题

### Q1: 启动服务器后提示"地址已被使用"？
**A:** 端口8888被占用，可以：
1. 关闭占用该端口的程序
2. 修改`common/config.py`中的`SERVER_PORT`为其他端口

### Q2: 客户端无法连接服务器？
**A:** 检查以下几点：
1. 确认服务器已启动
2. 检查防火墙是否允许8888端口
3. 确认服务器地址正确（localhost:8888）

### Q3: 图表显示中文乱码？
**A:** 需要安装中文字体：
- Windows: 系统自带"黑体(SimHei)"
- macOS: 安装 Arial Unicode MS
- Linux: `sudo apt-get install fonts-noto-cjk`

### Q4: 如何重置数据库？
**A:** 删除项目根目录下的`campus_secondhand.db`文件，重启服务器会自动创建新数据库。

### Q5: 如何修改管理员密码？
**A:** 在`server/database.py`的`create_default_admin`方法中修改默认密码。

## 🤝 项目特色

1. **完整性**: 满足课程所有基本要求和多项附加功能
2. **美观性**: 现代化UI设计，用户体验良好
3. **健壮性**: 完善的错误处理和并发控制
4. **可扩展性**: 模块化设计，易于功能扩展
5. **文档完备**: 详细的代码注释和使用文档

## 📜 许可证

本项目仅供学习和教学使用，不得用于商业用途。

## 👨‍💻 开发说明

- 开发语言: Python 3.8+
- 开发工具: PyCharm / VS Code
- 代码规范: PEP 8
- 注释规范: Google Style

## 🎯 后续优化方向

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

**项目完成时间**: 2024年
**开发周期**: 完整功能开发
**代码规模**: 约2000+行

如有问题，欢迎提出！祝使用愉快！🎉