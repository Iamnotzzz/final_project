import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, END, VERTICAL, HORIZONTAL
from client.network_client import NetworkClient
from common.config import ADMIN_ROLE
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib


matplotlib.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti TC', 'Microsoft YaHei', 'SimHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

class SecondHandSystemGUI:
    def __init__(self):
        self.root = tb.Window(themename="cosmo")
        self.root.title("校园二手交易平台")
        self.root.geometry("1000x700")
        self.center_window(self.root)
        
        self.network_client = NetworkClient()
        self.current_user = None
        
        self.login_window()
    
    def center_window(self, window):
        """窗口居中"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def clear_window(self):
        """清空窗口"""
        for widget in self.root.winfo_children():
            widget.destroy()

    # =================== 登录注册界面 ===================
    
    def login_window(self):
        """登录界面"""
        self.clear_window()
        
        container = tb.Frame(self.root)
        container.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        tb.Label(container, text="校园二手交易平台", 
                font=("微软雅黑", 26, "bold"), 
                bootstyle="primary").pack(pady=30)
        
        login_frame = tb.Labelframe(container, text="用户登录", padding=30, bootstyle="info")
        login_frame.pack(fill=X)
        
        tb.Label(login_frame, text="用户名", font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        self.username_entry = tb.Entry(login_frame, width=35, font=("微软雅黑", 10))
        self.username_entry.pack(fill=X, pady=(0, 15))
        
        tb.Label(login_frame, text="密码", font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        self.password_entry = tb.Entry(login_frame, width=35, show="●", font=("微软雅黑", 10))
        self.password_entry.pack(fill=X, pady=(0, 20))
        
        # 绑定回车键登录
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        btn_frame = tb.Frame(login_frame)
        btn_frame.pack(fill=X, pady=10)
        
        tb.Button(btn_frame, text="登录", bootstyle="primary", 
                 command=self.login, width=12).pack(side=LEFT, padx=(0, 10))
        tb.Button(btn_frame, text="注册新账号", bootstyle="success-outline", 
                 command=self.register_window, width=12).pack(side=LEFT)
        
        tb.Label(container, text="默认管理员: admin / admin123", 
                font=("Arial", 9), bootstyle="secondary").pack(pady=15)

    def register_window(self):
        """注册窗口"""
        reg_win = tb.Toplevel(self.root)
        reg_win.title("用户注册")
        reg_win.geometry("450x550")
        self.center_window(reg_win)
        
        tb.Label(reg_win, text="创建新账户", 
                font=("微软雅黑", 20, "bold"), 
                bootstyle="success").pack(pady=25)
        
        form_frame = tb.Frame(reg_win, padding=30)
        form_frame.pack(fill=BOTH, expand=True)
        
        entries = {}
        fields = [
            ("用户名", "username", None),
            ("密码", "password", "●"),
            ("确认密码", "password2", "●"),
            ("联系方式", "contact", None)
        ]
        
        for label_text, key, show_char in fields:
            tb.Label(form_frame, text=label_text, font=("微软雅黑", 10)).pack(anchor=W, pady=(10, 5))
            entry = tb.Entry(form_frame, show=show_char, font=("微软雅黑", 10))
            entry.pack(fill=X)
            entries[key] = entry
            
        def submit_register():
            username = entries["username"].get().strip()
            password = entries["password"].get()
            password2 = entries["password2"].get()
            contact = entries["contact"].get().strip()
            
            if not username or not password:
                messagebox.showerror("错误", "用户名和密码不能为空")
                return
            
            if len(password) < 6:
                messagebox.showerror("错误", "密码长度至少6位")
                return
                
            if password != password2:
                messagebox.showerror("错误", "两次输入的密码不一致")
                return
            
            if not self.network_client.connected and not self.network_client.connect():
                messagebox.showerror("错误", "无法连接到服务器\n请确保服务器已启动")
                return
                
            res = self.network_client.register(username, password, contact)
            if res['success']:
                messagebox.showinfo("成功", "注册成功！请登录")
                reg_win.destroy()
            else:
                messagebox.showerror("错误", res['message'])
        
        tb.Button(form_frame, text="立即注册", bootstyle="success", 
                 command=submit_register).pack(fill=X, pady=30)

    def login(self):
        """登录处理"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("提示", "请输入完整的登录信息")
            return
        
        if not self.network_client.connected and not self.network_client.connect():
            messagebox.showerror("连接失败", "无法连接到服务器\n请检查服务器是否已启动")
            return
        
        result = self.network_client.login(username, password)
        if result['success']:
            self.current_user = result['user']
            messagebox.showinfo("欢迎", f"欢迎回来，{username}！")
            if self.check_force_logout(result):
                return
            if self.current_user['role'] == ADMIN_ROLE:
                self.admin_main_window()
            else:
                self.user_main_window()
        else:
            messagebox.showerror("登录失败", result['message'])

    # =================== 普通用户主界面 ===================
    
    def user_main_window(self):
        """普通用户主窗口"""
        self.clear_window()
        
        # 顶部导航栏
        nav_bar = tb.Frame(self.root, bootstyle="primary", padding=10)
        nav_bar.pack(fill=X)
        
        tb.Label(nav_bar, text=f"👤 {self.current_user['username']}", 
                font=("微软雅黑", 12, "bold"), 
                bootstyle="inverse-primary").pack(side=LEFT, padx=10)
        
        tb.Button(nav_bar, text="退出登录", bootstyle="danger-outline", 
                 command=self.logout).pack(side=RIGHT, padx=5)
        
        # 主内容区
        main_content = tb.Frame(self.root)
        main_content.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 左侧边栏
        sidebar = tb.Frame(main_content, width=220)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        # 余额卡片
        balance_frame = tb.Labelframe(sidebar, text="💰 账户余额", 
                                      padding=15, bootstyle="info")
        balance_frame.pack(fill=X, pady=(0, 15))
        self.balance_label = tb.Label(balance_frame, text="¥0.00", 
                                      font=("Arial", 18, "bold"), 
                                      bootstyle="info")
        self.balance_label.pack()
        tb.Button(balance_frame, text="充值", bootstyle="warning", 
                 command=self.recharge_window).pack(fill=X, pady=(10, 0))
        
        # 功能菜单
        tb.Label(sidebar, text="📋 功能菜单", 
                font=("微软雅黑", 11, "bold")).pack(anchor=W, pady=(10, 10))
        
        menu_items = [
            ("发布商品", "success", self.add_goods_window),
            ("我的商品", "info", self.my_goods_window),
            ("我的订单", "warning", self.my_orders_window),
            ("刷新列表", "secondary", self.refresh_goods_list),
        ]
        
        for text, style, cmd in menu_items:
            tb.Button(sidebar, text=text, bootstyle=style, 
                     command=cmd).pack(fill=X, pady=3)
        
        # 右侧商品列表
        right_content = tb.Frame(main_content)
        right_content.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 工具栏
        toolbar = tb.Frame(right_content, padding=(0, 0, 0, 10))
        toolbar.pack(fill=X)
        
        tb.Label(toolbar, text="🛒 商品市场", 
                font=("微软雅黑", 14, "bold")).pack(side=LEFT)
        
        tb.Button(toolbar, text="🔍 搜索", bootstyle="info-outline", 
                 command=self.search_goods_window).pack(side=RIGHT, padx=5)
        tb.Button(toolbar, text="💳 购买选中", bootstyle="warning", 
                 command=self.buy_goods).pack(side=RIGHT)
        
        # 商品表格
        table_frame = tb.Frame(right_content)
        table_frame.pack(fill=BOTH, expand=True)
        
        cols = ("ID", "名称", "类别", "价格", "卖家", "发布时间")
        self.goods_tree = tb.Treeview(table_frame, columns=cols, 
                                      show="headings", bootstyle="info")
        
        # 隐藏ID列但保留数据
        self.goods_tree.column("ID", width=0, stretch=False)
        self.goods_tree.heading("ID", text="")
        
        widths = {"名称": 200, "类别": 100, "价格": 100, "卖家": 120, "发布时间": 150}
        for col in cols[1:]:
            self.goods_tree.heading(col, text=col)
            self.goods_tree.column(col, width=widths.get(col, 100))
        
        scrollbar_y = tb.Scrollbar(table_frame, orient=VERTICAL, 
                                   command=self.goods_tree.yview)
        scrollbar_x = tb.Scrollbar(table_frame, orient=HORIZONTAL, 
                                   command=self.goods_tree.xview)
        self.goods_tree.configure(yscrollcommand=scrollbar_y.set, 
                                 xscrollcommand=scrollbar_x.set)
        
        self.goods_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.refresh_balance()
        self.refresh_goods_list()

    # =================== 用户功能窗口 ===================
    
    def add_goods_window(self):
        """发布商品窗口"""
        win = tb.Toplevel(self.root)
        win.title("发布闲置商品")
        win.geometry("500x600")
        self.center_window(win)
        
        layout = tb.Frame(win, padding=25)
        layout.pack(fill=BOTH, expand=True)
        
        tb.Label(layout, text="📦 发布新商品", 
                font=("微软雅黑", 18, "bold"), 
                bootstyle="success").pack(pady=(0, 25))
        
        # 商品名称
        tb.Label(layout, text="商品名称 *", 
                font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        name_entry = tb.Entry(layout, font=("微软雅黑", 10))
        name_entry.pack(fill=X, pady=(0, 15))
        
        # 类别
        tb.Label(layout, text="商品类别 *", 
                font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        categories = ["学习资料", "电子产品", "生活用品", "运动器材", "服饰鞋包", "其他"]
        cat_cb = tb.Combobox(layout, values=categories, state="readonly", 
                            font=("微软雅黑", 10))
        cat_cb.current(0)
        cat_cb.pack(fill=X, pady=(0, 15))
        
        # 价格
        tb.Label(layout, text="价格 (¥) *", 
                font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        price_entry = tb.Entry(layout, font=("微软雅黑", 10))
        price_entry.pack(fill=X, pady=(0, 15))
        
        # 描述
        tb.Label(layout, text="商品描述", 
                font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        desc_frame = tb.Frame(layout)
        desc_frame.pack(fill=BOTH, expand=True, pady=(0, 20))
        
        desc_text = tb.Text(desc_frame, height=6, font=("微软雅黑", 9))
        desc_scroll = tb.Scrollbar(desc_frame, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scroll.set)
        
        desc_text.pack(side=LEFT, fill=BOTH, expand=True)
        desc_scroll.pack(side=RIGHT, fill=Y)
        
        def submit():
            name = name_entry.get().strip()
            category = cat_cb.get()
            price_str = price_entry.get().strip()
            description = desc_text.get("1.0", END).strip()
            
            if not name or not category or not price_str:
                messagebox.showerror("错误", "请填写所有必填项（*）")
                return
            
            try:
                price = float(price_str)
                if price <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("错误", "价格必须是大于0的数字")
                return
            
            result = self.network_client.add_goods(
                name, category, price, description, 
                self.current_user['user_id']
            )
            
            if result['success']:
                messagebox.showinfo("成功", "商品发布成功！")
                win.destroy()
                self.refresh_goods_list()
            else:
                messagebox.showerror("失败", result.get('message', '发布失败'))
        
        btn_frame = tb.Frame(layout)
        btn_frame.pack(fill=X)
        
        tb.Button(btn_frame, text="确认发布", bootstyle="success", 
                 command=submit).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        tb.Button(btn_frame, text="取消", bootstyle="secondary", 
                 command=win.destroy).pack(side=RIGHT, fill=X, expand=True, padx=(5, 0))

    def my_goods_window(self):
        """我的商品窗口"""
        win = tb.Toplevel(self.root)
        win.title("我的商品")
        win.geometry("800x600")
        self.center_window(win)
        
        # 标题
        header = tb.Frame(win, padding=15, bootstyle="info")
        header.pack(fill=X)
        tb.Label(header, text="📦 我的商品", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-info").pack(side=LEFT)
        
        # 表格
        table_frame = tb.Frame(win, padding=10)
        table_frame.pack(fill=BOTH, expand=True)
        
        cols = ("ID", "名称", "类别", "价格", "状态", "发布时间")
        tree = tb.Treeview(table_frame, columns=cols, show="headings")
        
        tree.column("ID", width=0, stretch=False)
        tree.heading("ID", text="")
        
        widths = {"名称": 200, "类别": 100, "价格": 100, "状态": 80, "发布时间": 150}
        for col in cols[1:]:
            tree.heading(col, text=col)
            tree.column(col, width=widths.get(col, 100))
        
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 加载数据
        result = self.network_client.get_user_goods(self.current_user['user_id'])
        if result['success']:
            status_map = {"available": "在售", "sold": "已售", "removed": "已下架"}
            for goods in result['goods']:
                tree.insert("", "end", values=(
                    goods['goods_id'],
                    goods['name'],
                    goods['category'],
                    f"¥{goods['price']:.2f}",
                    status_map.get(goods['status'], goods['status']),
                    goods['publish_time']
                ))
        
        # 操作按钮
        btn_frame = tb.Frame(win, padding=10)
        btn_frame.pack(fill=X)
        
        def remove_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("提示", "请选择要下架的商品")
                return
            
            item = tree.item(sel[0])
            goods_id = item['values'][0]
            goods_name = item['values'][1]
            status = item['values'][4]
            
            if status != "在售":
                messagebox.showinfo("提示", "只能下架在售商品")
                return
            
            if messagebox.askyesno("确认", f"确定要下架商品「{goods_name}」吗？"):
                result = self.network_client.remove_goods(goods_id)
                if result['success']:
                    messagebox.showinfo("成功", "商品已下架")
                    win.destroy()
                    self.my_goods_window()
                else:
                    messagebox.showerror("失败", result.get('message', '下架失败'))
        
        tb.Button(btn_frame, text="下架选中", bootstyle="danger", 
                 command=remove_selected).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="刷新", bootstyle="info", 
                 command=lambda: [win.destroy(), self.my_goods_window()]).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="关闭", bootstyle="secondary", 
                 command=win.destroy).pack(side=RIGHT, padx=5)

    def my_orders_window(self):
        """我的订单窗口"""
        win = tb.Toplevel(self.root)
        win.title("我的订单")
        win.geometry("900x600")
        self.center_window(win)
        
        # 标题
        header = tb.Frame(win, padding=15, bootstyle="warning")
        header.pack(fill=X)
        tb.Label(header, text="📋 我的订单", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-warning").pack(side=LEFT)
        
        # 表格
        table_frame = tb.Frame(win, padding=10)
        table_frame.pack(fill=BOTH, expand=True)
        
        cols = ("订单号", "商品名称", "价格", "买家", "卖家", "状态", "时间")
        tree = tb.Treeview(table_frame, columns=cols, show="headings")
        
        widths = {"订单号": 80, "商品名称": 180, "价格": 80, 
                 "买家": 100, "卖家": 100, "状态": 80, "时间": 150}
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=widths.get(col, 100))
        
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 加载数据
        result = self.network_client.get_user_orders(self.current_user['user_id'])
        if result['success']:
            status_map = {"pending": "待处理", "completed": "已完成", "cancelled": "已取消"}
            for order in result['orders']:
                tree.insert("", "end", values=(
                    order['order_id'],
                    order['goods_name'],
                    f"¥{order['price']:.2f}",
                    order['buyer_name'],
                    order['seller_name'],
                    status_map.get(order['status'], order['status']),
                    order['create_time']
                ))
        
        # 关闭按钮
        tb.Button(win, text="关闭", bootstyle="secondary", 
                 command=win.destroy).pack(pady=10)

    def buy_goods(self):
        """购买商品"""
        sel = self.goods_tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选择要购买的商品")
            return
        
        item = self.goods_tree.item(sel[0])
        goods_id = item['values'][0]
        name = item['values'][1]
        price = float(item['values'][3].replace('¥', ''))
        
        # 获取商品详情确认卖家
        all_goods = self.network_client.get_all_goods()['goods']
        target_goods = next((g for g in all_goods if g['goods_id'] == goods_id), None)
        
        if not target_goods:
            messagebox.showerror("错误", "商品不存在")
            return
        
        if target_goods['seller_id'] == self.current_user['user_id']:
            messagebox.showwarning("提示", "不能购买自己发布的商品")
            return
        
        if messagebox.askyesno("确认购买", 
                              f"商品：{name}\n价格：¥{price:.2f}\n\n确认购买吗？"):
            result = self.network_client.purchase_goods(goods_id, self.current_user['user_id'])
            
            # 检查是否被强制退出
            if self.check_force_logout(result):
                return
                
            if result['success']:
                messagebox.showinfo("成功", "购买成功！")
                self.refresh_goods_list()
                self.refresh_balance()
            else:
                messagebox.showerror("失败", result['message'])

    def recharge_window(self):
        """充值窗口"""
        win = tb.Toplevel(self.root)
        win.title("账户充值")
        win.geometry("400x350")
        self.center_window(win)
        
        frame = tb.Frame(win, padding=30)
        frame.pack(fill=BOTH, expand=True)
        
        tb.Label(frame, text="💰 账户充值", 
                font=("微软雅黑", 18, "bold"), 
                bootstyle="warning").pack(pady=(0, 30))
        
        # 当前余额
        current_balance = self.get_current_balance()
        tb.Label(frame, text=f"当前余额：¥{current_balance:.2f}", 
                font=("微软雅黑", 11)).pack(pady=(0, 20))
        
        # 充值金额
        tb.Label(frame, text="充值金额 (¥)", 
                font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        amount_entry = tb.Entry(frame, font=("微软雅黑", 12))
        amount_entry.pack(fill=X, pady=(0, 10))
        
        # 快捷金额按钮
        quick_frame = tb.Frame(frame)
        quick_frame.pack(fill=X, pady=(0, 20))
        
        for amt in [10, 50, 100, 200]:
            tb.Button(quick_frame, text=f"¥{amt}", bootstyle="info-outline",
                     command=lambda a=amt: amount_entry.delete(0, END) or amount_entry.insert(0, str(a))
                     ).pack(side=LEFT, padx=5, expand=True, fill=X)
        
        def submit_recharge():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的充值金额")
                return
            
            result = self.network_client.recharge_balance(
                self.current_user['user_id'], amount)
            if result['success']:
                messagebox.showinfo("成功", f"充值成功！\n{result['message']}")
                self.refresh_balance()
                win.destroy()
            else:
                messagebox.showerror("失败", result.get('message', '充值失败'))
        
        tb.Button(frame, text="确认充值", bootstyle="success", 
                 command=submit_recharge).pack(fill=X)

    def search_goods_window(self):
        """搜索商品窗口"""
        win = tb.Toplevel(self.root)
        win.title("搜索商品")
        win.geometry("400x250")
        self.center_window(win)
        
        frame = tb.Frame(win, padding=25)
        frame.pack(fill=BOTH, expand=True)
        
        tb.Label(frame, text="🔍 搜索商品", 
                font=("微软雅黑", 16, "bold")).pack(pady=(0, 20))
        
        tb.Label(frame, text="商品名称关键词", 
                font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        keyword_entry = tb.Entry(frame, font=("微软雅黑", 10))
        keyword_entry.pack(fill=X, pady=(0, 15))
        
        tb.Label(frame, text="商品类别", 
                font=("微软雅黑", 10)).pack(anchor=W, pady=(0, 5))
        categories = ["全部", "学习资料", "电子产品", "生活用品", "运动器材", "服饰鞋包", "其他"]
        cat_cb = tb.Combobox(frame, values=categories, state="readonly")
        cat_cb.current(0)
        cat_cb.pack(fill=X, pady=(0, 20))
        
        def do_search():
            keyword = keyword_entry.get().strip().lower()
            category = cat_cb.get()
            
            # 清空当前列表
            for item in self.goods_tree.get_children():
                self.goods_tree.delete(item)
            
            # 获取所有商品并过滤
            result = self.network_client.get_all_goods()
            # 接上文 search_goods_window 函数
            if result['success']:
                for goods in result['goods']:
                    # 关键词过滤
                    if keyword and keyword not in goods['name'].lower():
                        continue
                    # 类别过滤
                    if category != "全部" and goods['category'] != category:
                        continue
                    
                    self.goods_tree.insert("", "end", values=(
                        goods['goods_id'],
                        goods['name'],
                        goods['category'],
                        f"¥{goods['price']:.2f}",
                        goods['seller_name'],
                        goods['publish_time']
                    ))
            
            messagebox.showinfo("完成", "搜索完成")
            win.destroy()
        
        tb.Button(frame, text="搜索", bootstyle="primary", 
                 command=do_search).pack(fill=X)

    # =================== 管理员界面 ===================
    
    def admin_main_window(self):
        """管理员主窗口"""
        self.clear_window()
        
        # 顶部
        header = tb.Frame(self.root, bootstyle="dark", padding=15)
        header.pack(fill=X)
        tb.Label(header, text="🔧 系统管理后台", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-dark").pack(side=LEFT)
        tb.Label(header, text=f"管理员: {self.current_user['username']}", 
                font=("微软雅黑", 11), 
                bootstyle="inverse-dark").pack(side=LEFT, padx=20)
        tb.Button(header, text="退出", bootstyle="danger", 
                 command=self.logout).pack(side=RIGHT)
        
        # 仪表盘
        dashboard = tb.Frame(self.root, padding=30)
        dashboard.pack(fill=BOTH, expand=True)
        
        # 统计卡片区
        stats_frame = tb.Frame(dashboard)
        stats_frame.pack(fill=X, pady=(0, 30))
        
        # 获取统计数据
        users_result = self.network_client.get_all_users()
        goods_result = self.network_client.get_all_goods()
        orders_result = self.network_client.get_all_orders()
        
        stats = [
            ("用户数", len(users_result.get('users', [])), "primary"),
            ("商品数", len(goods_result.get('goods', [])), "success"),
            ("订单数", len(orders_result.get('orders', [])), "info"),
        ]
        
        for title, value, color in stats:
            card = tb.Labelframe(stats_frame, text=title, bootstyle=color, padding=20)
            card.pack(side=LEFT, fill=X, expand=True, padx=10)
            tb.Label(card, text=str(value), font=("Arial", 32, "bold"), 
                    bootstyle=color).pack()
        
        # 功能按钮区
        tb.Label(dashboard, text="管理功能", 
                font=("微软雅黑", 14, "bold")).pack(anchor=W, pady=(20, 15))
        
        btn_grid = tb.Frame(dashboard)
        btn_grid.pack(fill=X)
        
        actions = [
            ("👥 用户管理", "primary", self.manage_users_window),
            ("📦 商品管理", "info", self.manage_goods_window),
            ("📋 订单管理", "success", self.manage_all_orders_window),
            ("📊 数据看板", "warning", self.show_statistics_window),
            ("🎲 生成测试数据", "danger", self.generate_mock_data_window),
        ]
        
        for i, (text, style, cmd) in enumerate(actions):
            btn = tb.Button(btn_grid, text=text, bootstyle=style, 
                           width=18, command=cmd)
            btn.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="ew")
        
        for i in range(3):
            btn_grid.grid_columnconfigure(i, weight=1)

    def manage_users_window(self):
        """用户管理窗口"""
        win = tb.Toplevel(self.root)
        win.title("用户管理")
        win.geometry("900x600")
        self.center_window(win)
        
        # 标题
        header = tb.Frame(win, padding=15, bootstyle="primary")
        header.pack(fill=X)
        tb.Label(header, text="👥 用户管理", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-primary").pack(side=LEFT)
        
        # 表格
        table_frame = tb.Frame(win, padding=10)
        table_frame.pack(fill=BOTH, expand=True)
        
        cols = ("ID", "用户名", "角色", "联系方式", "余额", "注册时间")
        tree = tb.Treeview(table_frame, columns=cols, show="headings")
        
        tree.column("ID", width=50)
        widths = {"用户名": 120, "角色": 80, "联系方式": 150, "余额": 100, "注册时间": 150}
        for col in cols:
            tree.heading(col, text=col)
            if col in widths:
                tree.column(col, width=widths[col])
        
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 加载数据
        result = self.network_client.get_all_users()
        if result['success']:
            role_map = {"user": "普通用户", "admin": "管理员"}
            for user in result['users']:
                tree.insert("", "end", values=(
                    user['user_id'],
                    user['username'],
                    role_map.get(user['role'], user['role']),
                    user.get('contact', ''),
                    f"¥{user.get('balance', 0):.2f}",
                    user['created_at']
                ))
        
        # 操作按钮
        btn_frame = tb.Frame(win, padding=10)
        btn_frame.pack(fill=X)
        
        def delete_user():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("提示", "请选择要删除的用户")
                return
            
            item = tree.item(sel[0])
            user_id = item['values'][0]
            username = item['values'][1]
            role = item['values'][2]
            
            if role == "管理员":
                messagebox.showwarning("提示", "不能删除管理员账户")
                return
            
            if messagebox.askyesno("确认", f"确定要删除用户「{username}」吗？\n此操作将同时删除该用户的商品和订单"):
                result = self.network_client.delete_user(user_id)
                if result['success']:
                    messagebox.showinfo("成功", result['message'])
                    win.destroy()
                    self.manage_users_window()
                else:
                    messagebox.showerror("失败", result.get('message', '删除失败'))
        
        tb.Button(btn_frame, text="删除选中", bootstyle="danger", 
                 command=delete_user).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="刷新", bootstyle="info", 
                 command=lambda: [win.destroy(), self.manage_users_window()]).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="关闭", bootstyle="secondary", 
                 command=win.destroy).pack(side=RIGHT, padx=5)

    def manage_goods_window(self):
        """商品管理窗口"""
        win = tb.Toplevel(self.root)
        win.title("商品管理")
        win.geometry("1000x600")
        self.center_window(win)
        
        # 标题
        header = tb.Frame(win, padding=15, bootstyle="info")
        header.pack(fill=X)
        tb.Label(header, text="📦 商品管理", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-info").pack(side=LEFT)
        
        # 表格
        table_frame = tb.Frame(win, padding=10)
        table_frame.pack(fill=BOTH, expand=True)
        
        cols = ("ID", "名称", "类别", "价格", "卖家", "状态", "发布时间")
        tree = tb.Treeview(table_frame, columns=cols, show="headings")
        
        tree.column("ID", width=50)
        widths = {"名称": 200, "类别": 100, "价格": 100, "卖家": 120, "状态": 80, "发布时间": 150}
        for col in cols:
            tree.heading(col, text=col)
            if col in widths:
                tree.column(col, width=widths[col])
        
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 加载所有商品
        result = self.network_client.get_all_goods()
        if result['success']:
            status_map = {"available": "在售", "sold": "已售", "removed": "已下架"}
            for goods in result['goods']:
                tree.insert("", "end", values=(
                    goods['goods_id'],
                    goods['name'],
                    goods['category'],
                    f"¥{goods['price']:.2f}",
                    goods['seller_name'],
                    status_map.get(goods['status'], goods['status']),
                    goods['publish_time']
                ))
        
        # 操作按钮
        btn_frame = tb.Frame(win, padding=10)
        btn_frame.pack(fill=X)
        
        def remove_goods():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("提示", "请选择要下架的商品")
                return
            
            item = tree.item(sel[0])
            goods_id = item['values'][0]
            goods_name = item['values'][1]
            
            if messagebox.askyesno("确认", f"确定要下架商品「{goods_name}」吗？"):
                result = self.network_client.remove_goods(goods_id)
                if result['success']:
                    messagebox.showinfo("成功", result['message'])
                    win.destroy()
                    self.manage_goods_window()
                else:
                    messagebox.showerror("失败", result.get('message', '下架失败'))
        
        tb.Button(btn_frame, text="下架选中", bootstyle="danger", 
                 command=remove_goods).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="刷新", bootstyle="info", 
                 command=lambda: [win.destroy(), self.manage_goods_window()]).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="关闭", bootstyle="secondary", 
                 command=win.destroy).pack(side=RIGHT, padx=5)

    def manage_all_orders_window(self):
        """订单管理窗口"""
        win = tb.Toplevel(self.root)
        win.title("订单管理")
        win.geometry("1000x600")
        self.center_window(win)
        
        # 标题
        header = tb.Frame(win, padding=15, bootstyle="success")
        header.pack(fill=X)
        tb.Label(header, text="📋 订单管理", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-success").pack(side=LEFT)
        
        # 表格
        table_frame = tb.Frame(win, padding=10)
        table_frame.pack(fill=BOTH, expand=True)
        
        cols = ("订单号", "商品名称", "价格", "买家", "卖家", "状态", "创建时间")
        tree = tb.Treeview(table_frame, columns=cols, show="headings")
        
        widths = {"订单号": 100, "商品名称": 180, "价格": 100, 
                 "买家": 120, "卖家": 120, "状态": 80, "创建时间": 150}
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=widths.get(col, 100))
        
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 加载数据
        result = self.network_client.get_all_orders()
        if result['success']:
            status_map = {"pending": "待处理", "completed": "已完成", "cancelled": "已取消"}
            total_amount = 0
            for order in result['orders']:
                tree.insert("", "end", values=(
                    order['order_id'],
                    order['goods_name'],
                    f"¥{order['price']:.2f}",
                    order['buyer_name'],
                    order['seller_name'],
                    status_map.get(order['status'], order['status']),
                    order['create_time']
                ))
                if order['status'] != 'cancelled':
                    total_amount += order['price']
            
            # 统计信息
            stats_label = tb.Label(win, 
                                  text=f"总订单数: {len(result['orders'])}  |  总交易额: ¥{total_amount:.2f}",
                                  font=("微软雅黑", 10), bootstyle="info")
            stats_label.pack(pady=5)
        
        # 关闭按钮
        tb.Button(win, text="关闭", bootstyle="secondary", 
                 command=win.destroy).pack(pady=10)

    def show_statistics_window(self):
        """数据可视化看板"""
        stats_win = tb.Toplevel(self.root)
        stats_win.title("数据可视化看板")
        stats_win.geometry("1200x700")
        self.center_window(stats_win)
        
        # 标题
        header = tb.Frame(stats_win, padding=15, bootstyle="warning")
        header.pack(fill=X)
        tb.Label(header, text="📊 数据可视化看板", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-warning").pack()
        
        # 获取数据
        cat_res = self.network_client.get_goods_category_stats()
        sales_res = self.network_client.get_daily_sales_stats()
        
        if not cat_res['success'] or not sales_res['success']:
            messagebox.showerror("错误", "获取统计数据失败")
            return
        
        cat_data = cat_res['stats']
        sales_data = sales_res['stats']
        
        # 创建Notebook标签页
        notebook = tb.Notebook(stats_win)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 页面1: 商品类别分布
        tab1 = tb.Frame(notebook)
        notebook.add(tab1, text="商品类别分布")
        
        if cat_data:
            fig1 = plt.Figure(figsize=(10, 6), dpi=100)
            ax1 = fig1.add_subplot(111)
            
            labels = list(cat_data.keys())
            sizes = list(cat_data.values())
            colors = plt.cm.Set3(range(len(labels)))
            
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                startangle=90, colors=colors,
                                                textprops={'fontsize': 10})
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax1.set_title('各类别商品数量分布', fontsize=14, fontweight='bold', pad=20)
            
            canvas1 = FigureCanvasTkAgg(fig1, tab1)
            canvas1.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)
        else:
            tb.Label(tab1, text="暂无商品数据", 
                    font=("微软雅黑", 14)).pack(expand=True)
        
        # 页面2: 交易额趋势
        tab2 = tb.Frame(notebook)
        notebook.add(tab2, text="交易额趋势")
        
        if sales_data:
            fig2 = plt.Figure(figsize=(10, 6), dpi=100)
            ax2 = fig2.add_subplot(111)
            
            dates = [item[0][5:] for item in sales_data]
            amounts = [item[1] for item in sales_data]
            
            bars = ax2.bar(dates, amounts, color='#3498db', alpha=0.8, edgecolor='#2980b9', linewidth=1.5)
            ax2.set_title('近7日交易金额趋势', fontsize=14, fontweight='bold', pad=20)
            ax2.set_xlabel('日期', fontsize=11)
            ax2.set_ylabel('金额 (¥)', fontsize=11)
            ax2.grid(axis='y', alpha=0.3, linestyle='--')
            
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'¥{height:.0f}',
                        ha='center', va='bottom', fontsize=9)
            
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            fig2.tight_layout()
            
            canvas2 = FigureCanvasTkAgg(fig2, tab2)
            canvas2.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)
        else:
            tb.Label(tab2, text="暂无交易数据", 
                    font=("微软雅黑", 14)).pack(expand=True)
        
        # 页面3: 综合统计
        tab3 = tb.Frame(notebook, padding=20)
        notebook.add(tab3, text="综合统计")
        
        users_result = self.network_client.get_all_users()
        goods_result = self.network_client.get_all_goods()
        orders_result = self.network_client.get_all_orders()
        
        stats_data = [
            ("总用户数", len(users_result.get('users', [])), "primary"),
            ("总商品数", len(goods_result.get('goods', [])), "success"),
            ("总订单数", len(orders_result.get('orders', [])), "info"),
            ("总交易额", f"¥{sum(o['price'] for o in orders_result.get('orders', []) if o['status'] != 'cancelled'):.2f}", "warning"),
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            card = tb.Labelframe(tab3, text=title, bootstyle=color, padding=30)
            card.grid(row=i//2, column=i%2, padx=20, pady=20, sticky="ew")
            tb.Label(card, text=str(value), 
                    font=("Arial", 28, "bold"), 
                    bootstyle=color).pack()
        
        tab3.grid_columnconfigure(0, weight=1)
        tab3.grid_columnconfigure(1, weight=1)

    def generate_mock_data_window(self):
        """生成模拟测试数据窗口"""
        win = tb.Toplevel(self.root)
        win.title("生成测试数据")
        win.geometry("700x600")
        self.center_window(win)
        
        # 标题
        header = tb.Frame(win, padding=15, bootstyle="danger")
        header.pack(fill=X)
        tb.Label(header, text="🎲 生成测试数据", 
                font=("微软雅黑", 16, "bold"), 
                bootstyle="inverse-danger").pack()
        
        content = tb.Frame(win, padding=20)
        content.pack(fill=BOTH, expand=True)
        
        # 说明
        info_frame = tb.Labelframe(content, text="功能说明", padding=15, bootstyle="info")
        info_frame.pack(fill=X, pady=(0, 20))
        tb.Label(info_frame, text="此功能用于快速生成虚拟测试数据，包括用户、商品和订单\n便于测试系统功能和数据可视化效果", 
                justify=LEFT, font=("微软雅黑", 9)).pack()
        
        # 配置选项
        config_frame = tb.Labelframe(content, text="生成配置", padding=15)
        config_frame.pack(fill=X, pady=(0, 15))
        
        # 用户数量
        user_frame = tb.Frame(config_frame)
        user_frame.pack(fill=X, pady=5)
        tb.Label(user_frame, text="用户数量:", width=12).pack(side=LEFT)
        user_count = tb.Spinbox(user_frame, from_=1, to=50, value=10, width=10)
        user_count.pack(side=LEFT, padx=10)
        
        # 商品数量
        goods_frame = tb.Frame(config_frame)
        goods_frame.pack(fill=X, pady=5)
        tb.Label(goods_frame, text="商品数量:", width=12).pack(side=LEFT)
        goods_count = tb.Spinbox(goods_frame, from_=1, to=100, value=30, width=10)
        goods_count.pack(side=LEFT, padx=10)
        
        # 订单数量
        order_frame = tb.Frame(config_frame)
        order_frame.pack(fill=X, pady=5)
        tb.Label(order_frame, text="订单数量:", width=12).pack(side=LEFT)
        order_count = tb.Spinbox(order_frame, from_=0, to=100, value=20, width=10)
        order_count.pack(side=LEFT, padx=10)
        
        # 日志区域
        log_frame = tb.Labelframe(content, text="生成日志", padding=10)
        log_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        log_text = tb.Text(log_frame, height=12, font=("Consolas", 9))
        log_scroll = tb.Scrollbar(log_frame, command=log_text.yview)
        log_text.configure(yscrollcommand=log_scroll.set)
        
        log_text.pack(side=LEFT, fill=BOTH, expand=True)
        log_scroll.pack(side=RIGHT, fill=Y)
        
        def log(msg):
            """输出日志"""
            log_text.insert(END, f"{msg}\n")
            log_text.see(END)
            log_text.update()
        
        def start_generate():
            """开始生成数据"""
            import random
            import time
            from datetime import datetime, timedelta
            
            log_text.delete("1.0", END)
            log("=" * 60)
            log("开始生成测试数据...")
            log("=" * 60 + "\n")
            
            try:
                n_users = int(user_count.get())
                n_goods = int(goods_count.get())
                n_orders = int(order_count.get())
                
                # 生成用户
                log(f"[1/3] 生成用户数据 (目标: {n_users}个)")
                user_ids = []
                for i in range(n_users):
                    username = f"user_{random.randint(1000, 9999)}"
                    password = "123456"
                    contact = f"138{random.randint(10000000, 99999999)}"
                    
                    result = self.network_client.register(username, password, contact)
                    if result['success']:
                        # 获取用户ID
                        login_result = self.network_client.login(username, password)
                        if login_result['success']:
                            user_id = login_result['user']['user_id']
                            user_ids.append(user_id)
                            
                            # 随机充值
                            balance = random.randint(100, 5000)
                            self.network_client.recharge_balance(user_id, balance)
                            log(f"  ✓ 创建用户: {username}, 充值: ¥{balance}")
                    time.sleep(0.1)
                
                log(f"  完成! 成功创建 {len(user_ids)} 个用户\n")
                
                # 生成商品
                log(f"[2/3] 生成商品数据 (目标: {n_goods}个)")
                categories = ["学习资料", "电子产品", "生活用品", "运动器材", "服饰鞋包", "其他"]
                goods_names = {
                    "学习资料": ["高等数学", "大学物理", "计算机组成原理", "数据结构", "操作系统"],
                    "电子产品": ["iPhone", "小米手机", "华为平板", "机械键盘", "蓝牙耳机"],
                    "生活用品": ["台灯", "床上四件套", "保温杯", "雨伞", "收纳箱"],
                    "运动器材": ["篮球", "羽毛球拍", "跑步鞋", "瑜伽垫", "哑铃"],
                    "服饰鞋包": ["休闲鞋", "双肩包", "T恤", "牛仔裤", "外套"],
                    "其他": ["书签", "明信片", "手办", "海报", "钥匙扣"]
                }
                
                goods_ids = []
                for i in range(n_goods):
                    if not user_ids:
                        log("  ⚠ 没有可用用户，跳过商品生成")
                        break
                    
                    seller_id = random.choice(user_ids)
                    category = random.choice(categories)
                    name = random.choice(goods_names[category])
                    price = round(random.uniform(10, 500), 2)
                    description = f"闲置转让，{random.choice(['九成新', '全新', '八成新', '七成新'])}"
                    
                    result = self.network_client.add_goods(name, category, price, description, seller_id)
                    if result['success']:
                        goods_ids.append(result['goods_id'])
                        log(f"  ✓ 发布商品: {name} ({category}) - ¥{price}")
                    time.sleep(0.1)
                
                log(f"  完成! 成功发布 {len(goods_ids)} 件商品\n")
                
                # 生成订单
                log(f"[3/3] 生成订单数据 (目标: {n_orders}个)")
                self.refresh_goods_list()
                all_goods = self.network_client.get_all_goods()
                
                if all_goods['success'] and all_goods['goods']:
                    order_success = 0
                    for i in range(min(n_orders, len(all_goods['goods']))):
                        if not user_ids:
                            break
                        
                        goods = random.choice(all_goods['goods'])
                        buyer_id = random.choice([uid for uid in user_ids if uid != goods['seller_id']])
                        
                        result = self.network_client.purchase_goods(goods['goods_id'], buyer_id)
                        if result['success']:
                            order_success += 1
                            log(f"  ✓ 创建订单: {goods['name']} - ¥{goods['price']}")
                        
                        # 重新获取可用商品
                        all_goods = self.network_client.get_all_goods()
                        if not all_goods['goods']:
                            break
                        time.sleep(0.1)
                    
                    log(f"  完成! 成功创建 {order_success} 个订单\n")
                else:
                    log("  ⚠ 没有可用商品，跳过订单生成\n")
                
                log("=" * 60)
                log("数据生成完成!")
                log(f"用户: {len(user_ids)}个 | 商品: {len(goods_ids)}个")
                log("=" * 60)
                
                messagebox.showinfo("完成", "测试数据生成完成!\n请刷新相关页面查看")
                
            except Exception as e:
                log(f"\n❌ 错误: {str(e)}")
                messagebox.showerror("错误", f"生成数据时出错:\n{str(e)}")
        
        # 操作按钮
        btn_frame = tb.Frame(content)
        btn_frame.pack(fill=X)
        
        tb.Button(btn_frame, text="开始生成", bootstyle="success", 
                 command=start_generate).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        tb.Button(btn_frame, text="清空日志", bootstyle="warning-outline", 
                 command=lambda: log_text.delete("1.0", END)).pack(side=LEFT, fill=X, expand=True, padx=5)
        tb.Button(btn_frame, text="关闭", bootstyle="secondary", 
                 command=win.destroy).pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

    # =================== 辅助函数 ===================
    
    def refresh_goods_list(self):
        """刷新商品列表"""
        if not hasattr(self, 'goods_tree'):
            return
        
        if not self.network_client.connected:
            return
        
        for item in self.goods_tree.get_children():
            self.goods_tree.delete(item)
        
        result = self.network_client.get_all_goods()
        if result['success']:
            for goods in result['goods']:
                self.goods_tree.insert("", "end", values=(
                    goods['goods_id'],
                    goods['name'],
                    goods['category'],
                    f"¥{goods['price']:.2f}",
                    goods['seller_name'],
                    goods['publish_time']
                ))

    def get_current_balance(self):
        """获取当前余额"""
        if not self.current_user:
            return 0.0
        result = self.network_client.get_user_balance(self.current_user['user_id'])
        return result.get('balance', 0.0) if result.get('success') else 0.0

    def refresh_balance(self):
        """刷新余额显示"""
        if hasattr(self, 'balance_label'):
            balance = self.get_current_balance()
            self.balance_label.config(text=f"¥{balance:.2f}")

    def check_force_logout(self, response):
        """检查是否需要强制退出"""
        if response.get('force_logout_disconnected'):
            messagebox.showerror("账户已被删除", response.get('message', '您的账户已被管理员删除'))
            self.current_user = None
            self.login_window()
            return True
        return False
        
    def logout(self):
        """退出登录"""
        self.current_user = None
        self.network_client.disconnect()
        self.login_window()

    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SecondHandSystemGUI()
    app.run()