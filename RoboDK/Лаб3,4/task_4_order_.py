from robolink import *                                                  # RoboDK API
from robodk import *                                                    # Robot toolbox
import tkinter as tk
from tkinter import *
from tkinter import messagebox
#import numpy as np

RDK = Robolink()
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)             #инициализация робота
if not robot.Valid():
    raise Exception('No robot selected or available')

robot.setPoseFrame(robot.PoseFrame())
robot.setPoseTool(robot.PoseTool())
robot.setRounding(10)  
robot.setSpeed(100)

base_frame = RDK.Item('KUKA KR 4 R600 Base')
Base = RDK.Item('Base')                                                 #определение домашнего положения

Workbench = RDK.Item('Workbench4')
Workbench_surname = RDK.Item('Workbench_surname4')

def move_l(speed, offset):                                              #функция линейного движения
    robot.setSpeed(speed)                                               #задание скорости движения робота
    point = robot.Pose()*transl(offset[0],offset[1],offset[2])          #расчет желаемой координаты
    robot.MoveL(point)                                                  #линейное движение к определённой координате

def move_c(speed, offset_1, offset_2):                                  #функция дугообразного движения  
    robot.setSpeed(speed)                                               #задание скорости движения робота                        
    point1 = robot.Pose()*transl(offset_1[0],offset_1[1],offset_1[2])   #промежуточная координата   
    point2 = robot.Pose()*transl(offset_2[0],offset_2[1],offset_2[2])   #конечная координата   
    robot.MoveC(point1,point2)                                          #дугообразное движение к определённой координате

def move_j(speed, offset):                                              #Функция ptp движения  
    robot.setSpeed(speed)                                               #Задание скорости движения робота
    point = robot.Pose()*transl(offset[0],offset[1],offset[2])          #расчет желаемой координаты
    robot.MoveJ(point)                                                  #ptp движение к определённой координате

def letter_v(k):                                                        #функция написания буквы В
    move_l(50, (0, 0, -50))                                             #опускание маркера на рабочую поверхность
    move_l(75, (96*k, 0, 0))                                           #линейное движение к В1
    move_c(75,(-20*k, -16*k, 0) , (-40*k, 0, 0))                        #circle движение В2 В3 
    move_c(75,(-28*k, -32*k, 0) , (-56*k, 0, 0))                        #circle движение В4 В5 
    move_l(50, (0, 0, 50))                                              #подьём маркера над рабочей поверхностью

def letter_a(k):                                                        #функция написания буквы А
    move_l(50, (0, 0, -50))                                             #опускание маркера на рабочую поверхность
    move_l(75, (96*k, -16*k, 0))                                       #линейные движения
    move_l(75, (-96*k, -16*k, 0))                                          
    move_l(50, (0, 0, 50))                                              #подьём маркера над рабочей поверхностью
    move_l(50, (36*k, 6*k, 0))                                          
    move_l(50, (0, 0, -50))                                             #опускание маркера на рабочую поверхность
    move_l(75, (0, 20*k, 0))                                          
    move_l(50, (0, 0, 50))                                              #подьём маркера над рабочей поверхностью
    
def letter_d(k):                                                        #функция написания буквы Д
    move_l(50, (0, 0, -50))
    move_l(75, (12*k, 0, 0))                                          
    move_l(75, (0, -32*k, 0))
    move_l(75, (-12*k, 0, 0))                                          
    move_l(50, (0, 0, 50))                                          
    move_l(50, (12*k, 28*k, 0))                                          
    move_l(50, (0, 0, -50))                                          
    move_l(75, (96*k, 0, 0)) 
    move_l(75, (0, -24*k, 0))   
    move_l(75, (-96*k, 0, 0))                                        
    move_l(50, (0, 0, 50))                                      
    
def letter_i(k):                                                        #функция написания буквы И
    move_l(50, (0, 0, -50))
    move_l(75, (-96*k, 0, 0))                                          
    move_l(75, (96*k, -32*k, 0)) 
    move_l(75, (-96*k, 0, 0))                                         
    move_l(50, (0, 0, 50))   

def letter_m(k):                                                        #функция написания буквы М
    move_l(50, (0, 0, -50))
    move_l(75, (96*k, -8*k, 0))                                         
    move_l(75, (-96*k, -8*k, 0)) 
    move_l(75, (96*k, -8*k, 0))
    move_l(75, (-96*k, -8*k, 0))                                         
    move_l(50, (0, 0, 50)) 

def letter_o(k):                                                        #функция написания буквы О
    move_l(50, (0, 0, -50))
    move_c(75,(-16*k, -16*k, 0) , (0, -32*k, 0))                          
    move_l(75, (64*k, 0, 0)) 
    move_c(75,(16*k, 16*k, 0) , (0, 32*k, 0))
    move_l(75, (-64*k, 0, 0)) 
    move_l(50, (0, 0, 50))  

def letter_t(k):                                                        #функция написания буквы Т
    move_l(50, (0, 0, -50))
    move_l(75, (0, -32*k, 0))
    move_l(50, (0, 0, 50))
    move_l(50, (0, 16, 0))
    move_l(50, (0, 0, -50))
    move_l(75, (-96*k, 0, 0))                                          
    move_l(50, (0, 0, 50))

def letter_ya(k):                                                        #функция написания буквы Я
    move_l(50, (0, 0, -50))
    move_l(75, (48*k, -32*k, 0)) 
    move_c(75,(24*k, 24*k, 0) , (48*k, 0, 0))                          
    move_l(75, (-96*k, 0, 0)) 
    move_l(50, (0, 0, 50))

def letter_n(k):                                                        #функция написания буквы Н
    move_l(50, (0, 0, -50))
    move_l(75, (96*k, 0, 0))
    move_l(50, (0, 0, 50))
    move_l(50, (0, -32*k, 0))
    move_l(50, (0, 0, -50))
    move_l(75, (-96*k, 0, 0))                                          
    move_l(50, (0, 0, 50))
    move_l(50, (48*k, 32*k, 0))
    move_l(50, (0, 0, -50))
    move_l(75, (0, -32*k, 0))
    move_l(50, (0, 0, 50))

def draw_letter_name(position, i, scale):                               #функция перестановки букв в имени (пользователь сам выбирает последовательность)
    if i == 1:                                                          #в зависимости от позиции задаем движение к точке над буквой (этот цикл для первой позиции в имени)
        if position[i] in [1, 2, 5]:                                    #в зависимости от буквы задаем движение к точке над буквой
            move_j(100, (10, 200, -200))                                #если нужно нарисовать В,А,М 
        elif position[i] == 3:                                          #если нужно нарисовать Д 
            move_j(100, (-5, 200, -200))
        elif position[i] == 4:                                          #если нужно нарисовать И
            move_j(100, (10+96*scale, 200, -200))

    if i == 2:                                                          #для второй позиции
        if position[i] in [1, 2, 5]:
            move_j(100, (10, 140, -200))
        elif position[i] == 3:
            move_j(100, (-5, 140, -200))
        elif position[i] == 4:
            move_j(100, (10+96*scale, 140, -200))

    if i == 3:                                                          #для третей позиции
        if position[i] in [1, 2, 5]:
            move_j(100, (10, 80, -200))
        elif position[i] == 3:
            move_j(100, (-5, 80, -200))
        elif position[i] == 4:
            move_j(100, (10+96*scale, 80, -200))

    if i == 4:                                                          #для четвертой позиции
        if position[i] in [1, 2, 5]:
            move_j(100, (10, 20, -200))
        elif position[i] == 3:
            move_j(100, (-5, 20, -200))
        elif position[i] == 4:
            move_j(100, (10+96*scale, 20, -200))

    if i == 5:                                                          #для пятой позиции
        if position[i] in [1, 2, 5]:
            move_j(100, (10, -40, -200))
        elif position[i] == 3:
            move_j(100, (-5, -40, -200))
        elif position[i] == 4:
            move_j(100, (10+96*scale, -40, -200))
    
    if position[i] == 1:                                                #цифре 1 соответствует буква В
        letter_v(scale)
    if position[i] == 2:                                                #цифре 2 соответствует буква А
        letter_a(scale)
    if position[i] == 3:                                                #цифре 3 соответствует буква Д
        letter_d(scale)
    if position[i] == 4:                                                #цифре 4 соответствует буква И
        letter_i(scale)
    if position[i] == 5:                                                #цифре 5 соответствует буква М
        letter_m(scale)

def draw_letter_surname(position, i, scale):                            #функция перестановки букв в фамилии (пользователь сам выбирает последовательность)
    if i == 1:                                                          #в зависимости от позиции задаем движение к точке над буквой (этот цикл для первой позиции в фамилии)
        if position[i] in [1, 3, 5, 6]:                                 #в зависимости от буквы задаем движение к точке над буквой
            move_j(100, (60, 200, -200))                                #если нужно нарисовать М, В, Я, Н 
        elif position[i] == 2:                                          #если нужно нарисовать О
            move_j(100, (60+16*scale, 200, -200))
        elif position[i] == 4:                                          #если нужно нарисовать Т
            move_j(100, (60+96*scale, 200, -200))

    if i == 2:                                                          #для второй позиции
        if position[i] in [1, 3, 5, 6]:
            move_j(100, (60, 140, -200))
        elif position[i] == 2:
            move_j(100, (60+16*scale, 140, -200))
        elif position[i] == 4:
            move_j(100, (60+96*scale, 140, -200))
    
    if i == 3:                                                          #для третей позиции
        if position[i] in [1, 3, 5, 6]:
            move_j(100, (60, 80, -200))
        elif position[i] == 2:
            move_j(100, (60+16*scale, 80, -200))
        elif position[i] == 4:
            move_j(100, (60+96*scale, 80, -200))

    if i == 4:                                                          #для четвертой позиции
        if position[i] in [1, 3, 5, 6]:
            move_j(100, (60, 20, -200))
        elif position[i] == 2:
            move_j(100, (60+16*scale, 20, -200))
        elif position[i] == 4:
            move_j(100, (60+96*scale, 20, -200))

    if i == 5:                                                          #для пятой позиции
        if position[i] in [1, 3, 5, 6]:
            move_j(100, (60, -40, -200))
        elif position[i] == 2:
            move_j(100, (60+16*scale, -40, -200))
        elif position[i] == 4:
            move_j(100, (60+96*scale, -40, -200))

    if i == 6:                                                          #для шестой позиции
        if position[i] in [1, 3, 5, 6]:
            move_j(100, (60, -100, -200))
        elif position[i] == 2:
            move_j(100, (60+16*scale, -100, -200))
        elif position[i] == 4:
            move_j(100, (60+96*scale, -100, -200))
    
    if position[i] == 1:                                                #цифре 1 соответствует буква М
        letter_m(scale)
    if position[i] == 2:                                                #цифре 2 соответствует буква О
        letter_o(scale)
    if position[i] == 3:                                                #цифре 3 соответствует буква В
        letter_v(scale)
    if position[i] == 4:                                                #цифре 4 соответствует буква Т
        letter_t(scale)
    if position[i] == 5:                                                #цифре 5 соответствует буква Я
        letter_ya(scale)
    if position[i] == 6:                                                #цифре 6 соответствует буква Н
        letter_n(scale)

def task_4(name, surname):
    robot.setPoseFrame(RDK.Item('Frame4'))
    k=1

    order_name=5
    position_name=[0,0,0,0,0,0]
    Number_name=float(name)
    
    for i in range(order_name):                                         #алгоритм перевода 5ти значного числа (в имени) в массив из входящих в него цифр
        position_name[i+1]=(Number_name//10**(order_name-(i+1)))
        Number_name%=10 ** (order_name-(i+1))

    robot.MoveJ(Workbench.Pose())                                       #движение в точку над именем
    draw_letter_name(position_name, 1, k)                               #отрисовка буквы в имени на первой позиции
    robot.MoveJ(Workbench.Pose())
    draw_letter_name(position_name, 2, k)                               #отрисовка буквы на второй позиции
    robot.MoveJ(Workbench.Pose())
    draw_letter_name(position_name, 3, k)                               #отрисовка буквы на третей позиции
    robot.MoveJ(Workbench.Pose())
    draw_letter_name(position_name, 4, k)                               #отрисовка буквы на четвертой позиции
    robot.MoveJ(Workbench.Pose())
    draw_letter_name(position_name, 5, k)                               #отрисовка буквы на пятой позиции
    robot.MoveJ(Workbench.Pose())

    order_surname=6
    position_surname=[0,0,0,0,0,0,0]
    Number_surname=float(surname)
    
    for i in range(order_surname):                                      #алгоритм перевода 6ти значного числа (в фамилии) в массив из входящих в него цифр
        position_surname[i+1]=(Number_surname//10**(order_surname-(i+1)))
        Number_surname%=10 ** (order_surname-(i+1))

    robot.MoveJ(Workbench_surname.Pose())                               #движение в точку над фамилией
    draw_letter_surname(position_surname, 1, k)                         #отрисовка буквы в фамилии на первой позиции
    robot.MoveJ(Workbench_surname.Pose())
    draw_letter_surname(position_surname, 2, k)                         #отрисовка буквы на второй позиции
    robot.MoveJ(Workbench_surname.Pose())
    draw_letter_surname(position_surname, 3, k)                         #отрисовка буквы на третей позиции
    robot.MoveJ(Workbench_surname.Pose())
    draw_letter_surname(position_surname, 4, k)                         #отрисовка буквы на четвертой позиции
    robot.MoveJ(Workbench_surname.Pose())
    draw_letter_surname(position_surname, 5, k)                         #отрисовка буквы на пятой позиции
    robot.MoveJ(Workbench_surname.Pose())
    draw_letter_surname(position_surname, 6, k)                         #отрисовка буквы на шестой позиции
    robot.MoveJ(Workbench_surname.Pose())

    robot.setPoseFrame(base_frame)
    robot.MoveJ(Base.Pose())

def choose_scale():
    """Функция вывода окна для обработки вносимых значений."""
    window = Tk()
    window.title("Напишите варианты")
    window.geometry("450x150")

    frame = Frame(window, padx=10, pady=10)
    frame.pack(expand=True)

    name_order_lbl = Label(frame, text="Укажите порядок букв в имени")
    name_order_lbl.grid(row=2, column=1, pady=10)
    name_order_ent = Entry(frame)
    name_order_ent.grid(row=2, column=2)
    name_order_ent.insert(0, "12345")

    surname_order_lbl = Label(frame, text="Укажите порядок букв в фамилии")
    surname_order_lbl.grid(row=3, column=1, pady=10)
    surname_order_ent = Entry(frame)
    surname_order_ent.grid(row=3, column=2)
    surname_order_ent.insert(0, "123456")

    def handle_draw_button():
        try:
            name_order = name_order_ent.get()
            surname_order = surname_order_ent.get()
            window.destroy() # Закрываем окно
            task_4(name_order, surname_order)  # Запускаем task_4
        except Exception as e:
           messagebox.showerror("Ошибка", f"Ошибка: {e}")
            
    name_order_btn = Button(
        frame,
        text="Нарисовать",
        command=handle_draw_button  # Измененная команда
    )
    name_order_btn.grid(row=3, column=3)

    window.mainloop()

choose_scale()