import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# 确保能正确导入同目录下的其他模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solver import TwentyFourSolver
from game_manager import GameManager


class TwentyFourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("24点算法求解器")
        self.root.geometry("700x880")
        self.root.resizable(False, False)
        self.root.configure(bg='#ffffff')

        # 初始化游戏管理器
        self.gm = GameManager()
        self.current_cards = []

        # 设置现代扁平化风格
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 使用clam主题以便自定义颜色

        # 全局背景
        self.style.configure('.', background='#ffffff', font=('微软雅黑', 10))
        self.style.configure('TFrame', background='#ffffff')

        # 标题标签
        self.style.configure('Header.TLabel', font=('微软雅黑', 14, 'bold'), background='#ffffff', foreground='#333333')
        self.style.configure('SubHeader.TLabel', font=('微软雅黑', 11, 'bold'), background='#ffffff',
                             foreground='#4a90e2')

        # 卡牌展示区背景
        self.style.configure('CardArea.TFrame', background='#ffffff', relief='flat')

        # 信息标签
        self.style.configure('Info.TLabel', font=('微软雅黑', 11, 'bold'), background='#ffffff', foreground='#555555')

        # 输入框样式
        self.style.configure('TEntry', fieldbackground='#ffffff', borderwidth=1, relief='solid', padding=5)

        # 按钮样式
        self.style.configure('TButton', font=('微软雅黑', 10), padding=6, relief='flat', background='#e9ecef',
                             foreground='#333333')
        self.style.map('TButton', background=[('active', '#dee2e6')])

        # 主操作按钮 (蓝色)
        self.style.configure('Primary.TButton', font=('微软雅黑', 10, 'bold'), padding=6, relief='flat',
                             background='#4a90e2', foreground='#ffffff')
        self.style.map('Primary.TButton', background=[('active', '#3677c9')])

        # 成功/失败按钮
        self.style.configure('Success.TButton', font=('微软雅黑', 10), padding=6, relief='flat', background='#28a745',
                             foreground='#ffffff')
        self.style.map('Success.TButton', background=[('active', '#218838')])
        self.style.configure('Warning.TButton', font=('微软雅黑', 10), padding=6, relief='flat', background='#ffc107',
                             foreground='#333333')
        self.style.map('Warning.TButton', background=[('active', '#e0a800')])

        # LabelFrame 样式
        self.style.configure('TLabelframe', background='#ffffff', relief='solid', borderwidth=1)
        self.style.configure('TLabelframe.Label', background='#ffffff', foreground='#4a90e2',
                             font=('微软雅黑', 11, 'bold'))

    def setup_ui(self):
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # ================== 顶部：设置 ==================
        setting_frame = ttk.LabelFrame(main_container, text=" ⚙️ 设置 ", padding=15)
        setting_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(setting_frame, text="卡牌数量:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_count = ttk.Entry(setting_frame, width=6, justify='center')
        self.entry_count.insert(0, str(self.gm.card_count))
        self.entry_count.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(setting_frame, text="卡牌最大值:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_max = ttk.Entry(setting_frame, width=6, justify='center')
        self.entry_max.insert(0, str(self.gm.max_value))
        self.entry_max.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(setting_frame, text="目标值:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.entry_target = ttk.Entry(setting_frame, width=6, justify='center')
        self.entry_target.insert(0, str(self.gm.target))
        self.entry_target.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(setting_frame, text="应用设置", style='Primary.TButton', command=self.apply_settings).grid(row=0,
                                                                                                              column=6,
                                                                                                              padx=15,
                                                                                                              pady=5)

        # ================== 中部：求解模式 ==================
        solver_frame = ttk.LabelFrame(main_container, text=" 🧮 求解模式 ", padding=15)
        solver_frame.pack(fill=tk.BOTH, pady=(0, 15), expand=True)

        input_frame = ttk.Frame(solver_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="输入卡牌 (逗号分隔):").pack(side=tk.LEFT)
        self.entry_cards = ttk.Entry(input_frame)
        self.entry_cards.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        ttk.Button(input_frame, text="🔍 开始求解", style='Primary.TButton', command=self.solve_cards).pack(side=tk.LEFT)

        # 结果文本框
        txt_frame = ttk.Frame(solver_frame)
        txt_frame.pack(fill=tk.BOTH, expand=True)

        txt_scroll = ttk.Scrollbar(txt_frame)
        txt_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 设置 state=tk.DISABLED 防止用户编辑，但可选中复制
        self.txt_result = tk.Text(txt_frame, height=6, font=('Consolas', 11), bg='#f8f9fa', relief='flat',
                                  highlightthickness=1, highlightbackground='#dee2e6', highlightcolor='#4a90e2',
                                  yscrollcommand=txt_scroll.set, padx=8, pady=8, state=tk.DISABLED)
        self.txt_result.pack(fill=tk.BOTH, expand=True)
        txt_scroll.config(command=self.txt_result.yview)

        # ================== 底部：互动模式 ==================
        game_frame = ttk.LabelFrame(main_container, text=" 🎮 互动模式 ", padding=15)
        game_frame.pack(fill=tk.BOTH, pady=(0, 15), expand=True)

        # 分数和等级显示 (卡片式)
        score_frame = ttk.Frame(game_frame)
        score_frame.pack(fill=tk.X, pady=(0, 15))

        score_card1 = ttk.Frame(score_frame, style='CardArea.TFrame', relief='solid', borderwidth=1)
        score_card1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.lbl_score = ttk.Label(score_card1, text="当前得分: 0", style='Info.TLabel')
        self.lbl_score.pack(pady=8)

        score_card2 = ttk.Frame(score_frame, style='CardArea.TFrame', relief='solid', borderwidth=1)
        score_card2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.lbl_high = ttk.Label(score_card2, text=f"历史最高: {self.gm.high_score}", style='Info.TLabel')
        self.lbl_high.pack(pady=8)

        score_card3 = ttk.Frame(score_frame, style='CardArea.TFrame', relief='solid', borderwidth=1)
        score_card3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.lbl_level = ttk.Label(score_card3, text="当前等级: 1", style='Info.TLabel')
        self.lbl_level.pack(pady=8)

        # 卡牌动态展示区
        self.card_display_frame = ttk.Frame(game_frame, style='CardArea.TFrame', relief='solid', borderwidth=1)
        self.card_display_frame.pack(fill=tk.X, pady=10, ipady=20)
        self.lbl_cards_placeholder = ttk.Label(self.card_display_frame, text="点击下方按钮开始发牌",
                                               font=('微软雅黑', 12), background='#ffffff', foreground='#999999')
        self.lbl_cards_placeholder.pack(expand=True)

        # 作答输入区
        answer_frame = ttk.Frame(game_frame)
        answer_frame.pack(fill=tk.X, pady=(15, 10))
        self.entry_answer = ttk.Entry(answer_frame, font=('Consolas', 14), justify='center')
        self.entry_answer.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_answer.bind('<Return>', lambda event: self.submit_answer())

        ttk.Button(answer_frame, text="✔ 提交答案", style='Success.TButton', command=self.submit_answer).pack(
            side=tk.LEFT, padx=2)

        # 控制按钮区
        ctrl_frame = ttk.Frame(game_frame)
        ctrl_frame.pack(fill=tk.X)
        self.btn_start = ttk.Button(ctrl_frame, text="🎲 发牌/下一题", style='Primary.TButton', command=self.next_round)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(ctrl_frame, text="🚫 跳过", command=self.next_round).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                            padx=2)
        ttk.Button(ctrl_frame, text="💡 查看解法", style='Warning.TButton', command=self.show_solution).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # 新增：底部解法显示区
        hint_frame = ttk.Frame(game_frame)
        hint_frame.pack(fill=tk.X, pady=(10, 0))

        self.txt_hint = tk.Text(hint_frame, height=1, font=('Consolas', 12), bg='#ffffff', relief='flat',
                                highlightthickness=1, highlightbackground='#ffffff', highlightcolor='#ffffff',
                                padx=10, pady=5, state=tk.DISABLED, wrap=tk.WORD)
        self.txt_hint.pack(fill=tk.X)

    def render_cards(self, cards):
        """动态渲染扑克牌样式的组件"""
        # 清除旧组件
        for widget in self.card_display_frame.winfo_children():
            widget.destroy()

        if not cards:
            self.lbl_cards_placeholder = ttk.Label(self.card_display_frame, text="点击下方按钮开始发牌",
                                                   font=('微软雅黑', 12), background='#ffffff', foreground='#999999')
            self.lbl_cards_placeholder.pack(expand=True)
            return

        # 水平排列卡牌的容器
        cards_row = ttk.Frame(self.card_display_frame, style='CardArea.TFrame')
        cards_row.pack(expand=True)

        for val in cards:
            # 单张卡牌的容器
            card_box = tk.Frame(cards_row, bg='white', bd=0, highlightbackground='#ced4da', highlightthickness=2,
                                relief='flat')
            card_box.pack(side=tk.LEFT, padx=10, pady=5, ipadx=15, ipady=10)

            # 卡牌内容
            val_str = str(val)
            color = '#dc3545' if val in [1, 2, 3] else '#212529'  # 随意加点花色：前三个红色，其余黑色

            lbl_val = tk.Label(card_box, text=val_str, font=('Arial', 28, 'bold'), fg=color, bg='white')
            lbl_val.pack()

            # 扑克牌角标
            lbl_corner = tk.Label(card_box, text=val_str, font=('Arial', 10), fg=color, bg='white')
            lbl_corner.place(x=3, y=0)

    def apply_settings(self):
        """应用拓展模式设置"""
        try:
            count = int(self.entry_count.get())
            max_val = int(self.entry_max.get())
            target = int(self.entry_target.get())

            if count < 2 or count > 7:
                raise ValueError("卡牌数量建议在 2-7 之间")
            if max_val < 1:
                raise ValueError("卡牌最大值必须大于 0")

            self.gm.card_count = count
            self.gm.max_value = max_val
            self.gm.target = target

            messagebox.showinfo("成功", f"设置已更新:\n卡牌数={count}\n最大值={max_val}\n目标值={target}")
            self.render_cards([])  # 清空卡牌区
            self.update_hint("")  # 清空提示区

        except ValueError as e:
            messagebox.showerror("输入错误", f"请输入有效的正整数:\n{str(e)}")

    def solve_cards(self):
        """执行自动求解"""
        input_str = self.entry_cards.get().strip()
        if not input_str:
            return

        try:
            # 支持输入数字和字母
            card_map = {'A': 1, 'J': 11, 'Q': 12, 'K': 13}
            cards = []
            for x in input_str.split(','):
                x = x.strip().upper()
                if x in card_map:
                    cards.append(card_map[x])
                else:
                    cards.append(float(x) if '.' in x else int(x))

            # 使用当前设置的目标值
            target = int(self.entry_target.get())
            solutions = self.gm.solver.solve(cards, target, find_all=True)

            # 解锁文本框进行写入
            self.txt_result.config(state=tk.NORMAL)
            self.txt_result.delete(1.0, tk.END)

            if solutions:
                unique_sols = sorted(list(set(solutions)))
                self.txt_result.insert(tk.END, f"✅ 共找到 {len(unique_sols)} 种解法 (目标: {target}):\n\n", 'title')
                for s in unique_sols:
                    self.txt_result.insert(tk.END, f"{s} = {target}\n")
            else:
                self.txt_result.insert(tk.END, f"❌ 无法凑成 {target} 点")

            # 写入完成，重新上锁防止用户编辑
            self.txt_result.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("错误", f"输入格式有误:\n{str(e)}")

    def next_round(self):
        """开始下一题"""
        self.current_cards = self.gm.generate_valid_cards()
        self.render_cards(self.current_cards)
        self.entry_answer.delete(0, tk.END)
        self.update_hint("")  # 清空底部解法提示
        self.update_score_display()

    def submit_answer(self):
        """提交互动模式答案"""
        if not self.current_cards:
            messagebox.showwarning("提示", "请先点击【发牌开始】")
            return

        ans = self.entry_answer.get().strip()
        if not ans:
            return

        success, msg = self.gm.check_answer(self.current_cards, ans)

        if success:
            self.update_hint(f"🎉 {msg}")
            self.gm.level_up()
            self.next_round()
        else:
            self.update_hint(f"❌ {msg}")

    def show_solution(self):
        """在底部直接显示当前题目的解法"""
        if not self.current_cards:
            self.update_hint("⚠️ 请先发牌！")
            return

        target = int(self.entry_target.get())
        sols = self.gm.solver.solve(self.current_cards, target, find_all=False)
        if sols:
            self.update_hint(f"💡 参考解法: {sols[0]} = {target}")
        else:
            self.update_hint("💡 本题无解 (系统出题异常)")

    def update_hint(self, text):
        """更新底部的解法/提示框"""
        self.txt_hint.config(state=tk.NORMAL)
        self.txt_hint.delete(1.0, tk.END)
        self.txt_hint.insert(tk.END, text)
        self.txt_hint.config(state=tk.DISABLED)

    def update_score_display(self):
        """刷新分数和等级显示"""
        self.lbl_score.config(text=f"当前得分: {self.gm.current_score}")
        self.lbl_high.config(text=f"历史最高: {self.gm.high_score}")
        self.lbl_level.config(text=f"当前等级: {self.gm.level}")


if __name__ == '__main__':
    root = tk.Tk()
    app = TwentyFourApp(root)
    root.mainloop()