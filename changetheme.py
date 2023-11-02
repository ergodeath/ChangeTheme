# Скомпилировано с помощью auto-py-to-exe

# Расположение программ с автозапуском:
# \HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run

from winregistry import WinRegistry, WinregType
from tkinter import *
from tkinter import ttk
from os.path import expanduser, abspath
from os import curdir, chdir
from pystray import MenuItem as item, Icon
from PIL import Image
from datetime import datetime, timedelta
from math import ceil
from sys import argv, exit # sys.argv[0] - Показывает путь/имя файла, даже после компиляции, и даже после смены пути!
from tendo import singleton
import requests
# import threading
# import logging

try:
    me = singleton.SingleInstance()
    print(me)
except:
   exit()  # Чем отличается exit() от quit()???


homedir = expanduser("~") # находим папку нынешнего юзера C:\Users\%username%

tk = Tk()
tk.title("Change Theme auto")
tk.geometry("400x300")
TEST_REG_PATH = r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
RUN_REG_PATH = r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

first_run = False
client = WinRegistry()
enabled = IntVar()
enabledAutoStart = IntVar()
textVar = StringVar()
textVar2 = StringVar()

sunsetVar = IntVar()
sunriseVar = IntVar()

cityselected = StringVar()

cities = ['Moscow', 'Petersburg', 'Rostov', 'Great Novgorod', 'Nizhny Novgorod', 'Krasnodar', 'Murmansk', 'Yekaterinburg', 'Novosibirsk', 'Irkutsk', 'Vladivostok']
dict_cities = {'Moscow': (55.75, 37.62), 'Petersburg': (59.94, 30.31), 'Rostov': (57.19, 39.41), 'Great Novgorod': (58.52, 31.27), 'Nizhny Novgorod': (56.33, 44), 'Krasnodar': (45.04, 38.98), 'Murmansk': (68.98, 33.09), 'Yekaterinburg': (56.85, 60.61), 'Novosibirsk': (55.04, 82.93), 'Irkutsk': (52.3, 104.3), 'Vladivostok': (43.11, 131.87)}

# Координаты городов взяты из этого истоничка: https://kakdobratsyado.ru/koordinaty-gorodov-rossii/

try:
    file = open(homedir + "/Documents/change-theme-auto.cfg", "x")
    file.close()
    file = open(homedir + "/Documents/change-theme-auto.cfg", "w")
    file.write("0,20:00,10:00,0,0,0,Moscow")
    file.close()
    client.delete_entry(RUN_REG_PATH, "ChangeThemeV01")
except:
    pass


# os.path.abspath(__file__) # Получить текущую директорию, где расположен скрипт
# os.path.abspath(os.curdir) # Текущая директория, где запущен скрипт

dirThisfile = abspath(__file__)
ndx = dirThisfile.rfind('\\')
dirThisfile = dirThisfile[:ndx]
print(dirThisfile)



file = open(homedir + "/Documents/change-theme-auto.cfg", "r")
cfg_status = file.read()
file.close()
cfg_status = cfg_status.split(',')

# Иконка для окна
# tk.iconphoto(False, PhotoImage(file=dirThisfile + "\change-theme-icon.jpg"))
tk.iconbitmap(dirThisfile + "\change-theme-icon.ico")

def updateSunsetSunrise():
    global sunset_, sunrise_
    if sunsetVar.get() == 1 or sunriseVar.get() == 1:
        sunset_ = check_sun_set_rise().get('sunset')
        sunrise_ = check_sun_set_rise().get('sunrise')

def checking_on_off_first_position():
    if enabled.get() == 1: 
        sunrisefunc()
        sunsetfunc()
        sunset.config(state='normal')
        sunrise.config(state='normal')
        combobox.config(state='readonly')
    else:
        txt1.config(state='disabled')
        txt2.config(state='disabled') 
        sunset.config(state='disabled')
        sunrise.config(state='disabled')
        combobox.config(state='disabled')
        
def changetheme():
    global a
    if client.read_entry(TEST_REG_PATH, "SystemUsesLightTheme").value == 0: a = 1
    else: a = 0
    client.write_entry(TEST_REG_PATH, "SystemUsesLightTheme", a, WinregType.REG_DWORD)
    client.write_entry(TEST_REG_PATH, "AppsUseLightTheme", a, WinregType.REG_DWORD)
    cfg_status[0] = '0'
    enabled.set(0)
    checking_on_off_first_position()
    
def clickCheck():
    cfg_status[0] = str(enabled.get())
    print(cfg_status[0])
    checking_on_off_first_position() 
    
def checkingAutoStart():
    pathExe = argv[0]
    if cfg_status[3] == '1':
        try:
            client.write_entry(RUN_REG_PATH, "ChangeTheme_auto", pathExe, WinregType.REG_SZ)
        except:
            pass
    elif cfg_status[3] == '0':
        try:
            client.delete_entry(RUN_REG_PATH, "ChangeTheme_auto")
        except:
            pass
    
