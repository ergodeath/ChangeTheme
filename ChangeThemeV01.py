# Расположение программ с автозапуском:
# \HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run

from winregistry import WinRegistry, WinregType
from tkinter import *
from os.path import expanduser, abspath
from os import curdir, chdir
from pystray import MenuItem as item, Icon
from PIL import Image
from datetime import datetime, timedelta
from math import ceil
from sys import argv, exit # sys.argv[0] - Показывает путь/имя файла, даже после компиляции, и даже после смены пути!
from tendo import singleton
# import logging

try:
    me = singleton.SingleInstance()
    print(me)
except:
   exit()  # Чем отличается exit() от quit()???


homedir = expanduser("~") # находим папку нынешнего юзера C:\Users\%username%

tk = Tk()

tk.geometry("400x300")
TEST_REG_PATH = r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
RUN_REG_PATH = r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
client = WinRegistry()
enabled = IntVar()
enabledAutoStart = IntVar()
textVar = StringVar()
textVar2 = StringVar()

try:
    file = open(homedir + "/Documents/change-theme.cfg", "x")
    file.close()
    file = open(homedir + "/Documents/change-theme.cfg", "w")
    file.write("0,20:00,10:00,0")
    file.close()
except:
    pass


# os.path.abspath(__file__) # Получить текущую директорию, где расположен скрипт
# os.path.abspath(os.curdir) # Текущая директория, где запущен скрипт

dirThisfile = abspath(__file__)
ndx = dirThisfile.rfind('\\')
dirThisfile = dirThisfile[:ndx]
print(dirThisfile)



file = open(homedir + "/Documents/change-theme.cfg", "r")
cfg_status = file.read()
file.close()
cfg_status = cfg_status.split(',')

# Иконка для окна
# tk.iconphoto(False, PhotoImage(file=dirThisfile + "\change-theme-icon.jpg"))
tk.iconbitmap(dirThisfile + "\change-theme-icon.ico")

def click():
    global a
    if client.read_entry(TEST_REG_PATH, "SystemUsesLightTheme").value == 0: a = 1
    else: a = 0
    client.write_entry(TEST_REG_PATH, "SystemUsesLightTheme", a, WinregType.REG_DWORD)
    client.write_entry(TEST_REG_PATH, "AppsUseLightTheme", a, WinregType.REG_DWORD)
    cfg_status[0] = '0'
    enabled.set(0)
    
def clickCheck():
    cfg_status[0] = str(enabled.get())
    print(cfg_status[0])
    save()
    
def checkingAutoStart():
    pathExe = argv[0]
    if cfg_status[3] == '1':
        try:
            client.write_entry(RUN_REG_PATH, "ChangeThemeV01", pathExe, WinregType.REG_SZ)
        except:
            pass
    elif cfg_status[3] == '0':
        try:
            client.delete_entry(RUN_REG_PATH, "ChangeThemeV01")
        except:
            pass
    
def clickCheckAuto():
    cfg_status[3] = str(enabledAutoStart.get())
    print(cfg_status[3])
    checkingAutoStart()
    save()
    
def check_txt2():
    cfg_status[2] = txt1.get()
    print(cfg_status[1])
def check_txt1():
    cfg_status[2] = txt2.get()
    
def quit_window(icon, item):
    icon.stop()
    tk.after(0,tk.deiconify)
    tk.quit()
    quit() # Выход из программы Python
    # exit() # Выход из цикла
    

def save():
    cfg_status[1] = textVar.get()
    cfg_status[2] = textVar2.get()
    file = open(homedir + "/Documents/change-theme.cfg", "w")
    file.write(','.join(cfg_status))
    file.close()
    
def show_window(icon, item):
    save()
    timenow()
    icon.stop()
    tk.after(0,tk.deiconify)

def withdraw_window():
    save()
    timenow()
    tk.withdraw()
    image = Image.open(dirThisfile + "\change-theme-icon.jpg")
    menu = (item('Quit', quit_window), item('Show', show_window, default=True))
    icon = Icon("name", image, "title", menu)
    print(Icon.HAS_DEFAULT_ACTION)
    icon.run_detached()
    
