import socket
import json
from common.config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE
from common.utils import serialize_data, deserialize_data

class NetworkClient:
    def __init__(self):
        self.client = None
        self.connected = False
    
    def connect(self):
        """连接到服务器"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((SERVER_HOST, SERVER_PORT))
            self.connected = True
            return True
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.connected = False
    
    def send_request(self, action, data=None):
        """发送请求到服务器"""
        if not self.connected:
            return {'success': False, 'message': '未连接到服务器'}
        
        try:
            request = {'action': action, 'data': data or {}}
            request_data = serialize_data(request)
            request_bytes = request_data.encode('utf-8')
            
            # 发送数据长度头
            request_length = len(request_bytes)
            self.client.send(request_length.to_bytes(4, byteorder='big'))
            # 发送实际数据
            self.client.send(request_bytes)
            
            # 接收响应长度头
            length_data = self._recv_exact(4)
            if not length_data:
                return {'success': False, 'message': '接收响应长度失败'}
            
            response_length = int.from_bytes(length_data, byteorder='big')
            
            # 接收完整响应数据
            response_bytes = self._recv_exact(response_length)
            if not response_bytes:
                return {'success': False, 'message': '接收响应数据失败'}
            
            response = deserialize_data(response_bytes.decode('utf-8'))
            
            # 检查是否需要强制退出
            if response.get('force_logout'):
                # 断开连接并返回特殊标志
                self.disconnect()
                response['force_logout_disconnected'] = True
            
            return response
        except Exception as e:
            print(f"发送请求失败: {e}")
            return {'success': False, 'message': '网络请求失败'}
    
    def _recv_exact(self, length):
        """精确接收指定长度的数据"""
        data = b''
        while len(data) < length:
            chunk = self.client.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def register(self, username, password, contact=None):
        """用户注册"""
        return self.send_request('register', {
            'username': username,
            'password': password,
            'contact': contact
        })
    
    def login(self, username, password):
        """用户登录"""
        return self.send_request('login', {
            'username': username,
            'password': password
        })
    
    def get_all_goods(self):
        """获取所有商品"""
        return self.send_request('get_all_goods')
    
    def add_goods(self, name, category, price, description, seller_id):
        """添加商品"""
        return self.send_request('add_goods', {
            'name': name,
            'category': category,
            'price': price,
            'description': description,
            'seller_id': seller_id
        })
    
    def get_user_goods(self, user_id):
        """获取用户商品"""
        return self.send_request('get_user_goods', {
            'user_id': user_id
        })
    
    def create_order(self, goods_id, buyer_id, seller_id, price):
        """创建订单"""
        return self.send_request('create_order', {
            'goods_id': goods_id,
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'price': price
        })
    
    def get_user_orders(self, user_id):
        """获取用户订单"""
        return self.send_request('get_user_orders', {
            'user_id': user_id
        })
    
    def get_all_users(self):
        """获取所有用户（管理员功能）"""
        return self.send_request('get_all_users')
    
    def update_goods_status(self, goods_id, status):
        """更新商品状态"""
        return self.send_request('update_goods_status', {
            'goods_id': goods_id,
            'status': status
        })
    
    def recharge_balance(self, user_id, amount):
        """用户充值"""
        return self.send_request('recharge_balance', {
            'user_id': user_id,
            'amount': amount
        })
    
    def purchase_goods(self, goods_id, buyer_id):
        """购买商品"""
        return self.send_request('purchase_goods', {
            'goods_id': goods_id,
            'buyer_id': buyer_id
        })
    
    def get_user_balance(self, user_id):
        """获取用户余额"""
        return self.send_request('get_user_balance', {
            'user_id': user_id
        })
    
    def remove_goods(self, goods_id):
        """下架商品"""
        return self.send_request('remove_goods', {
            'goods_id': goods_id
        })
    
    def delete_user(self, user_id):
        """删除用户"""
        return self.send_request('delete_user', {
            'user_id': user_id
        })
    
    def get_all_orders(self):
        """获取所有订单（管理员功能）"""
        return self.send_request('get_all_orders')
    
    # --- 在 client/network_client.py 的 NetworkClient 类中添加 ---

    def get_goods_category_stats(self):
        """获取商品类别统计"""
        return self.send_request('get_goods_category_stats')

    def get_daily_sales_stats(self):
        """获取每日销量统计"""
        return self.send_request('get_daily_sales_stats')