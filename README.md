# 校园二手交易平台系统

一个基于Python的校园二手交易平台，支持用户注册登录、商品发布、购买和管理等功能。

## 功能特性

### 基本功能
- 用户注册/登录/注销
- 两种用户角色：普通用户、管理员
- 商品发布、浏览、购买
- 订单管理
- 个人信息维护

### 管理员功能
- 用户管理
- 商品管理
- 数据统计

## 系统架构

- **客户端**: Tkinter GUI界面
- **服务端**: Socket网络通信
- **数据库**: SQLite
- **通信协议**: JSON

## 项目结构

```
campus_secondhand/
├── client/              # 客户端代码
│   ├── gui.py          # GUI界面
│   └── network_client.py # 网络通信
├── server/             # 服务端代码
│   ├── server.py       # 主服务器
│   └── database.py     # 数据库操作
├── common/             # 公共模块
│   ├── config.py       # 配置文件
│   └── utils.py        # 工具函数
├── main.py             # 主程序入口
├── start_server.py     # 启动服务器脚本
├── start_client.py     # 启动客户端脚本
└── README.md           # 项目说明
```

## 安装和运行

### 环境要求
- Python 3.6+
- tkinter (通常随Python安装)

### 运行步骤

1. **启动服务器**
   ```bash
   python start_server.py
   ```
   或者
   ```bash
   python main.py
   # 选择"是"启动服务器
   ```

2. **启动客户端**
   ```bash
   python start_client.py
   ```
   或者
   ```bash
   python main.py
   # 选择"否"启动客户端
   ```

### 默认账户
- 管理员账户: `admin` / `admin123`

## 使用说明

### 普通用户
1. 注册新账户或使用现有账户登录
2. 浏览商品列表
3. 发布自己的商品
4. 购买其他用户的商品
5. 查看我的商品和订单

### 管理员
1. 使用管理员账户登录
2. 管理所有用户
3. 管理所有商品
4. 查看系统统计数据

## 数据库设计

### 用户表 (users)
- user_id: 用户ID
- username: 用户名
- password: 密码（哈希存储）
- role: 用户角色（user/admin）
- contact: 联系方式
- created_at: 注册时间

### 商品表 (goods)
- goods_id: 商品ID
- name: 商品名称
- category: 商品类别
- price: 价格
- description: 商品描述
- seller_id: 卖家ID
- status: 商品状态（available/sold/removed）
- publish_time: 发布时间

### 订单表 (orders)
- order_id: 订单ID
- goods_id: 商品ID
- buyer_id: 买家ID
- seller_id: 卖家ID
- price: 价格
- status: 订单状态（pending/completed/cancelled）
- create_time: 创建时间

## 扩展功能建议

1. 数据爬取：爬取校内论坛二手商品信息
2. 数据可视化：商品类别分布、价格趋势图表
3. 数据分析：热门商品推荐、交易活跃时段分析
4. 搜索功能：商品关键词搜索
5. 聊天功能：买卖双方简单沟通

## 开发说明

### 网络通信
- 使用Socket进行客户端-服务端通信
- JSON格式传输数据
- 支持多客户端并发连接

### 安全考虑
- 密码使用SHA256哈希存储
- 基本的用户输入验证
- 防止SQL注入（使用参数化查询）

### 注意事项
1. 确保先启动服务器再启动客户端
2. 默认服务器地址为localhost:8888
3. 数据库文件会自动创建在项目根目录

## 常见问题

**Q: 无法连接到服务器？**
A: 请确保服务器已启动，并且防火墙允许8888端口访问。

**Q: 忘记管理员密码？**
A: 默认管理员账户为admin/admin123，可在database.py中修改。

**Q: 如何在不同电脑上运行？**
A: 修改common/config.py中的SERVER_HOST为服务器IP地址。

## 许可证

本项目仅供学习和教学使用。