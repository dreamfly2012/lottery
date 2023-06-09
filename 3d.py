import tkinter as tk
from tkinter import ttk


ws = tk.Tk()
ws.title('3d分析器')
ws.geometry('800x1200')
ws['bg'] = '#AC99F2'


frame = tk.Frame(ws)
frame.pack(pady=20)

# labels
my_label = tk.Label(frame, text="最近10期数据")


my_label.grid(row=0, column=0)

game_frame = tk.Frame(ws)
game_frame.pack()

# scrollbar
game_scroll = tk.Scrollbar(game_frame)
game_scroll.pack(side=tk.RIGHT, fill=tk.Y)

game_scroll = tk.Scrollbar(game_frame, orient='horizontal')
game_scroll.pack(side=tk.BOTTOM, fill=tk.X)

my_game = ttk.Treeview(
    game_frame, yscrollcommand=game_scroll.set, xscrollcommand=game_scroll.set)


my_game.pack()

game_scroll.config(command=my_game.yview)
game_scroll.config(command=my_game.xview)

# define our column

my_game['columns'] = ('qihao', 'bai', 'shi', 'ge')

# format our column
my_game.column("#0", width=0,  stretch=tk.NO)
my_game.column("qihao", anchor=tk.CENTER, width=80)
my_game.column("bai", anchor=tk.CENTER, width=80)
my_game.column("shi", anchor=tk.CENTER, width=80)
my_game.column("ge", anchor=tk.CENTER, width=80)


# Create Headings
my_game.heading("#0", text="", anchor=tk.CENTER)
my_game.heading("qihao", text="期号", anchor=tk.CENTER)
my_game.heading("bai", text="百位", anchor=tk.CENTER)
my_game.heading("shi", text="十位", anchor=tk.CENTER)
my_game.heading("ge", text="个位", anchor=tk.CENTER)


# add data
my_game.insert(parent='', index='end', text='',
               values=('2023119', '1', '1', '2'))
my_game.insert(parent='', index='end', text='',
               values=('2023120', '1', '9', '2'))
my_game.insert(parent='', index='end', text='',
               values=('2023121', '4', '1', '2'))
my_game.insert(parent='', index='end', text='',
               values=('2023122', '5', '5', '8'))
my_game.insert(parent='', index='end', text='',
               values=('2023123', '1', '1', '2'))
my_game.insert(parent='', index='end', text='',
               values=('2023124', '7', '1', '4'))
my_game.insert(parent='', index='end', text='',
               values=('2023125', '1', '1', '2'))
my_game.insert(parent='', index='end',  text='',
               values=('2023125', '1', '1', '2'))
my_game.insert(parent='', index='end',  text='',
               values=('2023125', '1', '1', '2'))
my_game.insert(parent='', index='end',  text='',
               values=('2023125', '1', '1', '2'))
my_game.insert(parent='', index='end',  text='',
               values=('2023125', '1', '1', '2'))


my_game.pack()

frame = tk.Frame(ws)
frame.pack(pady=20)

# labels
qihao_label = tk.Label(frame, text="qihao")
qihao_label.grid(row=0, column=0)

bai_label = tk.Label(frame, text="bai")
bai_label.grid(row=0, column=1)

shi_label = tk.Label(frame, text="shi")
shi_label.grid(row=0, column=2)

ge_label = tk.Label(frame, text="ge")
ge_label.grid(row=0, column=3)


# Entry boxes
qihao_entry = tk.Entry(frame)
qihao_entry.grid(row=1, column=0)

bai_entry = tk.Entry(frame)
bai_entry.grid(row=1, column=1)

shi_entry = tk.Entry(frame)
shi_entry.grid(row=1, column=2)

ge_entry = tk.Entry(frame)
ge_entry.grid(row=1, column=3)

# Select Record


