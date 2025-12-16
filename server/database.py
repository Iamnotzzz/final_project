import sqlite3
import os
import threading
from common.config import DATABASE_NAME, USER_ROLE, ADMIN_ROLE
from common.utils import hash_password, get_current_time

class Database:
    """数据库管理类 - 支持并发控制和事务处理"""
    
    _lock = threading.RLock()  # 使用递归锁支持并发控制
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), DATABASE_NAME)
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接 - 开启WAL模式提升并发性能"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        # 开启WAL模式，提升并发性能
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=5000')
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
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
                        price REAL NOT NULL CHECK(price > 0),
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
                
                # 创建索引提升查询性能
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_goods_status ON goods(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_goods_seller ON goods(seller_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_seller ON orders(seller_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_time ON orders(create_time)')
                
                conn.commit()
                
                # 检查是否需要创建默认管理员
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = ?', (ADMIN_ROLE,))
                if cursor.fetchone()['count'] == 0:
                    self.create_default_admin(conn, cursor)
                    
            except Exception as e:
                conn.rollback()
                print(f"初始化数据库失败: {e}")
                raise
            finally:
                conn.close()
    
    def create_default_admin(self, conn=None, cursor=None):
        """创建默认管理员账户"""
        close_conn = False
        if conn is None:
            conn = self.get_connection()
            cursor = conn.cursor()
            close_conn = True
        
        try:
            admin_password = hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password, role, contact, balance, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', admin_password, ADMIN_ROLE, 'admin@campus.com', 10000.0, get_current_time()))
            conn.commit()
            print("默认管理员账户创建成功")
        except sqlite3.IntegrityError:
            print("管理员账户已存在")
        finally:
            if close_conn:
                conn.close()
    
    # =================== 用户相关操作 ===================
    
    def register_user(self, username, password, contact=None):
        """用户注册 - 加锁保证并发安全"""
        with self._lock:
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
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': f'注册失败: {str(e)}'}
            finally:
                conn.close()
    
    def login_user(self, username, password):
        """用户登录验证"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = hash_password(password)
            cursor.execute('''
                SELECT user_id, username, role, contact, balance FROM users
                WHERE username = ? AND password = ?
            ''', (username, hashed_password))
            
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def get_all_users(self):
        """获取所有用户列表（管理员功能）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT user_id, username, role, contact, balance, created_at 
                FROM users 
                ORDER BY created_at DESC
            ''')
            users = [dict(row) for row in cursor.fetchall()]
            return users
        finally:
            conn.close()
    
    def delete_user(self, user_id):
        """删除用户（管理员功能） - 事务处理"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # 检查用户是否存在且不是管理员
                cursor.execute('SELECT username, role FROM users WHERE user_id = ?', (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    return {'success': False, 'message': '用户不存在'}
                
                if user['role'] == ADMIN_ROLE:
                    return {'success': False, 'message': '不能删除管理员账户'}
                
                # 开始事务
                cursor.execute('BEGIN TRANSACTION')
                
                # 下架用户的所有商品
                cursor.execute('''
                    UPDATE goods SET status = ? WHERE seller_id = ?
                ''', ('removed', user_id))
                
                # 取消相关订单
                cursor.execute('''
                    UPDATE orders SET status = ? 
                    WHERE buyer_id = ? OR seller_id = ?
                ''', ('cancelled', user_id, user_id))
                
                # 删除用户
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                
                conn.commit()
                return {'success': True, 'message': f'用户 {user["username"]} 已删除'}
                
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': f'删除用户失败：{str(e)}'}
            finally:
                conn.close()
    
    # =================== 商品相关操作 ===================
    
    def add_goods(self, name, category, price, description, seller_id):
        """添加商品"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO goods (name, category, price, description, seller_id, publish_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, category, price, description, seller_id, get_current_time()))
                
                conn.commit()
                goods_id = cursor.lastrowid
                return {'success': True, 'goods_id': goods_id, 'message': '商品发布成功'}
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': f'发布失败: {str(e)}'}
            finally:
                conn.close()
    
    def get_all_goods(self):
        """获取所有在售商品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT g.*, u.username as seller_name
                FROM goods g
                JOIN users u ON g.seller_id = u.user_id
                WHERE g.status = 'available'
                ORDER BY g.publish_time DESC
            ''')
            
            goods = [dict(row) for row in cursor.fetchall()]
            return goods
        finally:
            conn.close()
    
    def get_user_goods(self, user_id):
        """获取用户发布的所有商品"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM goods
                WHERE seller_id = ?
                ORDER BY publish_time DESC
            ''', (user_id,))
            
            goods = [dict(row) for row in cursor.fetchall()]
            return goods
        finally:
            conn.close()
    
    def update_goods_status(self, goods_id, status):
        """更新商品状态"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE goods SET status = ?
                    WHERE goods_id = ?
                ''', (status, goods_id))
                
                conn.commit()
                return {'success': True}
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': str(e)}
            finally:
                conn.close()
    
    def remove_goods(self, goods_id):
        """下架商品"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('SELECT goods_id, status FROM goods WHERE goods_id = ?', (goods_id,))
                goods = cursor.fetchone()
                
                if not goods:
                    return {'success': False, 'message': '商品不存在'}
                
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
    
    # =================== 订单相关操作 ===================
    
    def create_order(self, goods_id, buyer_id, seller_id, price):
        """创建订单"""
        from common.utils import generate_order_id
        
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                order_id = generate_order_id()
                cursor.execute('''
                    INSERT INTO orders (order_id, goods_id, buyer_id, seller_id, price, create_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (order_id, goods_id, buyer_id, seller_id, price, get_current_time()))
                
                # 更新商品状态
                cursor.execute('UPDATE goods SET status = ? WHERE goods_id = ?', ('sold', goods_id))
                
                conn.commit()
                return {'success': True, 'order_id': order_id}
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': f'创建订单失败: {str(e)}'}
            finally:
                conn.close()
    
    def get_user_orders(self, user_id):
        """获取用户相关订单"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
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
            return orders
        finally:
            conn.close()
    
    def get_all_orders(self):
        """获取所有订单（管理员功能）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT o.*, g.name as goods_name, u1.username as buyer_name, u2.username as seller_name
                FROM orders o
                JOIN goods g ON o.goods_id = g.goods_id
                JOIN users u1 ON o.buyer_id = u1.user_id
                JOIN users u2 ON o.seller_id = u2.user_id
                ORDER BY o.create_time DESC
            ''')
            
            orders = [dict(row) for row in cursor.fetchall()]
            return orders
        finally:
            conn.close()
    
    # =================== 余额相关操作 ===================
    
    def get_user_balance(self, user_id):
        """获取用户余额"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['balance'] if result else 0.0
        finally:
            conn.close()
    
    def recharge_balance(self, user_id, amount):
        """用户充值 - 使用乐观锁防止并发问题"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                amount = float(amount)
                if amount <= 0:
                    return {'success': False, 'message': '充值金额必须大于0'}
                
                # 获取当前余额
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if not result:
                    return {'success': False, 'message': '用户不存在'}
                
                old_balance = result['balance']
                new_balance = old_balance + amount
                
                # 更新余额
                cursor.execute('''
                    UPDATE users SET balance = ? WHERE user_id = ? AND balance = ?
                ''', (new_balance, user_id, old_balance))
                
                if cursor.rowcount == 0:
                    # 更新失败，可能是并发修改，重试
                    return self.recharge_balance(user_id, amount)
                
                conn.commit()
                return {
                    'success': True, 
                    'message': f'充值成功！当前余额：¥{new_balance:.2f}',
                    'balance': new_balance
                }
            except ValueError:
                return {'success': False, 'message': '充值金额必须是数字'}
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': f'充值失败: {str(e)}'}
            finally:
                conn.close()
    
    def purchase_goods(self, goods_id, buyer_id, seller_id, price):
        """购买商品 - 完整事务处理"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # 开始事务
                cursor.execute('BEGIN IMMEDIATE TRANSACTION')
                
                # 1. 检查商品状态（加锁）
                cursor.execute('''
                    SELECT status, seller_id FROM goods WHERE goods_id = ?
                ''', (goods_id,))
                goods = cursor.fetchone()
                
                if not goods:
                    raise Exception('商品不存在')
                
                if goods['status'] != 'available':
                    raise Exception('商品已售出或已下架')
                
                if goods['seller_id'] == buyer_id:
                    raise Exception('不能购买自己的商品')
                
                # 2. 检查买家余额
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (buyer_id,))
                buyer = cursor.fetchone()
                
                if not buyer:
                    raise Exception('买家不存在')
                
                if buyer['balance'] < price:
                    raise Exception('余额不足，请先充值')
                
                # 3. 扣除买家余额
                new_buyer_balance = buyer['balance'] - price
                cursor.execute('''
                    UPDATE users SET balance = ? WHERE user_id = ?
                ''', (new_buyer_balance, buyer_id))
                
                # 4. 增加卖家余额
                cursor.execute('''
                    UPDATE users SET balance = balance + ? WHERE user_id = ?
                ''', (price, seller_id))
                
                # 5. 创建订单
                from common.utils import generate_order_id
                order_id = generate_order_id()
                cursor.execute('''
                    INSERT INTO orders (order_id, goods_id, buyer_id, seller_id, price, status, create_time)
                    VALUES (?, ?, ?, ?, ?, 'completed', ?)
                ''', (order_id, goods_id, buyer_id, seller_id, price, get_current_time()))
                
                # 6. 更新商品状态为已售
                cursor.execute('''
                    UPDATE goods SET status = 'sold' WHERE goods_id = ?
                ''', (goods_id,))
                
                # 提交事务
                conn.commit()
                
                return {
                    'success': True,
                    'message': '购买成功！',
                    'order_id': order_id,
                    'new_balance': new_buyer_balance
                }
                
            except Exception as e:
                conn.rollback()
                return {'success': False, 'message': str(e)}
            finally:
                conn.close()
    
    # =================== 统计分析功能 ===================
    
    def get_goods_category_stats(self):
        """获取商品类别统计数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT category, COUNT(*) as count
                FROM goods
                WHERE status != 'removed'
                GROUP BY category
                ORDER BY count DESC
            ''')
            
            stats = {row['category']: row['count'] for row in cursor.fetchall()}
            return stats
        finally:
            conn.close()
    
    def get_daily_sales_stats(self, days=7):
        """获取最近N天的销售统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    substr(create_time, 1, 10) as date,
                    SUM(price) as total_amount,
                    COUNT(*) as order_count
                FROM orders
                WHERE status = 'completed'
                GROUP BY date
                ORDER BY date DESC
                LIMIT ?
            ''', (days,))
            
            stats = [(row['date'], row['total_amount']) for row in cursor.fetchall()]
            return stats[::-1]  # 反转为升序
        finally:
            conn.close()
    
    def get_top_sellers(self, limit=10):
        """获取销售排行榜"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    u.username,
                    COUNT(o.order_id) as sales_count,
                    SUM(o.price) as total_revenue
                FROM users u
                JOIN orders o ON u.user_id = o.seller_id
                WHERE o.status = 'completed'
                GROUP BY u.user_id
                ORDER BY total_revenue DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_system_statistics(self):
        """获取系统综合统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # 用户统计
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = ?', (USER_ROLE,))
            stats['total_users'] = cursor.fetchone()['count']
            
            # 商品统计
            cursor.execute('SELECT COUNT(*) as count FROM goods WHERE status = "available"')
            stats['available_goods'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM goods WHERE status = "sold"')
            stats['sold_goods'] = cursor.fetchone()['count']
            
            # 订单统计
            cursor.execute('SELECT COUNT(*) as count, SUM(price) as total FROM orders WHERE status = "completed"')
            order_stats = cursor.fetchone()
            stats['total_orders'] = order_stats['count'] or 0
            stats['total_revenue'] = order_stats['total'] or 0.0
            
            return stats
        finally:
            conn.close()

# 使用示例
if __name__ == "__main__":
    db = Database()
    print("数据库初始化完成")
    
    # 测试统计功能
    stats = db.get_system_statistics()
    print(f"系统统计: {stats}")