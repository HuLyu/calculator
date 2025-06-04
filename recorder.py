import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# 数据库初始化
conn = sqlite3.connect("trades.db")
c = conn.cursor()
c.execute(
    """
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL
)
"""
)
conn.commit()


# 添加交易记录函数
def add_trade(event=None):
    try:
        amount = float(entry_amount.get())
    except ValueError:
        messagebox.showerror("输入错误", "请输入有效数字")
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO trades (date, amount) VALUES (?, ?)", (timestamp, amount))
    conn.commit()
    entry_amount.delete(0, tk.END)
    update_view()


# 刷新视图函数
def update_view():
    # 清空表格内容
    for item in tree_daily.get_children():
        tree_daily.delete(item)
    for item in tree_all.get_children():
        tree_all.delete(item)

    # 查询每日盈亏汇总
    c.execute(
        "SELECT substr(date,1,10) as day, SUM(amount)"
        " FROM trades GROUP BY day ORDER BY day"
    )
    for day, total in c.fetchall():
        tree_daily.insert("", "end", values=(day, f"{total:.2f}"))

    # 查询所有交易记录
    c.execute("SELECT date, amount FROM trades ORDER BY date")
    for ts, amt in c.fetchall():
        tree_all.insert("", "end", values=(ts, f"{amt:.2f}"))

    # 总盈亏
    c.execute("SELECT SUM(amount) FROM trades")
    overall = c.fetchone()[0] or 0.0
    label_overall.config(text=f"总盈亏: {overall:.2f}")


# 界面搭建函数
def setup_ui():
    root = tk.Tk()
    root.title("交易记事本")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack()

    # 输入区
    tk.Label(frame, text="输入每笔交易盈亏:").grid(row=0, column=0, sticky="w")
    global entry_amount
    entry_amount = tk.Entry(frame)
    entry_amount.grid(row=0, column=1, padx=5)
    entry_amount.bind("<Return>", add_trade)
    btn_add = tk.Button(frame, text="添加交易", command=add_trade)
    btn_add.grid(row=0, column=2, padx=5)

    # 每日盈亏汇总表格
    tk.Label(frame, text="每日盈亏汇总:").grid(
        row=1, column=0, columnspan=3, sticky="w", pady=(10, 0)
    )
    global tree_daily
    tree_daily = ttk.Treeview(
        frame, columns=("日期", "日总额"), show="headings", height=5
    )
    tree_daily.heading("日期", text="日期")
    tree_daily.heading("日总额", text="日总额")
    tree_daily.grid(row=2, column=0, columnspan=3, pady=5)

    # 所有交易记录表格
    tk.Label(frame, text="所有交易记录:").grid(
        row=3, column=0, columnspan=3, sticky="w", pady=(10, 0)
    )
    global tree_all
    tree_all = ttk.Treeview(frame, columns=("时间", "金额"), show="headings", height=8)
    tree_all.heading("时间", text="时间")
    tree_all.heading("金额", text="金额")
    tree_all.grid(row=4, column=0, columnspan=3, pady=5)

    # 总盈亏标签
    global label_overall
    label_overall = tk.Label(frame, text="总盈亏: 0.00")
    label_overall.grid(row=5, column=0, columnspan=3, pady=(10, 0))

    # 初始化视图
    update_view()
    root.mainloop()
    conn.close()


if __name__ == "__main__":
    setup_ui()