def select_record():
    # clear entry boxes
    qihao_entry.delete(0, tk.END)
    bai_entry.delete(0, tk.END)
    shi_entry.delete(0, tk.END)
    ge_entry.delete(0, tk.END)

    # grab record
    selected = my_game.focus()
    # grab record values
    values = my_game.item(selected, 'values')
    # temp_label.config(text=selected)

    # output to entry boxes
    qihao_entry.insert(0, values[0])
    bai_entry.insert(0, values[1])
    shi_entry.insert(0, values[2])
    ge_entry.insert(0, values[3])

# save Record


def update_record():
    selected = my_game.focus()
    # save new data
    my_game.item(selected, text="", values=(qihao_entry.get(),
                 bai_entry.get(), shi_entry.get(), ge_entry.get()))

    # clear entry boxes
    qihao_entry.delete(0, tk.END)
    shi_entry.delete(0, tk.END)
    bai_entry.delete(0, tk.END)
    ge_entry.delete(0, tk.END)


def refresh_record():
    pass


# Buttons
select_button = tk.Button(ws, text="Select Record", command=select_record)
select_button.pack(pady=10)

refresh_button = tk.Button(ws, text="Update Record", command=update_record)
refresh_button.pack(pady=10)

temp_label = tk.Button(ws, text="Refresh Record", command=refresh_record)
temp_label.pack()

# 走势图

# 3d历史数据
data = [
    [2003001, '2003-02-23', 9, 0, 3],
    [2003002, '2003-02-26', 1, 5, 7],
    [2003003, '2003-02-27', 4, 4, 6],
    [2003004, '2003-02-28', 6, 4, 7],
    [2003005, '2003-03-01', 7, 4, 2],
    [2003006, '2003-03-02', 0, 9, 0],
    [2003007, '2003-03-03', 2, 3, 0],
    [2003008, '2003-03-04', 8, 1, 9],
    [2003009, '2003-03-05', 7, 0, 2],
    [2003010, '2003-03-06', 4, 3, 4],
    # 省略部分数据
]

canvas = tk.Canvas(ws, width=650, height=400)
canvas.pack()

# 绘制标题
canvas.create_text(300, 50, text='3d最近10期走势图', font=('Arial', 24), fill='blue')

# 绘制网格线
# 百位
for i in range(10):
    canvas.create_text(30 + i*20, 110, text=str(0+i),
                       font=('Arial', 12), fill='black')
# 十位
for i in range(10):
    canvas.create_text(30 + 200 + i*20, 110, text=str(0+i),
                       font=('Arial', 12), fill='black')
# 个位
for i in range(10):
    canvas.create_text(30 + 400 + i*20, 110, text=str(0+i),
                       font=('Arial', 12), fill='black')

# Horizontal
for i in range(1, 32):
    x = i * 20
    canvas.create_line(x, 100, x, 550, width=1, fill='gray')

# Vertical
for i in range(1, 15):
    y = 100 + i * 20
    canvas.create_line(20, y, 620, y, width=1, fill='gray')

# 绘制中奖数据
fill_color = 'red'
column = len(data)

for i in range(column):
    # draw bai
    x = 20 + data[i][2] * 20
    y = 120 + i * 20
    # shape
    canvas.create_oval(x, y, x + 16, y + 16, fill=fill_color)
    # text
    canvas.create_text(x + 8, y + 10, text=str(
        data[i][2]), font=('Arial', 12), fill='white')
    # draw shi
    x = 20 + 200 + data[i][3] * 20
    y = 120 + i * 20
    canvas.create_oval(x, y, x + 16, y + 16, fill=fill_color)

    # text
    canvas.create_text(x + 8, y + 10, text=str(
        data[i][2]), font=('Arial', 12), fill='white')
    # draw ge
    x = 20 + 400 + data[i][4] * 20
    y = 120 + i * 20
    canvas.create_oval(x, y, x + 16, y + 16, fill=fill_color)
    # text
    canvas.create_text(x + 8, y + 10, text=str(
        data[i][2]), font=('Arial', 12), fill='white')
    # 绘制中奖号码
    # if j == 6:
    #    x = 200
    #    y = 80 + i * 20
    #    canvas.create_text(x, y, text=str(
    #        data[i][j]), font=('Arial', 12), fill='black')


ws.mainloop()