def clickCheckAuto():
    cfg_status[3] = str(enabledAutoStart.get())
    print(cfg_status[3])
    checkingAutoStart()
    
def quit_window(icon, item):
    icon.stop()
    tk.after(0,tk.deiconify)
    tk.quit()
    quit() # Выход из программы Python
    # Можно еще использоваться sys.exit() (import sys)
    # exit() # Выход из цикла
    
def check_sun_set_rise():
    lat, lon = dict_cities.get(cfg_status[6])
    res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=sunrise,sunset&timezone=Europe%2FMoscow&forecast_days=1") 
    data = res.json()
    data = data.get('daily')
    return {'sunset': data.get('sunset')[0][-5:], 'sunrise': data.get('sunrise')[0][-5:]}
    
def selectItemCombobox(eventObject):
    cfg_status[6] = combobox.get()

def save():
    updateSunsetSunrise()
    if sunsetVar.get() == 1:
        cfg_status[1] = sunset_
        textVar.set(sunset_)
    else:
        cfg_status[1] = textVar.get()
        
    if sunriseVar.get() == 1:
        cfg_status[2] = sunrise_
        textVar2.set(sunrise_)
    else:
        cfg_status[2] = textVar2.get()
        
    file = open(homedir + "/Documents/change-theme-auto.cfg", "w")
    file.write(','.join(cfg_status))
    print(cfg_status)
    file.close()
    
def show_window(icon, item):
    icon.stop()
    tk.after(0,tk.deiconify)

def withdraw_window():
    # my_thread = threading.Thread(target=updateSunsetSunrise)
    # my_thread.start()
    # my_thread.join()
    tk.withdraw()
    # if first_run is True: timenow()
    image = Image.open(dirThisfile + "\change-theme-icon.jpg")
    menu = (item('Quit', quit_window), item('Show', show_window, default=True))
    icon = Icon("name", image, "title", menu)
    print(Icon.HAS_DEFAULT_ACTION)
    save()
    timenow()
    icon.run_detached()
    

    
def timenow():
    global a
    timer = 600 # 10 минут, далее должно измениться 
    timeNow = datetime.now()
    print(timeNow)
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
    # Tk.call

if cfg_status[0] == '0':
    enabled.set(0)
else:
    enabled.set(1)
if cfg_status[3] == '0':
    enabledAutoStart.set(0)
else:
    enabledAutoStart.set(1)
if cfg_status[4] == '0':
    txt1_state = 'normal'
else:
    txt1_state = 'readonly'
    sunsetVar.set(1)
if cfg_status[5] == '0':
    txt2_state = 'normal'
else:
    txt2_state = 'readonly'
    sunriseVar.set(1)

# textVar = cfg_status[1]
# textVar2 = cfg_status[2]
check = Checkbutton(text='Смена темы по расписанию', variable=enabled, command=clickCheck)
check.pack()
txt1 = Entry(width=10, textvariable=textVar)
txt2 = Entry(width=10, textvariable=textVar2)
txt1.insert(0, cfg_status[1])
txt2.insert(0, cfg_status[2])
txt1.config(state=txt1_state)
txt2.config(state=txt2_state)
txt1.pack()
txt2.pack()

def sunsetfunc():
    cfg_status[4] = str(sunsetVar.get())
    if sunsetVar.get() == 1:
        txt1.config(state='readonly')
    else:
        txt1.config(state='normal')
        
def sunrisefunc():
    cfg_status[5] = str(sunriseVar.get())
    if sunriseVar.get() == 1:
        txt2.config(state='readonly')
    else:
        txt2.config(state='normal')


combobox = ttk.Combobox(values=cities, state='readonly')
combobox.pack()
combobox.bind("<<ComboboxSelected>>", selectItemCombobox)
combobox.current(cities.index(cfg_status[6]))
# print(combobox.get())

sunset = Checkbutton(text='Включать dark theme во время заката', variable=sunsetVar, command=sunsetfunc)
sunset.pack()
sunrise = Checkbutton(text='Выключать dark theme во время восхода', variable=sunriseVar, command=sunrisefunc)
sunrise.pack()


checkAutoStart = Checkbutton(text='Автозапуск при включении пк', variable=enabledAutoStart, command=clickCheckAuto)
checkAutoStart.pack()

# save_button = Button(text="save configuration", command=save)
# save_button.pack()

btn = Button(text="change theme", command=changetheme)
btn.pack()



# texttext = Label(text=f"{dirThisfile}, {__file__}, {curdir}, {argv[0]}")
# texttext.pack()

# timenow()
withdraw_window()
checking_on_off_first_position()
checkingAutoStart()

tk.protocol('WM_DELETE_WINDOW', withdraw_window)
tk.mainloop()
