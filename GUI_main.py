from tkinter import *
from tkinter import ttk
import tkinter as tk

window = tk.Tk()
window.title('Control panel')
window.geometry('700x380')

text = tk.Label(window, text = '管理者介面', font = ('Arial', 18), height = 3)
text.pack()

task = tk.Label(window, text = '請選擇任務類型 :', font = ('Arial', 12))
task.place(x = 30, y = 100)

task_com = ttk.Combobox(window, height = 5, values = ['圖片命名作業 : Group1', '圖片命名作業 : Group2', '圖片命名作業 : Group3', '詞彙心像作業 : Group1', '詞彙心像作業 : Group2'])
task_com.place(x = 160, y = 101)
task_com.current(0)

amount = tk.Label(window, text = '請選擇圖片張數 :', font = ('Arial', 12))
amount.place(x = 360, y = 100)

amount_com = ttk.Combobox(window, values = ['300'])
amount_com.place(x = 490, y = 101)
amount_com.current(0)

on_click = False
def start_act() :
    global on_click
    if on_click == False :
        on_click = True
        print('System on')

photo = PhotoImage(file = r"C:\Users\chris\web_project\Tkinter_GUI\source\play.png")
on_photo = photo.subsample(13, 13)
start = tk.Button(window, text = '  ON ', font =('Verdana', 20), image = on_photo, height = 50, width = 130, compound = LEFT, command = start_act).pack(side = tk.LEFT, padx = 130)

on_click2 = False
def stop_act() :
    global on_click2
    if on_click2 == False :
        on_click2 = True
        print('System off')

photo2 = PhotoImage(file = r"C:\Users\chris\web_project\Tkinter_GUI\source\stop.png")
off_photo = photo2.subsample(13, 13)
stop = tk.Button(window, text = ' OFF ', font =('Verdana', 20), image = off_photo, height = 50, width = 130, compound = LEFT, command = stop_act).pack(side = tk.LEFT)



window.mainloop()