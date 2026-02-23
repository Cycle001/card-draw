import tkinter as tk
import random
import os
from tkinter import simpledialog, messagebox, filedialog

class CardDrawer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("抽牌程序 - 卡组管理器")
        self.root.geometry("1200x700")  # 增加宽度以适应左右布局
        
        # 初始化卡组管理器
        self.card_groups = []
        self.current_group_index = 0
        self.edit_mode = False
        
        # 编辑模式下选中的卡牌索引
        self.selected_card_indices = []
        
        # 记录每行的卡牌数量（用于自适应布局）
        self.cards_per_row = 13
        
        # 记录每张牌的抽取状态（使用索引而不是卡牌名称）
        self.drawn_indices = []
        self.current_card_index = None
        self.current_card_index = None
        
        # 默认卡组的原始卡牌（用于恢复功能）
        self.default_54_cards = None
        self.default_108_cards = None
        
        # 创建主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # 顶部：卡组管理工具栏
        self.create_group_toolbar(main_frame)
        
        # 创建左右分区的容器
        content_frame = tk.Frame(main_frame)
        content_frame.pack(expand=True, fill=tk.BOTH, pady=(10, 0))
        
        # 左侧：卡牌组显示区域
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 10))
        
        # 右侧：抽牌区域
        right_frame = tk.Frame(content_frame, width=300)  # 设置固定宽度
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # 创建卡牌显示区域（在左侧）
        self.create_card_display(left_frame)
        
        # 创建抽牌区域（在右侧）
        self.create_draw_area(right_frame)
        
        # 初始化默认卡组
        self.initialize_default_groups()
        
        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self.on_window_resize)
        
        self.root.mainloop()
    
    def create_group_toolbar(self, parent):
        """创建卡组管理工具栏"""
        toolbar_frame = tk.Frame(parent, bg="#e0e0e0", relief=tk.RAISED, bd=2)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 卡组选择下拉菜单
        tk.Label(toolbar_frame, text="卡组:", font=("Arial", 10), 
                bg="#e0e0e0").pack(side=tk.LEFT, padx=(10, 5))
        
        self.group_var = tk.StringVar()
        self.group_dropdown = tk.OptionMenu(toolbar_frame, self.group_var, "")
        self.group_dropdown.config(font=("Arial", 10), width=15)
        self.group_dropdown.pack(side=tk.LEFT, padx=5)
        
        # 绑定下拉菜单选择事件
        self.group_var.trace("w", self.on_group_selected)
        
        # 增加卡组按钮
        self.add_group_btn = tk.Button(
            toolbar_frame,
            text="增加卡组",
            command=self.add_card_group,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.add_group_btn.pack(side=tk.LEFT, padx=5)
        
        # 删除卡组按钮
        self.delete_group_btn = tk.Button(
            toolbar_frame,
            text="删除卡组",
            command=self.delete_card_group,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            state="disabled"  # 初始禁用，至少保留一组
        )
        self.delete_group_btn.pack(side=tk.LEFT, padx=5)
        
        # 修改卡组按钮
        self.edit_group_btn = tk.Button(
            toolbar_frame,
            text="修改卡组",
            command=self.enable_edit_mode,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.edit_group_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存卡组按钮（编辑模式下才启用）
        self.save_group_btn = tk.Button(
            toolbar_frame,
            text="保存卡组",
            command=self.save_and_exit_edit_mode,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            state="disabled"  # 初始禁用，仅在编辑模式下启用
        )
        self.save_group_btn.pack(side=tk.LEFT, padx=5)
        
        # 载入卡组按钮
        self.load_group_btn = tk.Button(
            toolbar_frame,
            text="载入卡组",
            command=self.load_card_group,
            font=("Arial", 10),
            bg="#9C27B0",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.load_group_btn.pack(side=tk.LEFT, padx=5)
        
        # 导出卡组按钮
        self.export_group_btn = tk.Button(
            toolbar_frame,
            text="导出卡组",
            command=self.export_card_group,
            font=("Arial", 10),
            bg="#795548",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.export_group_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_label = tk.Label(
            toolbar_frame,
            text="当前: 完整扑克牌组 (54张)",
            font=("Arial", 10, "italic"),
            bg="#e0e0e0",
            fg="#333333"
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def initialize_default_groups(self):
        """初始化默认卡组"""
        # 定义花色顺序：方块>梅花>红心>黑桃
        suits = ['♦', '♣', '♥', '♠']  # 按照要求的顺序
        
        # 定义点数顺序：K>Q>J>10>9>8>7>6>5>4>3>2>A
        ranks = ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']
        
        # 1. 创建一副完整扑克牌组（54张）按指定顺序
        cards_54 = []
        for suit in suits:
            for rank in ranks:
                cards_54.append(f"{rank}{suit}")
        
        # 添加大小王（先小王后大王）
        cards_54.append("小王")
        cards_54.append("大王")
        
        # 保存默认卡组的原始状态（用于恢复）
        self.default_54_cards = cards_54.copy()
        
        # 创建第一副默认卡组
        default_group_54 = {
            "name": "完整扑克牌组",
            "cards": cards_54,
            "is_default": True,
            "is_editable": True  # 现在默认卡组也可以修改
        }
        
        # 2. 创建两副完整扑克牌组（108张）按指定顺序
        cards_108 = []
        for suit in suits:  # 创建两副牌
            for _ in range(2):
                for rank in ranks:
                    cards_108.append(f"{rank}{suit}")
        for _ in range(2):
            cards_108.append("小王")
        for _ in range(2):
            cards_108.append("大王")
        
        # 保存默认卡组的原始状态（用于恢复）
        self.default_108_cards = cards_108.copy()
        
        # 创建第二副默认卡组
        default_group_108 = {
            "name": "两副扑克牌组",
            "cards": cards_108,
            "is_default": True,
            "is_editable": True  # 现在默认卡组也可以修改
        }
        
        # 添加默认卡组
        self.card_groups.append(default_group_54)
        self.card_groups.append(default_group_108)
        self.current_group_index = 0
        
        # 更新下拉菜单
        self.update_group_dropdown()
        
        # 更新卡牌显示
        self.update_card_display_from_group()
    
    def update_group_dropdown(self):
        """更新卡组下拉菜单"""
        menu = self.group_dropdown["menu"]
        menu.delete(0, "end")
        
        # 重新创建所有下拉菜单项
        for i, group in enumerate(self.card_groups):
            name = group["name"]
            if group.get("is_default", False):
                name = f"{name} (默认)"
            
            # 为每个菜单项设置正确的回调函数
            menu.add_command(
                label=name,
                command=lambda idx=i: self.select_group_by_index(idx)
            )
        
        # 设置当前选中的卡组
        self.select_group_by_index(self.current_group_index)
    
    def select_group_by_index(self, index):
        """根据索引选择卡组"""
        if 0 <= index < len(self.card_groups):
            # 设置下拉菜单显示值
            current_group = self.card_groups[index]
            name = current_group["name"]
            if current_group.get("is_default", False):
                name = f"{name} (默认)"
            self.group_var.set(name)
            
            # 更新当前组索引
            self.current_group_index = index
            
            # 清空抽取状态（因为切换卡组）
            self.drawn_indices = []  # 修改
            self.current_card = None
            self.current_card_index = None  # 新增
            
            # 更新卡牌显示
            self.update_card_display_from_group()
            
            # 重置当前状态
            self.reset()
            
            # 更新按钮状态
            self.update_group_buttons_state()
            
            # 更新状态标签
            card_count = len(current_group["cards"])
            self.status_label.config(
                text=f"当前: {current_group['name']} ({card_count}张)"
            )
    
    def on_group_selected(self, *args):
        """当卡组被选中时的处理函数"""
        try:
            # 获取当前下拉菜单显示的值
            selected_value = self.group_var.get()
            
            # 尝试查找对应的卡组索引
            if selected_value:
                # 查找卡组名称对应的索引
                for i, group in enumerate(self.card_groups):
                    name = group["name"]
                    if group.get("is_default", False):
                        name = f"{name} (默认)"
                    
                    if selected_value == name:
                        self.select_group_by_index(i)
                        break
        except Exception as e:
            print(f"切换卡组时出错: {e}")
    
    def update_group_buttons_state(self):
        """更新卡组管理按钮状态"""
        current_group = self.card_groups[self.current_group_index]
        
        # 更新删除按钮状态
        if len(self.card_groups) <= 1:
            self.delete_group_btn.config(state="disabled")
        elif current_group.get("is_default", False):
            self.delete_group_btn.config(state="disabled")
        else:
            self.delete_group_btn.config(state="normal")
        
        # 更新修改按钮状态
        if current_group.get("is_editable", True) == False:
            self.edit_group_btn.config(state="disabled")
        else:
            self.edit_group_btn.config(state="normal")
    
    def add_card_group(self):
        """增加新卡组"""
        # 计算新卡组编号
        default_count = sum(1 for group in self.card_groups if group.get("is_default", False))
        custom_groups = [group for group in self.card_groups if not group.get("is_default", False)]
        
        new_index = len(custom_groups) + 1
        
        # 创建与默认卡组相同的卡牌，按指定顺序
        suits = ['♦', '♣', '♥', '♠']  # 按照要求的顺序
        ranks = ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']  # 按照要求的顺序
        
        cards = []
        for suit in suits:
            for rank in ranks:
                cards.append(f"{rank}{suit}")
        cards.append("小王")
        cards.append("大王")
        
        # 创建新卡组
        new_group = {
            "name": f"自定义卡组 {new_index}",
            "cards": cards.copy(),
            "is_default": False,
            "is_editable": True
        }
        
        self.card_groups.append(new_group)
        self.current_group_index = len(self.card_groups) - 1
        
        # 更新界面
        self.update_group_dropdown()
        self.update_card_display_from_group()
        self.update_group_buttons_state()
        
        messagebox.showinfo("成功", f"已添加新卡组: {new_group['name']}")
    
    def delete_card_group(self):
        """删除当前卡组"""
        current_group = self.card_groups[self.current_group_index]
        
        # 如果当前卡组是默认卡组，不能删除
        if current_group.get("is_default", False):
            messagebox.showwarning("警告", "默认卡组不能删除！")
            return
        
        # 确认删除
        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除卡组 '{current_group['name']}' 吗？"
        )
        
        if confirm:
            # 删除当前卡组
            del self.card_groups[self.current_group_index]
            
            # 如果删除了当前卡组，切换到第一个卡组
            if self.current_group_index >= len(self.card_groups):
                self.current_group_index = 0
            
            # 更新界面
            self.update_group_dropdown()
            self.update_card_display_from_group()
            self.update_group_buttons_state()
            
            messagebox.showinfo("成功", "卡组已删除")
    
    def load_card_group(self):
        """从文件载入卡组"""
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择卡组文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return  # 用户取消了选择
        
        try:
            # 读取文件内容
            cards = []
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    card = line.strip()
                    if card:  # 跳过空行
                        cards.append(card)
            
            if not cards:
                messagebox.showwarning("警告", "文件为空或没有有效的卡牌数据！")
                return
            
            # 询问卡组名称
            file_name = os.path.basename(file_path)
            default_name = os.path.splitext(file_name)[0]
            
            group_name = simpledialog.askstring(
                "卡组名称",
                f"请输入新卡组的名称:",
                initialvalue=default_name
            )
            
            if not group_name or not group_name.strip():
                group_name = default_name
            
            # 创建新卡组
            new_group = {
                "name": group_name.strip(),
                "cards": cards,
                "is_default": False,
                "is_editable": True
            }
            
            self.card_groups.append(new_group)
            self.current_group_index = len(self.card_groups) - 1
            
            # 更新界面
            self.update_group_dropdown()
            self.update_card_display_from_group()
            self.update_group_buttons_state()
            
            messagebox.showinfo("成功", f"已从文件载入卡组: {new_group['name']} ({len(cards)}张牌)")
            
        except Exception as e:
            messagebox.showerror("错误", f"载入文件时出错: {str(e)}")
    
    def export_card_group(self):
        """导出当前卡组到文件"""
        current_group = self.card_groups[self.current_group_index]
        
        if not current_group["cards"]:
            messagebox.showwarning("警告", "当前卡组为空，无法导出！")
            return
        
        # 打开文件保存对话框
        default_name = f"{current_group['name']}.txt"
        file_path = filedialog.asksaveasfilename(
            title="保存卡组文件",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ],
            initialfile=default_name
        )
        
        if not file_path:
            return  # 用户取消了保存
        
        try:
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as file:
                for card in current_group["cards"]:
                    file.write(f"{card}\n")
            
            messagebox.showinfo("成功", f"卡组已成功导出到文件: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出文件时出错: {str(e)}")
    
    def enable_edit_mode(self):
        """进入编辑卡组模式"""
        self.edit_mode = True
        current_group = self.card_groups[self.current_group_index]
        
        # 清空选中的卡牌
        self.selected_card_indices = []
        
        # 更新按钮状态
        self.edit_group_btn.config(state="disabled")
        self.save_group_btn.config(state="normal")
        self.add_group_btn.config(state="disabled")
        self.delete_group_btn.config(state="disabled")
        self.load_group_btn.config(state="disabled")
        self.export_group_btn.config(state="disabled")
        self.draw_button.config(state="disabled")
        self.reset_button.config(state="disabled")
        
        # 更新状态标签
        self.status_label.config(
            text=f"编辑模式: {current_group['name']} - 左键多选，右键菜单"
        )
        
        # 重新创建可编辑的卡牌显示
        self.create_editable_card_display()
        
        # 添加编辑工具栏（包含删除选中按钮）
        self.create_edit_toolbar()
    
    def create_edit_toolbar(self):
        """创建编辑模式下的工具栏"""
        if hasattr(self, 'edit_toolbar_frame'):
            self.edit_toolbar_frame.destroy()
        
        # 创建编辑工具栏框架
        self.edit_toolbar_frame = tk.Frame(self.card_display_parent, bg="#e0e0e0", relief=tk.RAISED, bd=2)
        self.edit_toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        tk.Label(self.edit_toolbar_frame, text="编辑模式", 
                font=("Arial", 10, "bold"), bg="#e0e0e0").pack(side=tk.LEFT, padx=(10, 5))
        
        # 提示标签
        tk.Label(self.edit_toolbar_frame, text="左键多选卡牌，右键打开菜单", 
                font=("Arial", 9), bg="#e0e0e0", fg="#666666").pack(side=tk.LEFT, padx=5)
        
        # 删除选中按钮
        self.delete_selected_btn = tk.Button(
            self.edit_toolbar_frame,
            text="删除选中卡牌",
            command=self.delete_selected_cards,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            state="disabled"  # 初始禁用，没有选中的卡牌
        )
        self.delete_selected_btn.pack(side=tk.LEFT, padx=5)
        
        # 恢复默认按钮（仅当当前卡组是默认卡组时显示）
        current_group = self.card_groups[self.current_group_index]
        if current_group.get("is_default", False):
            self.restore_default_btn = tk.Button(
                self.edit_toolbar_frame,
                text="恢复默认",
                command=self.restore_default_group,
                font=("Arial", 10),
                bg="#FF9800",
                fg="white",
                padx=10,
                pady=5,
                cursor="hand2"
            )
            self.restore_default_btn.pack(side=tk.LEFT, padx=5)
        
        # 已选中数量显示
        self.selection_count_label = tk.Label(
            self.edit_toolbar_frame,
            text="已选中: 0 张",
            font=("Arial", 10),
            bg="#e0e0e0",
            fg="#333333"
        )
        self.selection_count_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def restore_default_group(self):
        """恢复默认卡组到初始状态"""
        current_group = self.card_groups[self.current_group_index]
        
        # 确认恢复
        confirm = messagebox.askyesno(
            "确认恢复",
            f"确定要将卡组 '{current_group['name']}' 恢复到默认状态吗？所有修改都将丢失！"
        )
        
        if confirm:
            # 根据卡组名称恢复相应的默认卡组
            if current_group["name"] == "完整扑克牌组":
                current_group["cards"] = self.default_54_cards.copy()
            elif current_group["name"] == "两副扑克牌组":
                current_group["cards"] = self.default_108_cards.copy()
            
            # 刷新显示
            self.create_editable_card_display()
            
            # 清空选中状态
            self.selected_card_indices = []
            self.update_selection_count()
            self.delete_selected_btn.config(state="disabled")
            
            messagebox.showinfo("成功", "默认卡组已恢复")
    
    def create_editable_card_display(self):
        """创建可编辑的卡牌显示"""
        # 清空现有的卡牌显示
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        
        # 获取当前卡组的卡牌
        current_group = self.card_groups[self.current_group_index]
        cards = current_group["cards"]
        
        # 计算每行显示的卡牌数量
        self.calculate_cards_per_row()
        
        # 创建卡牌显示
        self.editable_card_buttons = []
        
        row_frame = None
        for i, card in enumerate(cards):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            # 每行创建一个框架
            if col == 0:
                row_frame = tk.Frame(self.card_frame, bg="#f0f0f0")
                row_frame.pack(expand=True, fill=tk.X, padx=10, pady=5)
            
            # 创建卡牌编辑按钮
            btn = self.create_editable_card_button(row_frame, card, i)
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.editable_card_buttons.append(btn)
        
        # 添加"添加新卡牌"按钮
        if cards:
            # 计算最后一行剩余的空白位置
            remaining_cards = len(cards) % self.cards_per_row
            if remaining_cards == 0:
                remaining_cards = self.cards_per_row
            empty_slots = self.cards_per_row - remaining_cards
        else:
            empty_slots = self.cards_per_row
        
        add_card_frame = tk.Frame(self.card_frame, bg="#f0f0f0")
        add_card_frame.pack(expand=True, fill=tk.X, padx=10, pady=5)
        
        # 添加空白占位使添加按钮居中
        for _ in range(empty_slots):
            empty_label = tk.Label(add_card_frame, text="", width=6)
            empty_label.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 添加"+"按钮
        add_btn = tk.Button(
            add_card_frame,
            text="+",
            command=self.add_new_card,
            font=("Arial", 14, "bold"),
            width=6,
            height=2,
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        add_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 更新滚动区域
        self.update_canvas_scrollregion()
    
    def create_editable_card_button(self, parent, card, index):
        """创建可编辑的卡牌按钮"""
        # 确定颜色
        if card == "大王":
            color = "red"
        elif card == "小王":
            color = "black"
        elif card.endswith('♥') or card.endswith('♦'):
            color = "red"
        else:
            color = "black"
        
        # 创建按钮框架
        frame = tk.Frame(parent, bg="#f0f0f0")
        
        # 卡牌显示按钮
        card_btn = tk.Button(
            frame,
            text=card,
            font=("Consolas", 10, "bold"),
            width=6,
            height=2,
            bg="white",
            fg=color,
            relief=tk.RAISED,
            bd=1,
            cursor="hand2"
        )
        card_btn.pack()
        
        # 绑定左键点击事件（多选/取消多选）
        card_btn.bind("<Button-1>", lambda e, idx=index: self.select_card_for_editing(idx))
        
        # 绑定右键点击事件（弹出菜单）
        card_btn.bind("<Button-3>", lambda e, idx=index: self.show_card_context_menu(e, idx))
        
        return frame
    
    def select_card_for_editing(self, card_index):
        """在编辑模式下选择/取消选择卡牌"""
        if not self.edit_mode:
            return
        
        if card_index in self.selected_card_indices:
            # 如果已选中，则取消选择
            self.selected_card_indices.remove(card_index)
            # 更新按钮颜色
            self.update_card_button_selection(card_index, False)
        else:
            # 如果未选中，则选中
            self.selected_card_indices.append(card_index)
            # 更新按钮颜色
            self.update_card_button_selection(card_index, True)
        
        # 更新选中计数显示
        self.update_selection_count()
        
        # 更新删除选中按钮状态
        if self.selected_card_indices:
            self.delete_selected_btn.config(state="normal")
        else:
            self.delete_selected_btn.config(state="disabled")
    
    def update_card_button_selection(self, card_index, selected):
        """更新卡牌按钮的选中状态显示"""
        if not hasattr(self, 'editable_card_buttons'):
            return
        
        if 0 <= card_index < len(self.editable_card_buttons):
            card_frame = self.editable_card_buttons[card_index]
            card_btn = card_frame.winfo_children()[0]  # 获取按钮
            
            # 获取卡牌文本以确定颜色
            current_group = self.card_groups[self.current_group_index]
            card = current_group["cards"][card_index]
            
            if card == "大王":
                color = "red"
            elif card == "小王":
                color = "black"
            elif card.endswith('♥') or card.endswith('♦'):
                color = "red"
            else:
                color = "black"
            
            if selected:
                # 选中状态：背景色为黄色，字体颜色不变
                card_btn.config(bg="#FFD700", fg=color)
            else:
                # 未选中状态：恢复正常颜色
                card_btn.config(bg="white", fg=color)
    
    def update_selection_count(self):
        """更新选中卡牌数量显示"""
        if hasattr(self, 'selection_count_label'):
            count = len(self.selected_card_indices)
            self.selection_count_label.config(text=f"已选中: {count} 张")
    
    def show_card_context_menu(self, event, card_index):
        """显示卡牌右键菜单"""
        if not self.edit_mode:
            return
        
        # 创建右键菜单
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # 添加菜单项
        context_menu.add_command(
            label="重命名",
            command=lambda: self.rename_card_by_index(card_index)
        )
        context_menu.add_command(
            label="删除",
            command=lambda: self.delete_card_by_index(card_index)
        )
        context_menu.add_separator()
        context_menu.add_command(label="取消")
        
        # 显示菜单
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # 确保菜单被释放
            context_menu.grab_release()
    
    def rename_card_by_index(self, card_index):
        """通过索引重命名卡牌"""
        current_group = self.card_groups[self.current_group_index]
        current_card = current_group["cards"][card_index]
        
        # 弹出输入对话框
        new_name = simpledialog.askstring(
            "重命名卡牌",
            f"请输入新名称（原名称: {current_card}）:",
            parent=self.root
        )
        
        if new_name and new_name.strip():
            # 更新卡牌名称
            current_group["cards"][card_index] = new_name.strip()
            
            # 刷新显示
            self.create_editable_card_display()
            
            # 清空选中状态
            self.selected_card_indices = []
            self.update_selection_count()
            self.delete_selected_btn.config(state="disabled")
            
            messagebox.showinfo("成功", "卡牌已重命名")
    
    def delete_card_by_index(self, card_index):
        """通过索引删除卡牌"""
        # 确认删除
        confirm = messagebox.askyesno(
            "确认删除",
            "确定要删除这张卡牌吗？"
        )
        
        if confirm:
            current_group = self.card_groups[self.current_group_index]
            
            # 删除卡牌
            del current_group["cards"][card_index]
            
            # 刷新显示
            self.create_editable_card_display()
            
            # 清空选中状态
            self.selected_card_indices = []
            self.update_selection_count()
            self.delete_selected_btn.config(state="disabled")
            
            messagebox.showinfo("成功", "卡牌已删除")
    
    def delete_selected_cards(self):
        """删除选中的卡牌"""
        if not self.selected_card_indices:
            return
        
        # 确认删除
        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除选中的 {len(self.selected_card_indices)} 张卡牌吗？"
        )
        
        if confirm:
            current_group = self.card_groups[self.current_group_index]
            
            # 按从大到小的顺序删除，避免索引变化
            for index in sorted(self.selected_card_indices, reverse=True):
                if 0 <= index < len(current_group["cards"]):
                    del current_group["cards"][index]
            
            # 刷新显示
            self.create_editable_card_display()
            
            # 清空选中状态
            self.selected_card_indices = []
            self.update_selection_count()
            self.delete_selected_btn.config(state="disabled")
            
            messagebox.showinfo("成功", f"已删除 {len(self.selected_card_indices)} 张卡牌")
    
    def add_new_card(self):
        """添加新卡牌"""
        # 弹出输入对话框
        new_card = simpledialog.askstring(
            "添加新卡牌",
            "请输入新卡牌名称（例如: A♥, 大王, 10♣）:",
            parent=self.root
        )
        
        if new_card and new_card.strip():
            current_group = self.card_groups[self.current_group_index]
            
            # 添加新卡牌
            current_group["cards"].append(new_card.strip())
            
            # 刷新显示
            self.create_editable_card_display()
            
            messagebox.showinfo("成功", "新卡牌已添加")
    
    def save_and_exit_edit_mode(self):
        """保存并退出编辑模式"""
        self.edit_mode = False
        
        # 清空选中状态
        self.selected_card_indices = []
        
        # 清空抽取状态（因为卡牌可能被修改）
        self.drawn_indices = []  # 新增
        self.current_card = None
        self.current_card_index = None  # 新增
        
        # 移除编辑工具栏
        if hasattr(self, 'edit_toolbar_frame'):
            self.edit_toolbar_frame.destroy()
        
        # 更新按钮状态
        self.edit_group_btn.config(state="normal")
        self.save_group_btn.config(state="disabled")
        self.add_group_btn.config(state="normal")
        self.delete_group_btn.config(state="normal")
        self.load_group_btn.config(state="normal")
        self.export_group_btn.config(state="normal")
        self.draw_button.config(state="normal")
        self.reset_button.config(state="disabled")  # 重置按钮在未抽取牌时禁用
        
        # 更新组按钮状态
        self.update_group_buttons_state()
        
        # 重新创建正常的卡牌显示
        self.update_card_display_from_group()
        
        # 更新状态标签
        current_group = self.card_groups[self.current_group_index]
        card_count = len(current_group["cards"])
        self.status_label.config(
            text=f"当前: {current_group['name']} ({card_count}张)"
        )
        
        messagebox.showinfo("成功", "卡组修改已保存")
    
    def create_card_display(self, parent):
        """创建卡牌显示区域（带水平和垂直滚动功能）"""
        self.card_display_parent = parent
        
        # 1. 创建主容器框架
        container = tk.Frame(parent)
        container.pack(expand=True, fill=tk.BOTH, pady=(0, 20))
        
        # 标题（不随内容滚动）
        title_label = tk.Label(container,
                            text="所有卡牌（可点击切换状态，灰色表示已抽取）",
                            font=("Arial", 14), pady=10)
        title_label.pack()
        
        # 2. 创建滚动容器框架
        scroll_container = tk.Frame(container)
        scroll_container.pack(expand=True, fill=tk.BOTH)
        
        # 3. 创建滚动条
        self.v_scrollbar = tk.Scrollbar(scroll_container, orient=tk.VERTICAL)
        self.h_scrollbar = tk.Scrollbar(scroll_container, orient=tk.HORIZONTAL)
        
        # 4. 创建画布（同时支持水平和垂直滚动）
        self.canvas = tk.Canvas(scroll_container, 
                            bg="#f0f0f0", 
                            relief=tk.RIDGE, 
                            bd=2,
                            yscrollcommand=self.v_scrollbar.set,
                            xscrollcommand=self.h_scrollbar.set)
        
        # 5. 配置滚动条
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        # 6. 使用grid布局管理器（更好的控制滚动条位置）
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 7. 配置网格权重，使画布可以扩展
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)
        
        # 8. 创建卡牌框架（放在画布中）
        self.card_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas_frame_id = self.canvas.create_window((0, 0), 
                                                        window=self.card_frame, 
                                                        anchor="nw")
        
        # 9. 绑定配置事件，更新滚动区域
        self.card_frame.bind("<Configure>", self._configure_frame)
        
        # 10. 绑定画布大小变化事件
        self.canvas.bind("<Configure>", self._configure_canvas)
        
        # 11. 绑定鼠标滚轮事件（更好的用户体验）
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 绑定滚轮事件到画布
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
    
    def _configure_frame(self, event):
        """更新画布的滚动区域"""
        # 更新画布的滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # 设置卡牌框架的最小宽度与画布可视区域相同
        canvas_width = self.canvas.winfo_width()
        if canvas_width > 0:
            self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
    
    def _configure_canvas(self, event):
        """当画布大小变化时，调整卡牌框架宽度"""
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)
        
        # 窗口大小变化时重新计算卡牌布局
        if self.edit_mode:
            self.create_editable_card_display()
        else:
            self.update_card_display_from_group()
    
    def calculate_cards_per_row(self):
        """计算每行可以显示的卡牌数量"""
        # 计算每行可以显示的卡牌数量（基于窗口宽度）
        # 每个卡牌按钮的宽度大约为80像素，加上内边距
        button_width = 80
        padding = 20
        
        # 获取画布宽度
        if hasattr(self, 'canvas'):
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 0:
                # 计算可以容纳的卡牌数量（至少1张）
                self.cards_per_row = max(1, (canvas_width - padding) // button_width)
            else:
                self.cards_per_row = 13  # 默认值
        else:
            self.cards_per_row = 13  # 默认值
    
    def update_canvas_scrollregion(self):
        """手动更新画布的滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def update_card_display_from_group(self):
        """从当前卡组更新卡牌显示"""
        # 清空现有的卡牌显示
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        
        # 获取当前卡组的卡牌
        current_group = self.card_groups[self.current_group_index]
        cards = current_group["cards"]
        
        # 重置抽取状态
        self.drawn_indices = []  # 修改：使用索引列表
        self.current_card = None
        self.current_card_index = None  # 新增
        
        # 计算每行显示的卡牌数量
        self.calculate_cards_per_row()
        
        # 创建卡牌按钮
        self.card_buttons = []
        row_frame = None
        
        for i, card in enumerate(cards):  # 注意：这里使用了enumerate获取索引
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            # 每行创建一个框架
            if col == 0:
                row_frame = tk.Frame(self.card_frame, bg="#f0f0f0")
                row_frame.pack(expand=True, fill=tk.X, padx=10, pady=5)
            
            # 创建卡牌按钮，传递索引i
            btn = self.create_normal_card_button(row_frame, card, i)  # 传递索引i
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.card_buttons.append({"card": card, "button": btn})
        
        # 更新滚动区域
        self.update_canvas_scrollregion()
    
    def create_normal_card_button(self, parent, card, card_index):
        """创建普通模式下的卡牌按钮"""
        # 确定颜色
        if card == "大王":
            color = "red"
        elif card == "小王":
            color = "black"
        elif card.endswith('♥') or card.endswith('♦'):
            color = "red"
        else:
            color = "black"
        
        # 创建按钮
        btn = tk.Button(
            parent,
            text=card,
            command=lambda idx=card_index: self.toggle_card(idx),  # 使用索引
            font=("Consolas", 12, "bold"),
            width=6,
            height=2,
            relief=tk.RAISED,
            bd=2,
            bg="white",
            fg=color,
            activebackground="#e0e0e0",
            cursor="hand2"
        )
        
        return btn
    
    def on_window_resize(self, event):
        """窗口大小变化时的处理函数"""
        # 仅在宽度变化时重新布局（避免频繁重绘）
        if hasattr(self, 'last_width'):
            if abs(self.last_width - self.root.winfo_width()) > 50:  # 宽度变化超过50像素才重新布局
                if self.edit_mode:
                    self.create_editable_card_display()
                else:
                    self.update_card_display_from_group()
                self.last_width = self.root.winfo_width()
        else:
            self.last_width = self.root.winfo_width()
    
    def toggle_card(self, card_index):
        """切换卡牌状态（点击事件）"""
        if self.edit_mode:
            return  # 编辑模式下禁用切换功能
        
        # 获取当前卡组的所有卡牌
        current_group = self.card_groups[self.current_group_index]
        
        # 确保索引在有效范围内
        if 0 <= card_index < len(current_group["cards"]):
            card = current_group["cards"][card_index]
            
            if card_index in self.drawn_indices:
                # 如果已抽取，则放回
                self.drawn_indices.remove(card_index)
            else:
                # 如果未抽取，则抽取
                self.drawn_indices.append(card_index)
            
            # 设置当前牌为点击的牌
            self.current_card = card
            self.current_card_index = card_index  # 保存当前牌的索引
            
            # 更新当前牌显示
            self.update_current_card_display()
            
            # 更新卡牌按钮显示
            self.update_card_buttons()
            
            # 启用重置按钮（如果有牌被抽取）
            if self.drawn_indices:
                self.reset_button.config(state="normal")
            else:
                self.reset_button.config(state="disabled")
    
    def update_card_buttons(self):
        """更新所有卡牌按钮的显示状态"""
        current_group = self.card_groups[self.current_group_index]
        all_cards = current_group["cards"]
        
        for i, card_info in enumerate(self.card_buttons):
            # 获取卡牌和按钮
            card = all_cards[i] if i < len(all_cards) else ""
            btn = card_info["button"]
            
            # 使用索引判断是否被抽取
            if i in self.drawn_indices:
                # 已抽取的牌：浅灰色
                btn.config(
                    bg="#E0E0E0",
                    fg="#A0A0A0",
                    relief=tk.SUNKEN
                )
            else:
                # 未抽取的牌：恢复正常颜色
                if card == "大王":
                    color = "red"
                elif card == "小王":
                    color = "black"
                elif card.endswith('♥') or card.endswith('♦'):
                    color = "red"
                else:
                    color = "black"
                
                btn.config(
                    bg="white",
                    fg=color,
                    relief=tk.RAISED
                )
    
    def create_draw_area(self, parent):
        """创建抽牌区域（在右侧）"""
        # 创建上下分区的容器
        container = tk.Frame(parent)
        container.pack(expand=True, fill=tk.BOTH)
        
        # 上部分：当前抽到的牌显示
        top_frame = tk.Frame(container, height=300)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 标题
        tk.Label(
            top_frame,
            text="当前抽到的牌",
            font=("Arial", 12, "bold"),
            pady=10
        ).pack()
        
        # 当前牌显示区域
        self.current_card_display = tk.Label(
            top_frame,
            text="等待抽牌...",
            font=("Consolas", 36, "bold"),
            width=8,
            height=4,
            bg="white",
            relief=tk.RIDGE,
            bd=3,
            wraplength=200  # 允许文字换行
        )
        self.current_card_display.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        # 下部分：按钮区域
        bottom_frame = tk.Frame(container)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # 抽牌按钮
        self.draw_button = tk.Button(
            bottom_frame,
            text="随机抽一张牌",
            command=self.draw_random_card,
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=15,
            cursor="hand2",
            relief="raised",
            bd=2
        )
        self.draw_button.pack(fill=tk.X, pady=(0, 10))
        
        # 重置按钮（初始禁用）
        self.reset_button = tk.Button(
            bottom_frame,
            text="重置",
            command=self.reset,
            state="disabled",
            font=("Arial", 14),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=15,
            cursor="hand2",
            relief="raised",
            bd=2
        )
        self.reset_button.pack(fill=tk.X)
    
    def draw_random_card(self):
        """随机抽取一张牌"""
        if self.edit_mode:
            return  # 编辑模式下禁用随机抽牌
        
        # 获取当前卡组的卡牌
        current_group = self.card_groups[self.current_group_index]
        all_cards = current_group["cards"]
        
        # 获取所有未抽取的牌的索引
        available_indices = [i for i in range(len(all_cards)) if i not in self.drawn_indices]
        
        if not available_indices:
            messagebox.showinfo("提示", "所有牌都已被抽取！")
            return  # 如果牌堆为空，直接返回
        
        # 从剩余牌中随机抽取一张
        self.current_card_index = random.choice(available_indices)
        self.current_card = all_cards[self.current_card_index]
        self.drawn_indices.append(self.current_card_index)
        
        # 更新显示
        self.update_current_card_display()
        self.update_card_buttons()
        
        # 启用重置按钮
        self.reset_button.config(state="normal")
        
        # 如果所有牌都被抽取，禁用抽牌按钮
        if len(self.drawn_indices) == len(all_cards):
            self.draw_button.config(state="disabled", bg="#CCCCCC")
            messagebox.showinfo("提示", "所有牌都已被抽取！")
    
    def update_current_card_display(self):
        """更新当前牌显示"""
        if self.current_card:
            # 确定颜色
            if self.current_card == "大王":
                color = "red"
            elif self.current_card == "小王":
                color = "black"
            elif self.current_card.endswith('♥') or self.current_card.endswith('♦'):
                color = "red"
            else:
                color = "black"
            
            self.current_card_display.config(
                text=self.current_card,
                fg=color
            )
        else:
            self.current_card_display.config(text="等待抽牌...", fg="black")
    
    def reset(self):
        """重置所有状态"""
        # 清空已抽取的牌索引
        self.drawn_indices = []
        self.current_card = None
        self.current_card_index = None
        
        # 重置显示
        self.current_card_display.config(text="等待抽牌...", fg="black")
        
        # 重置所有卡牌按钮
        if hasattr(self, 'card_buttons'):
            current_group = self.card_groups[self.current_group_index]
            all_cards = current_group["cards"]
            
            for i, card_info in enumerate(self.card_buttons):
                if i < len(all_cards):
                    card = all_cards[i]
                    btn = card_info["button"]
                    
                    # 恢复正常颜色
                    if card == "大王":
                        color = "red"
                    elif card == "小王":
                        color = "black"
                    elif card.endswith('♥') or card.endswith('♦'):
                        color = "red"
                    else:
                        color = "black"
                    
                    btn.config(
                        bg="white",
                        fg=color,
                        relief=tk.RAISED
                    )
        
        # 重置按钮状态
        if not self.edit_mode:
            self.draw_button.config(state="normal", bg="#4CAF50")
        self.reset_button.config(state="disabled")

# 运行程序
if __name__ == "__main__":
    app = CardDrawer()