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

Workbench = RDK.Item('Workbench3')
Workbench_surname = RDK.Item('Workbench_surname3')

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

def task_3(scale):
    robot.setPoseFrame(RDK.Item('Frame3'))
    robot.MoveJ(Workbench.Pose())                                       #движение в точку над Именем
    move_j(100, (10, 200, -200))                                        #движение  точку над буквой
    letter_v(scale)                                                     #отрисовка буквы В
    robot.MoveJ(Workbench.Pose())
    move_j(100, (10, 140, -200))
    letter_a(scale)                                                     #отрисовка буквы А
    robot.MoveJ(Workbench.Pose())
    move_j(100, (-5, 80, -200))
    letter_d(scale)                                                     #отрисовка буквы Д
    robot.MoveJ(Workbench.Pose())
    move_j(100, (10+96*scale, 20, -200))
    letter_i(scale)                                                     #отрисовка буквы И
    robot.MoveJ(Workbench.Pose())
    move_j(100, (10, -40, -200))
    letter_m(scale)                                                     #отрисовка буквы М
    robot.MoveJ(Workbench.Pose())

    robot.MoveJ(Workbench_surname.Pose())                               #движение в точку над Фамилией
    move_j(100, (60, 200, -200))                                        #движение  точку над буквой
    letter_m(scale)                                                     #отрисовка буквы М
    robot.MoveJ(Workbench_surname.Pose())
    move_j(100, (60+16*scale, 140, -200))
    letter_o(scale)                                                     #отрисовка буквы О
    robot.MoveJ(Workbench_surname.Pose())
    move_j(100, (60, 80, -200))
    letter_v(scale)                                                     #отрисовка буквы В
    robot.MoveJ(Workbench_surname.Pose())
    move_j(100, (60+96*scale, 20, -200))
    letter_t(scale)                                                     #отрисовка буквы Т
    robot.MoveJ(Workbench_surname.Pose())
    move_j(100, (60, -40, -200))
    letter_ya(scale)                                                    #отрисовка буквы Я
    robot.MoveJ(Workbench_surname.Pose())
    move_j(100, (60, -100, -200))
    letter_n(scale)                                                     #отрисовка буквы Н
    robot.MoveJ(Workbench_surname.Pose())

    robot.setPoseFrame(base_frame)
    robot.MoveJ(Base.Pose())                                            #возврат в исходное положение

scale = 0.0
def choose_scale():                                                     #функция вывода окна для обработки вносимых значений
    """Функция вывода окна для обработки вносимых значений."""
    window = Tk()
    window.title("Напишите варианты")
    window.geometry("400x100")

    frame = Frame(window, padx=10, pady=10)
    frame.pack(expand=True)

    scale_lbl = Label(frame, text="Укажите масштаб")
    scale_lbl.grid(row=1, column=1, pady=10)
    scale_ent = Entry(frame)
    scale_ent.grid(row=1, column=2)
    scale_ent.insert(0, "1")


    def handle_add_button():
        global scale
        try:
            scale = float(scale_ent.get())
            window.destroy() # Закрываем окно
         
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число.")
    
    scale_btn = Button(
        frame,
        text="Добавить",
        command=handle_add_button  # Измененная команда
    )
    scale_btn.grid(row=1, column=3)

    window.mainloop()

choose_scale()
task_3(scale)  # Запуск task_3