import hashlib
import json
import datetime

def hash_password(password):
    """密码哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()

def serialize_data(data):
    """序列化数据为JSON"""
    return json.dumps(data, ensure_ascii=False, default=str)

def deserialize_data(data):
    """反序列化JSON数据"""
    return json.loads(data)

def get_current_time():
    """获取当前时间字符串"""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def generate_order_id():
    """生成订单ID"""
    import uuid
    return str(uuid.uuid4())[:8]