def timenow():
    global a
    timer = 600 # 10 минут, далее должно измениться 
    timeNow = datetime.now()
    tm1 = cfg_status[1].split(':')
    tm1 = list(map(int, tm1))
    tm2 = cfg_status[2].split(':')
    tm2 = list(map(int, tm2))
    tm11 = datetime(year=timeNow.year, month=timeNow.month, day=timeNow.day, hour=tm1[0], minute=tm1[1])
    tm22 = datetime(year=timeNow.year, month=timeNow.month, day=timeNow.day, hour=tm2[0], minute=tm2[1])
    # 00:40  00:10
    if cfg_status[0] == '1':
        if timeNow > tm11 and timeNow < tm22:
            print('Можем включить темную тему1')
            # считаем время до отключения темной темы
            timer = datetime.timestamp(tm22) - datetime.timestamp(timeNow)
            a = 0
        elif timeNow > tm11 and timeNow > tm22 and tm11 < tm22:
            print('Включаем светлую тему2')
            a = 1
            # Считаем когда включить темную тему
            tm11 = datetime.now() + timedelta(days=1)
            tm11 = datetime(year=tm11.year, month=tm11.month, day=tm11.day, hour=tm1[0], minute=tm1[1])
            timer = datetime.timestamp(tm11) - datetime.timestamp(timeNow)
        elif timeNow > tm11 and timeNow > tm22 and tm11 > tm22:
            print('Включаем темную тему3')
            a = 0
            # Считаем когда включить светлую тему
            tm22 = datetime.now() + timedelta(days=1)
            tm22 = datetime(year=tm22.year, month=tm22.month, day=tm22.day, hour=tm2[0], minute=tm2[1])
            timer = datetime.timestamp(tm22) - datetime.timestamp(timeNow)
        elif timeNow < tm11 and timeNow > tm22:
            print('Включаем светлую тему4')
            a = 1
            # Считаем когда включить темную тему
            timer = datetime.timestamp(tm11) - datetime.timestamp(timeNow)
        elif timeNow < tm22 and timeNow < tm11 and tm11 < tm22:
            print('Включаем светлую тему5')
            # Посчитать время до выключения темной темы.
            a = 1
            timer = datetime.timestamp(tm11) - datetime.timestamp(timeNow)
        elif timeNow < tm22 and timeNow < tm11 and tm11 > tm22:
            print('Включаем темную тему6')
            a = 0
            timer = datetime.timestamp(tm22) - datetime.timestamp(timeNow)
        client.write_entry(TEST_REG_PATH, "SystemUsesLightTheme", a, WinregType.REG_DWORD)
        client.write_entry(TEST_REG_PATH, "AppsUseLightTheme", a, WinregType.REG_DWORD)
    # Запускаем отсчет времени до следующего запуска timenow
    tk.after(ceil(timer * 1000), timenow)
    Tk.call

if cfg_status[0] == '0':
    enabled.set(0)
else:
    enabled.set(1)
if cfg_status[3] == '0':
    enabledAutoStart.set(0)
else:
    enabledAutoStart.set(1)
check = Checkbutton(text='Смена темы по расписанию', variable=enabled, command=clickCheck)
check.pack()
txt1 = Entry(width=10, textvariable=textVar)
txt2 = Entry(width=10, textvariable=textVar2)
txt1.insert(0, cfg_status[1])
txt2.insert(0, cfg_status[2])
txt1.pack()
txt2.pack()
btn = Button(text="change theme", command=click)
btn.pack()
checkAutoStart = Checkbutton(text='Автозапуск при включении пк', variable=enabledAutoStart, command=clickCheckAuto)
checkAutoStart.pack()

# texttext = Label(text=f"{dirThisfile}, {__file__}, {curdir}, {argv[0]}")
# texttext.pack()
timenow()
checkingAutoStart()
withdraw_window()
tk.protocol('WM_DELETE_WINDOW', withdraw_window)
tk.mainloop()