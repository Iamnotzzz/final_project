import socket
import threading
import json
from common.config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE
from common.utils import serialize_data, deserialize_data
from server.database import Database

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, SERVER_PORT))
        self.db = Database()
        self.clients = {}
        self.running = False
    
    def start(self):
        """启动服务器"""
        self.running = True
        self.server.listen(5)
        print(f"服务器启动成功，监听 {SERVER_HOST}:{SERVER_PORT}")
        
        while self.running:
            try:
                client_socket, address = self.server.accept()
                print(f"新连接来自: {address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"接受连接时发生错误: {e}")
    
    def handle_client(self, client_socket, address):
        """处理客户端请求"""
        try:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                try:
                    request = deserialize_data(data.decode('utf-8'))
                    response = self.process_request(request, client_socket)
                    
                    response_data = serialize_data(response)
                    client_socket.send(response_data.encode('utf-8'))
                    
                except json.JSONDecodeError:
                    error_response = {'success': False, 'message': '数据格式错误'}
                    client_socket.send(serialize_data(error_response).encode('utf-8'))
                
        except Exception as e:
            print(f"处理客户端 {address} 时发生错误: {e}")
        finally:
            client_socket.close()
            if address in self.clients:
                del self.clients[address]
            print(f"客户端 {address} 断开连接")
    
    def process_request(self, request, client_socket):
        """处理客户端请求"""
        action = request.get('action')
        data = request.get('data', {})
        
        if action == 'register':
            return self.handle_register(data)
        elif action == 'login':
            return self.handle_login(data, client_socket)
        elif action == 'get_all_goods':
            return self.handle_get_all_goods()
        elif action == 'add_goods':
            return self.handle_add_goods(data)
        elif action == 'get_user_goods':
            return self.handle_get_user_goods(data)
        elif action == 'create_order':
            return self.handle_create_order(data)
        elif action == 'get_user_orders':
            return self.handle_get_user_orders(data)
        elif action == 'get_all_users':
            return self.handle_get_all_users(data)
        elif action == 'update_goods_status':
            return self.handle_update_goods_status(data)
        elif action == 'recharge_balance':
            return self.handle_recharge_balance(data)
        elif action == 'purchase_goods':
            return self.handle_purchase_goods(data)
        elif action == 'get_user_balance':
            return self.handle_get_user_balance(data)
        elif action == 'remove_goods':
            return self.handle_remove_goods(data)
        elif action == 'delete_user':
            return self.handle_delete_user(data)
        elif action == 'get_all_orders':
            return self.handle_get_all_orders(data)
        else:
            return {'success': False, 'message': '未知操作'}
    
    def handle_register(self, data):
        """处理用户注册"""
        username = data.get('username')
        password = data.get('password')
        contact = data.get('contact')
        
        if not username or not password:
            return {'success': False, 'message': '用户名和密码不能为空'}
        
        result = self.db.register_user(username, password, contact)
        return result
    
    def handle_login(self, data, client_socket):
        """处理用户登录"""
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'success': False, 'message': '用户名和密码不能为空'}
        
        user = self.db.login_user(username, password)
        if user:
            # 记录登录用户
            self.clients[client_socket.getpeername()] = user
            return {'success': True, 'user': user}
        else:
            return {'success': False, 'message': '用户名或密码错误'}
    
    def handle_get_all_goods(self):
        """处理获取所有商品"""
        goods = self.db.get_all_goods()
        return {'success': True, 'goods': goods}
    
    def handle_add_goods(self, data):
        """处理添加商品"""
        name = data.get('name')
        category = data.get('category')
        price = data.get('price')
        description = data.get('description')
        seller_id = data.get('seller_id')
        
        if not all([name, category, price, seller_id]):
            return {'success': False, 'message': '商品信息不完整'}
        
        result = self.db.add_goods(name, category, price, description, seller_id)
        return result
    
    def handle_get_user_goods(self, data):
        """处理获取用户商品"""
        user_id = data.get('user_id')
        
        if not user_id:
            return {'success': False, 'message': '用户ID不能为空'}
        
        goods = self.db.get_user_goods(user_id)
        return {'success': True, 'goods': goods}
    
    def handle_create_order(self, data):
        """处理创建订单"""
        goods_id = data.get('goods_id')
        buyer_id = data.get('buyer_id')
        seller_id = data.get('seller_id')
        price = data.get('price')
        
        if not all([goods_id, buyer_id, seller_id, price]):
            return {'success': False, 'message': '订单信息不完整'}
        
        result = self.db.create_order(goods_id, buyer_id, seller_id, price)
        return result
    
    def handle_get_user_orders(self, data):
        """处理获取用户订单"""
        user_id = data.get('user_id')
        
        if not user_id:
            return {'success': False, 'message': '用户ID不能为空'}
        
        orders = self.db.get_user_orders(user_id)
        return {'success': True, 'orders': orders}
    
    def handle_get_all_users(self, data):
        """处理获取所有用户（管理员功能）"""
        users = self.db.get_all_users()
        return {'success': True, 'users': users}
    
    def handle_update_goods_status(self, data):
        """处理更新商品状态"""
        goods_id = data.get('goods_id')
        status = data.get('status')
        
        if not goods_id or not status:
            return {'success': False, 'message': '商品ID和状态不能为空'}
        
        self.db.update_goods_status(goods_id, status)
        return {'success': True}
    
    def handle_recharge_balance(self, data):
        """处理用户充值"""
        user_id = data.get('user_id')
        amount = data.get('amount')
        
        if not user_id or not amount:
            return {'success': False, 'message': '用户ID和充值金额不能为空'}
        
        result = self.db.recharge_balance(user_id, amount)
        return result
    
    def handle_purchase_goods(self, data):
        """处理购买商品"""
        goods_id = data.get('goods_id')
        buyer_id = data.get('buyer_id')
        
        if not goods_id or not buyer_id:
            return {'success': False, 'message': '商品ID和买家ID不能为空'}
        
        # 获取商品信息
        goods_list = self.db.get_all_goods()
        target_goods = None
        for goods in goods_list:
            if goods['goods_id'] == goods_id:
                target_goods = goods
                break
        
        if not target_goods:
            return {'success': False, 'message': '商品不存在'}
        
        result = self.db.purchase_goods(
            goods_id, 
            buyer_id, 
            target_goods['seller_id'], 
            target_goods['price']
        )
        return result
    
    def handle_get_user_balance(self, data):
        """处理获取用户余额"""
        user_id = data.get('user_id')
        
        if not user_id:
            return {'success': False, 'message': '用户ID不能为空'}
        
        balance = self.db.get_user_balance(user_id)
        return {'success': True, 'balance': balance}
    
    def handle_remove_goods(self, data):
        """处理下架商品"""
        goods_id = data.get('goods_id')
        
        if not goods_id:
            return {'success': False, 'message': '商品ID不能为空'}
        
        result = self.db.remove_goods(goods_id)
        return result
    
    def handle_delete_user(self, data):
        """处理删除用户"""
        user_id = data.get('user_id')
        
        if not user_id:
            return {'success': False, 'message': '用户ID不能为空'}
        
        result = self.db.delete_user(user_id)
        return result
    
    def handle_get_all_orders(self, data):
        """处理获取所有订单（管理员功能）"""
        orders = self.db.get_all_orders()
        return {'success': True, 'orders': orders}
    
    def stop(self):
        """停止服务器"""
        self.running = False
        self.server.close()

if __name__ == "__main__":
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        server.stop()