import sqlite3
import os
from common.config import DATABASE_NAME, USER_ROLE, ADMIN_ROLE
from common.utils import hash_password, get_current_time

class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), DATABASE_NAME)
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                contact TEXT,
                balance REAL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 创建商品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goods (
                goods_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                seller_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'available',
                publish_time TEXT NOT NULL,
                FOREIGN KEY (seller_id) REFERENCES users (user_id)
            )
        ''')
        
        # 创建订单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                goods_id INTEGER NOT NULL,
                buyer_id INTEGER NOT NULL,
                seller_id INTEGER NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                create_time TEXT NOT NULL,
                FOREIGN KEY (goods_id) REFERENCES goods (goods_id),
                FOREIGN KEY (buyer_id) REFERENCES users (user_id),
                FOREIGN KEY (seller_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        
        # 检查是否需要创建默认管理员账户
        cursor.execute('SELECT * FROM users WHERE role = ?', (ADMIN_ROLE,))
        if not cursor.fetchone():
            self.create_default_admin()
        
        conn.close()
    
    def create_default_admin(self):
        """创建默认管理员账户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        admin_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO users (username, password, role, contact, balance, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', admin_password, ADMIN_ROLE, 'admin@campus.com', 1000.0, get_current_time()))
        
        conn.commit()
        conn.close()
    
    # 用户相关方法
    def register_user(self, username, password, contact=None):
        """用户注册"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password, role, contact, balance, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, USER_ROLE, contact, 0.0, get_current_time()))
            
            conn.commit()
            return {'success': True, 'message': '注册成功'}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': '用户名已存在'}
        finally:
            conn.close()
    
    def login_user(self, username, password):
        """用户登录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(password)
        cursor.execute('''
            SELECT user_id, username, role, contact, balance FROM users
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def get_all_users(self):
        """获取所有用户（管理员用）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, username, role, contact, balance, created_at FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return users
    
    # 商品相关方法
    def add_goods(self, name, category, price, description, seller_id):
        """添加商品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO goods (name, category, price, description, seller_id, publish_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, category, price, description, seller_id, get_current_time()))
        
        conn.commit()
        goods_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'goods_id': goods_id}
    
    def get_all_goods(self):
        """获取所有商品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT g.*, u.username as seller_name
            FROM goods g
            JOIN users u ON g.seller_id = u.user_id
            WHERE g.status = 'available'
            ORDER BY g.publish_time DESC
        ''')
        
        goods = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return goods
    
    def get_user_goods(self, user_id):
        """获取用户发布的商品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM goods
            WHERE seller_id = ?
            ORDER BY publish_time DESC
        ''', (user_id,))
        
        goods = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return goods
    
    def update_goods_status(self, goods_id, status):
        """更新商品状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE goods SET status = ?
            WHERE goods_id = ?
        ''', (status, goods_id))
        
        conn.commit()
        conn.close()
    
    # 订单相关方法
    def create_order(self, goods_id, buyer_id, seller_id, price):
        """创建订单"""
        from common.utils import generate_order_id
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        order_id = generate_order_id()
        cursor.execute('''
            INSERT INTO orders (order_id, goods_id, buyer_id, seller_id, price, create_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (order_id, goods_id, buyer_id, seller_id, price, get_current_time()))
        
        # 更新商品状态为已售
        self.update_goods_status(goods_id, 'sold')
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'order_id': order_id}
    
    def get_user_orders(self, user_id):
        """获取用户订单"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, g.name as goods_name, u1.username as buyer_name, u2.username as seller_name
            FROM orders o
            JOIN goods g ON o.goods_id = g.goods_id
            JOIN users u1 ON o.buyer_id = u1.user_id
            JOIN users u2 ON o.seller_id = u2.user_id
            WHERE o.buyer_id = ? OR o.seller_id = ?
            ORDER BY o.create_time DESC
        ''', (user_id, user_id))
        
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders
    
    # 余额相关方法
    def get_user_balance(self, user_id):
        """获取用户余额"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result['balance']
        return 0.0
    
    def recharge_balance(self, user_id, amount):
        """用户充值"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            amount = float(amount)
            if amount <= 0:
                return {'success': False, 'message': '充值金额必须大于0'}
            
            cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE user_id = ?
            ''', (amount, user_id))
            
            conn.commit()
            
            # 获取更新后的余额（在同一连接中查询）
            cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            new_balance = result['balance'] if result else 0.0
            
            return {'success': True, 'message': f'充值成功！当前余额：¥{new_balance:.2f}', 'balance': new_balance}
        except ValueError:
            return {'success': False, 'message': '充值金额必须是数字'}
        finally:
            conn.close()
    
    def purchase_goods(self, goods_id, buyer_id, seller_id, price):
        """购买商品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查商品状态
            cursor.execute('SELECT status FROM goods WHERE goods_id = ?', (goods_id,))
            goods = cursor.fetchone()
            if not goods:
                return {'success': False, 'message': '商品不存在'}
            
            if goods['status'] != 'available':
                return {'success': False, 'message': '商品已售出或已下架'}
            
            # 检查买家余额（在同一连接中查询）
            cursor.execute('SELECT balance FROM users WHERE user_id = ?', (buyer_id,))
            buyer_result = cursor.fetchone()
            if not buyer_result:
                return {'success': False, 'message': '买家不存在'}
            
            buyer_balance = buyer_result['balance']
            if buyer_balance < price:
                return {'success': False, 'message': '余额不足，请先充值'}
            
            # 扣除买家余额
            cursor.execute('''
                UPDATE users SET balance = balance - ? WHERE user_id = ?
            ''', (price, buyer_id))
            
            # 增加卖家余额
            cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE user_id = ?
            ''', (price, seller_id))
            
            # 创建订单
            from common.utils import generate_order_id
            order_id = generate_order_id()
            cursor.execute('''
                INSERT INTO orders (order_id, goods_id, buyer_id, seller_id, price, create_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_id, goods_id, buyer_id, seller_id, price, get_current_time()))
            
            # 更新商品状态为已售（在同一连接中执行）
            cursor.execute('''
                UPDATE goods SET status = ? WHERE goods_id = ?
            ''', ('sold', goods_id))
            
            conn.commit()
            
            # 获取更新后的余额（在同一连接中查询）
            cursor.execute('SELECT balance FROM users WHERE user_id = ?', (buyer_id,))
            new_balance_result = cursor.fetchone()
            new_buyer_balance = new_balance_result['balance'] if new_balance_result else 0.0
            
            return {
                'success': True, 
                'message': '购买成功！',
                'order_id': order_id,
                'new_balance': new_buyer_balance
            }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'购买失败：{str(e)}'}
        finally:
            conn.close()
    
    # 管理员功能
    def remove_goods(self, goods_id):
        """下架商品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查商品是否存在
            cursor.execute('SELECT goods_id FROM goods WHERE goods_id = ?', (goods_id,))
            if not cursor.fetchone():
                return {'success': False, 'message': '商品不存在'}
            
            # 更新商品状态为已下架
            cursor.execute('''
                UPDATE goods SET status = ? WHERE goods_id = ?
            ''', ('removed', goods_id))
            
            conn.commit()
            return {'success': True, 'message': '商品已下架'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'下架失败：{str(e)}'}
        finally:
            conn.close()
    
    def delete_user(self, user_id):
        """删除用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查用户是否存在
            cursor.execute('SELECT username, role FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            # 不能删除管理员
            if user['role'] == 'admin':
                return {'success': False, 'message': '不能删除管理员账户'}
            
            # 删除用户的相关商品
            cursor.execute('UPDATE goods SET status = ? WHERE seller_id = ?', ('removed', user_id))
            
            # 删除用户的订单记录
            cursor.execute('DELETE FROM orders WHERE buyer_id = ? OR seller_id = ?', (user_id, user_id))
            
            # 删除用户
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            
            conn.commit()
            return {'success': True, 'message': f'用户 {user["username"]} 已删除'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'message': f'删除用户失败：{str(e)}'}
        finally:
            conn.close()
    
    def get_all_orders(self):
        """获取所有订单（管理员用）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, g.name as goods_name, u1.username as buyer_name, u2.username as seller_name
            FROM orders o
            JOIN goods g ON o.goods_id = g.goods_id
            JOIN users u1 ON o.buyer_id = u1.user_id
            JOIN users u2 ON o.seller_id = u2.user_id
            ORDER BY o.create_time DESC
        ''')
        
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders