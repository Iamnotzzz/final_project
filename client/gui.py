import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from client.network_client import NetworkClient
from common.config import ADMIN_ROLE

class SecondHandSystemGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("校园二手交易平台")
        self.root.geometry("800x600")
        
        self.network_client = NetworkClient()
        self.current_user = None
        
        self.login_window()
    
    def login_window(self):
        """登录窗口"""
        self.clear_window()
        
        login_frame = ttk.Frame(self.root, padding="20")
        login_frame.pack(expand=True)
        
        ttk.Label(login_frame, text="校园二手交易平台", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(login_frame, text="用户名:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="密码:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(login_frame, text="登录", command=self.login).grid(row=3, column=0, padx=5, pady=10)
        ttk.Button(login_frame, text="注册", command=self.register_window).grid(row=3, column=1, padx=5, pady=10)
        
        # 默认管理员账户提示
        ttk.Label(login_frame, text="默认管理员: admin/admin123", font=("Arial", 8)).grid(row=4, column=0, columnspan=2, pady=5)
    
    def register_window(self):
        """注册窗口"""
        register_window = tk.Toplevel(self.root)
        register_window.title("用户注册")
        register_window.geometry("300x250")
        
        ttk.Label(register_window, text="用户注册", font=("Arial", 14)).pack(pady=10)
        
        ttk.Label(register_window, text="用户名:").pack()
        reg_username_entry = ttk.Entry(register_window)
        reg_username_entry.pack(pady=5)
        
        ttk.Label(register_window, text="密码:").pack()
        reg_password_entry = ttk.Entry(register_window, show="*")
        reg_password_entry.pack(pady=5)
        
        ttk.Label(register_window, text="联系方式:").pack()
        reg_contact_entry = ttk.Entry(register_window)
        reg_contact_entry.pack(pady=5)
        
        def register():
            username = reg_username_entry.get()
            password = reg_password_entry.get()
            contact = reg_contact_entry.get()
            
            if not username or not password:
                messagebox.showerror("错误", "用户名和密码不能为空")
                return
            
            if not self.network_client.connected:
                if not self.network_client.connect():
                    messagebox.showerror("错误", "无法连接到服务器")
                    return
            
            result = self.network_client.register(username, password, contact)
            if result['success']:
                messagebox.showinfo("成功", "注册成功！请登录")
                register_window.destroy()
            else:
                messagebox.showerror("错误", result['message'])
        
        ttk.Button(register_window, text="注册", command=register).pack(pady=10)
    
    def login(self):
        """登录处理"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("错误", "用户名和密码不能为空")
            return
        
        if not self.network_client.connected:
            if not self.network_client.connect():
                messagebox.showerror("错误", "无法连接到服务器")
                return
        
        result = self.network_client.login(username, password)
        if result['success']:
            self.current_user = result['user']
            messagebox.showinfo("成功", f"欢迎, {self.current_user['username']}!")
            
            if self.current_user['role'] == ADMIN_ROLE:
                self.admin_main_window()
            else:
                self.user_main_window()
        else:
            messagebox.showerror("错误", result['message'])
    
    def user_main_window(self):
        """普通用户主窗口"""
        self.clear_window()
        
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 用户菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="用户", menu=user_menu)
        user_menu.add_command(label="我的商品", command=self.my_goods_window)
        user_menu.add_command(label="我的订单", command=self.my_orders_window)
        user_menu.add_command(label="账户充值", command=self.recharge_window)
        user_menu.add_command(label="退出登录", command=self.logout)
        
        # 商品菜单
        goods_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="商品", menu=goods_menu)
        goods_menu.add_command(label="发布商品", command=self.add_goods_window)
        goods_menu.add_command(label="刷新商品列表", command=self.refresh_goods_list)
        
        # 主界面
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 用户信息框架
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"欢迎, {self.current_user['username']}", font=("Arial", 14)).pack(side=tk.LEFT)
        
        # 余额显示
        self.balance_label = ttk.Label(info_frame, text="余额: ¥0.00", font=("Arial", 12))
        self.balance_label.pack(side=tk.RIGHT, padx=10)
        
        # 刷新余额
        self.refresh_balance()
        
        # 商品列表
        self.goods_tree = ttk.Treeview(main_frame, columns=("名称", "类别", "价格", "卖家", "发布时间"), show="headings")
        self.goods_tree.heading("名称", text="商品名称")
        self.goods_tree.heading("类别", text="类别")
        self.goods_tree.heading("价格", text="价格")
        self.goods_tree.heading("卖家", text="卖家")
        self.goods_tree.heading("发布时间", text="发布时间")
        
        self.goods_tree.column("名称", width=150)
        self.goods_tree.column("类别", width=100)
        self.goods_tree.column("价格", width=100)
        self.goods_tree.column("卖家", width=100)
        self.goods_tree.column("发布时间", width=150)
        
        self.goods_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 购买按钮
        ttk.Button(main_frame, text="购买选中商品", command=self.buy_goods).pack(pady=5)
        
        self.refresh_goods_list()
    
    def admin_main_window(self):
        """管理员主窗口"""
        self.clear_window()
        
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 管理菜单
        admin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="管理", menu=admin_menu)
        admin_menu.add_command(label="用户管理", command=self.manage_users_window)
        admin_menu.add_command(label="商品管理", command=self.manage_goods_window)
        admin_menu.add_command(label="交易记录", command=self.manage_all_orders_window)
        admin_menu.add_command(label="退出登录", command=self.logout)
        
        # 主界面
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"管理员面板 - {self.current_user['username']}", font=("Arial", 14)).pack(pady=10)
        
        ttk.Button(main_frame, text="用户管理", command=self.manage_users_window, width=20).pack(pady=5)
        ttk.Button(main_frame, text="商品管理", command=self.manage_goods_window, width=20).pack(pady=5)
        ttk.Button(main_frame, text="交易记录", command=self.manage_all_orders_window, width=20).pack(pady=5)
    
    def refresh_goods_list(self):
        """刷新商品列表"""
        if not self.network_client.connected:
            return
        
        result = self.network_client.get_all_goods()
        if result['success']:
            # 清空现有列表
            for item in self.goods_tree.get_children():
                self.goods_tree.delete(item)
            
            # 添加新数据
            for goods in result['goods']:
                self.goods_tree.insert("", "end", values=(
                    goods['name'],
                    goods['category'],
                    f"¥{goods['price']}",
                    goods['seller_name'],
                    goods['publish_time']
                ))
    
    def add_goods_window(self):
        """发布商品窗口"""
        add_window = tk.Toplevel(self.root)
        add_window.title("发布商品")
        add_window.geometry("400x350")
        
        ttk.Label(add_window, text="发布商品", font=("Arial", 14)).pack(pady=10)
        
        ttk.Label(add_window, text="商品名称:").pack()
        name_entry = ttk.Entry(add_window, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(add_window, text="商品类别:").pack()
        # 预定义商品类别
        categories = ["学习资料", "零食饮料", "宿舍用品", "电子产品", "服装鞋帽", "生活用品", "运动器材", "其他"]
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(add_window, textvariable=category_var, values=categories, width=28, state="readonly")
        category_combo.pack(pady=5)
        category_combo.set(categories[0])  # 设置默认值
        
        ttk.Label(add_window, text="价格:").pack()
        price_entry = ttk.Entry(add_window, width=30)
        price_entry.pack(pady=5)
        
        ttk.Label(add_window, text="商品描述:").pack()
        description_text = tk.Text(add_window, width=30, height=5)
        description_text.pack(pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(add_window)
        button_frame.pack(pady=10)
        
        def add_goods():
            name = name_entry.get()
            category = category_var.get()
            price = price_entry.get()
            description = description_text.get("1.0", tk.END).strip()
            
            if not all([name, category, price]):
                messagebox.showerror("错误", "请填写完整信息")
                return
            
            try:
                price = float(price)
            except ValueError:
                messagebox.showerror("错误", "价格必须是数字")
                return
            
            result = self.network_client.add_goods(name, category, price, description, self.current_user['user_id'])
            if result['success']:
                messagebox.showinfo("成功", "商品发布成功！")
                add_window.destroy()
                self.refresh_goods_list()
            else:
                messagebox.showerror("错误", result['message'])
        
        ttk.Button(button_frame, text="发布商品", command=add_goods).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def buy_goods(self):
        """购买商品"""
        selected = self.goods_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要购买的商品")
            return
        
        # 获取选中的商品信息
        item = self.goods_tree.item(selected[0])
        goods_name = item['values'][0]
        price_str = item['values'][2].replace('¥', '')
        
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("错误", "商品价格格式错误")
            return
        
        # 获取商品ID（需要从商品列表中查找）
        goods_id = None
        result = self.network_client.get_all_goods()
        if result['success']:
            for goods in result['goods']:
                if goods['name'] == goods_name and goods['price'] == price:
                    goods_id = goods['goods_id']
                    break
        
        if not goods_id:
            messagebox.showerror("错误", "无法获取商品信息")
            return
        
        if messagebox.askyesno("确认购买", f"确定要购买 {goods_name} 吗？\n价格: ¥{price}"):
            result = self.network_client.purchase_goods(goods_id, self.current_user['user_id'])
            if result['success']:
                # 使用服务端返回的余额更新显示
                new_balance = result.get('new_balance', 0.0)
                if hasattr(self, 'balance_label'):
                    self.balance_label.config(text=f"余额: ¥{new_balance:.2f}")
                
                messagebox.showinfo("成功", f"{result['message']}\n订单号: {result.get('order_id', 'N/A')}")
                self.refresh_goods_list()
            else:
                messagebox.showerror("错误", result['message'])
    
    def my_goods_window(self):
        """我的商品窗口"""
        my_window = tk.Toplevel(self.root)
        my_window.title("我的商品")
        my_window.geometry("600x400")
        
        ttk.Label(my_window, text="我的商品", font=("Arial", 14)).pack(pady=10)
        
        result = self.network_client.get_user_goods(self.current_user['user_id'])
        if result['success']:
            goods_tree = ttk.Treeview(my_window, columns=("名称", "类别", "价格", "状态", "发布时间"), show="headings")
            goods_tree.heading("名称", text="商品名称")
            goods_tree.heading("类别", text="类别")
            goods_tree.heading("价格", text="价格")
            goods_tree.heading("状态", text="状态")
            goods_tree.heading("发布时间", text="发布时间")
            
            goods_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for goods in result['goods']:
                goods_tree.insert("", "end", values=(
                    goods['name'],
                    goods['category'],
                    f"¥{goods['price']}",
                    goods['status'],
                    goods['publish_time']
                ))
    
    def my_orders_window(self):
        """我的订单窗口"""
        orders_window = tk.Toplevel(self.root)
        orders_window.title("我的订单")
        orders_window.geometry("700x400")
        
        ttk.Label(orders_window, text="我的订单", font=("Arial", 14)).pack(pady=10)
        
        result = self.network_client.get_user_orders(self.current_user['user_id'])
        if result['success']:
            orders_tree = ttk.Treeview(orders_window, columns=("订单号", "商品", "买家", "卖家", "价格", "状态", "时间"), show="headings")
            orders_tree.heading("订单号", text="订单号")
            orders_tree.heading("商品", text="商品名称")
            orders_tree.heading("买家", text="买家")
            orders_tree.heading("卖家", text="卖家")
            orders_tree.heading("价格", text="价格")
            orders_tree.heading("状态", text="状态")
            orders_tree.heading("时间", text="创建时间")
            
            orders_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for order in result['orders']:
                orders_tree.insert("", "end", values=(
                    order['order_id'],
                    order['goods_name'],
                    order['buyer_name'],
                    order['seller_name'],
                    f"¥{order['price']}",
                    order['status'],
                    order['create_time']
                ))
    
    def manage_users_window(self):
        """用户管理窗口"""
        users_window = tk.Toplevel(self.root)
        users_window.title("用户管理")
        users_window.geometry("600x450")
        
        ttk.Label(users_window, text="用户管理", font=("Arial", 14)).pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(users_window)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="删除选中用户", command=lambda: self.delete_selected_user(users_window, users_tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新列表", command=lambda: self.refresh_users_list_in_window(users_tree)).pack(side=tk.LEFT, padx=5)
        
        result = self.network_client.get_all_users()
        if result['success']:
            users_tree = ttk.Treeview(users_window, columns=("ID", "用户名", "角色", "联系方式", "余额", "注册时间"), show="headings")
            users_tree.heading("ID", text="用户ID")
            users_tree.heading("用户名", text="用户名")
            users_tree.heading("角色", text="角色")
            users_tree.heading("联系方式", text="联系方式")
            users_tree.heading("余额", text="余额")
            users_tree.heading("注册时间", text="注册时间")
            
            users_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for user in result['users']:
                users_tree.insert("", "end", values=(
                    user['user_id'],
                    user['username'],
                    user['role'],
                    user['contact'],
                    f"¥{user.get('balance', 0):.2f}",
                    user['created_at']
                ))
    
    def manage_goods_window(self):
        """商品管理窗口"""
        goods_window = tk.Toplevel(self.root)
        goods_window.title("商品管理")
        goods_window.geometry("700x450")
        
        ttk.Label(goods_window, text="商品管理", font=("Arial", 14)).pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(goods_window)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="下架选中商品", command=lambda: self.remove_selected_goods(goods_tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新列表", command=lambda: self.refresh_goods_list_in_window(goods_tree)).pack(side=tk.LEFT, padx=5)
        
        result = self.network_client.get_all_goods()
        if result['success']:
            goods_tree = ttk.Treeview(goods_window, columns=("ID", "名称", "类别", "价格", "卖家", "状态", "发布时间"), show="headings")
            goods_tree.heading("ID", text="商品ID")
            goods_tree.heading("名称", text="商品名称")
            goods_tree.heading("类别", text="类别")
            goods_tree.heading("价格", text="价格")
            goods_tree.heading("卖家", text="卖家")
            goods_tree.heading("状态", text="状态")
            goods_tree.heading("发布时间", text="发布时间")
            
            goods_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for goods in result['goods']:
                goods_tree.insert("", "end", values=(
                    goods['goods_id'],
                    goods['name'],
                    goods['category'],
                    f"¥{goods['price']}",
                    goods['seller_name'],
                    goods['status'],
                    goods['publish_time']
                ))
    
    def recharge_window(self):
        """充值窗口"""
        recharge_window = tk.Toplevel(self.root)
        recharge_window.title("账户充值")
        recharge_window.geometry("300x200")
        
        ttk.Label(recharge_window, text="账户充值", font=("Arial", 14)).pack(pady=10)
        
        # 显示当前余额
        current_balance = self.get_current_balance()
        ttk.Label(recharge_window, text=f"当前余额: ¥{current_balance:.2f}").pack(pady=5)
        
        ttk.Label(recharge_window, text="充值金额:").pack()
        amount_entry = ttk.Entry(recharge_window, width=20)
        amount_entry.pack(pady=5)
        
        def recharge():
            amount = amount_entry.get()
            if not amount:
                messagebox.showerror("错误", "请输入充值金额")
                return
            
            try:
                amount = float(amount)
                if amount <= 0:
                    messagebox.showerror("错误", "充值金额必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "充值金额必须是数字")
                return
            
            result = self.network_client.recharge_balance(self.current_user['user_id'], amount)
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self.refresh_balance()
                recharge_window.destroy()
            else:
                messagebox.showerror("错误", result['message'])
        
        # 按钮框架
        button_frame = ttk.Frame(recharge_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确认充值", command=recharge).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=recharge_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def get_current_balance(self):
        """获取当前用户余额"""
        result = self.network_client.get_user_balance(self.current_user['user_id'])
        if result['success']:
            return result['balance']
        return 0.0
    
    def refresh_balance(self):
        """刷新余额显示"""
        if hasattr(self, 'balance_label'):
            balance = self.get_current_balance()
            self.balance_label.config(text=f"余额: ¥{balance:.2f}")
    
    def remove_selected_goods(self, goods_tree):
        """下架选中的商品"""
        selected = goods_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要下架的商品")
            return
        
        item = goods_tree.item(selected[0])
        goods_id = item['values'][0]
        goods_name = item['values'][1]
        
        if messagebox.askyesno("确认下架", f"确定要下架商品 '{goods_name}' 吗？"):
            result = self.network_client.remove_goods(goods_id)
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self.refresh_goods_list_in_window(goods_tree)
            else:
                messagebox.showerror("错误", result['message'])
    
    def delete_selected_user(self, parent_window, users_tree):
        """删除选中的用户"""
        selected = users_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的用户")
            return
        
        item = users_tree.item(selected[0])
        user_id = item['values'][0]
        username = item['values'][1]
        role = item['values'][2]
        
        if role == 'admin':
            messagebox.showerror("错误", "不能删除管理员账户")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除用户 '{username}' 吗？\n这将同时删除该用户的所有商品和订单记录！"):
            result = self.network_client.delete_user(user_id)
            if result['success']:
                messagebox.showinfo("成功", result['message'])
                self.refresh_users_list_in_window(users_tree)
            else:
                messagebox.showerror("错误", result['message'])
    
    def refresh_goods_list_in_window(self, goods_tree):
        """刷新指定窗口中的商品列表"""
        # 清空现有列表
        for item in goods_tree.get_children():
            goods_tree.delete(item)
        
        # 重新加载数据
        result = self.network_client.get_all_goods()
        if result['success']:
            for goods in result['goods']:
                goods_tree.insert("", "end", values=(
                    goods['goods_id'],
                    goods['name'],
                    goods['category'],
                    f"¥{goods['price']}",
                    goods['seller_name'],
                    goods['status'],
                    goods['publish_time']
                ))
    
    def refresh_users_list_in_window(self, users_tree):
        """刷新指定窗口中的用户列表"""
        # 清空现有列表
        for item in users_tree.get_children():
            users_tree.delete(item)
        
        # 重新加载数据
        result = self.network_client.get_all_users()
        if result['success']:
            for user in result['users']:
                users_tree.insert("", "end", values=(
                    user['user_id'],
                    user['username'],
                    user['role'],
                    user['contact'],
                    f"¥{user.get('balance', 0):.2f}",
                    user['created_at']
                ))
    
    def logout(self):
        """退出登录"""
        self.current_user = None
        self.network_client.disconnect()
        self.login_window()
    
    def clear_window(self):
        """清空窗口"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def manage_all_orders_window(self):
        """所有交易记录窗口"""
        orders_window = tk.Toplevel(self.root)
        orders_window.title("交易记录管理")
        orders_window.geometry("900x500")
        
        ttk.Label(orders_window, text="所有交易记录", font=("Arial", 14)).pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(orders_window)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="刷新列表", command=lambda: self.refresh_all_orders_list(orders_tree)).pack(side=tk.LEFT, padx=5)
        
        # 交易记录表格
        orders_tree = ttk.Treeview(orders_window, columns=("订单号", "商品", "买家", "卖家", "价格", "状态", "创建时间"), show="headings")
        orders_tree.heading("订单号", text="订单号")
        orders_tree.heading("商品", text="商品名称")
        orders_tree.heading("买家", text="买家")
        orders_tree.heading("卖家", text="卖家")
        orders_tree.heading("价格", text="价格")
        orders_tree.heading("状态", text="状态")
        orders_tree.heading("创建时间", text="创建时间")
        
        # 设置列宽
        orders_tree.column("订单号", width=100)
        orders_tree.column("商品", width=150)
        orders_tree.column("买家", width=100)
        orders_tree.column("卖家", width=100)
        orders_tree.column("价格", width=80)
        orders_tree.column("状态", width=80)
        orders_tree.column("创建时间", width=150)
        
        orders_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 加载数据
        self.refresh_all_orders_list(orders_tree)
    
    def refresh_all_orders_list(self, orders_tree):
        """刷新所有交易记录列表"""
        # 清空现有列表
        for item in orders_tree.get_children():
            orders_tree.delete(item)
        
        # 重新加载数据
        result = self.network_client.get_all_orders()
        if result['success']:
            for order in result['orders']:
                orders_tree.insert("", "end", values=(
                    order['order_id'],
                    order['goods_name'],
                    order['buyer_name'],
                    order['seller_name'],
                    f"¥{order['price']}",
                    order['status'],
                    order['create_time']
                ))
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SecondHandSystemGUI()
    app.run()