# load dll
import time

import numpy as np
import ctypes
import threading
import queue
import threading
from threading import Timer
from filter import filter
import ctypes
from CCA_user import cca_user
import multiprocessing
import tkinter as tk
from tkinter import Frame, Label
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Slider
from multiprocessing import shared_memory

WIN_SIZE = 5
SAMPLE_RATE = 1000
CH_NUM = 9
THRD_CORR = 0.1
THRD_CNT = 2
fifo_queue = queue.Queue()

g_ssvep_result = -1
g_counter = 0
res_prev = -1.0

freq_list = [26, 27, 29, 27.5, 31, 32, 30.5, 22,
             34.5, 28.5, 32.5, 34, 31.5,28, 33.5, 33, 30, 29.5]
# 3s的时间窗，创建一个队列，只存3s的数据，eeg数据先进先出
eeg_data = np.zeros((CH_NUM, SAMPLE_RATE * WIN_SIZE))
shm_size = CH_NUM * SAMPLE_RATE * WIN_SIZE * 8  # 每个 float64 是 8 字节
shm = shared_memory.SharedMemory(create=True, size=shm_size)

# 设置中文显示字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
matplotlib.rcParams['axes.unicode_minus'] = False  # 负号显示


# class App:
#         def __init__(self, root):
#             self.root = root
#             self.root.title("实时显示八个动态折线图")
#             # 创建一个 4x2 的网格布局
#             self.figure, self.axes = plt.subplots(4, 2, figsize=(12, 10))
#             self.canvas = FigureCanvasTkAgg(self.figure, master=root)
#             self.canvas.draw()
#             self.canvas.get_tk_widget().place(x=0, y=0)
#
#             label1 = tk.Label(root, text="通道", bg="green", font=('Arial', 20))
#             label1.place(x=0, y=0)
#
#             # 创建一个退出按钮
#             quit_button = tk.Button(root, text="退出", command=root.quit, font=('Arial', 20))
#             quit_button.place(x=1500, y=850)
#             # 创建折线图，每个图表对应一个通道
#             self.lines = []
#             for i, ax in enumerate(self.axes.flat):
#                 line, = ax.plot(np.arange(0, eeg_data.shape[1]), eeg_data[i])  # 每个通道绘制一条线
#                 self.lines.append(line)
#                 ax.set_title(f"通道 {i + 1}")
#                 ax.set_xlim(0, 400)  # 设置x轴范围为0到400
#                 ax.set_ylim(np.min(eeg_data), np.max(eeg_data))
#
#             # 添加滚动条，用于选择显示窗口
#             ax_slider = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
#             self.slider = Slider(ax_slider, '选取时间段', 1, eeg_data.shape[1], valinit=10, valstep=1)
#
#             self.slider.on_changed(self.update_average)
#
#             # 启动动画，实时更新折线图
#             self.ani = animation.FuncAnimation(self.figure, self.update, interval=100, blit=True)
#
#         def AA(self):
#             dr = threading.Thread(target=self.__init__)
#             dr.start()
#
#
#         def update(self, frame):
#             # 更新每个通道的折线图
#             for i in range(8):
#                 self.lines[i].set_ydata(eeg_data[i])  # 使用最新的eeg_data
#             self.canvas.draw()  # 重绘画布
#             return self.lines
#
#
#         def update_average(self, val):
#             # 计算指定时间段的平均值
#             window_size = int(self.slider.val)
#             averages = []
#             for i in range(8):
#                 if window_size > eeg_data.shape[1]:
#                     averages.append(np.mean(eeg_data[i]))
#                 else:
#                     averages.append(np.mean(eeg_data[i][-window_size:]))
#             # print(f"Averages over the last {window_size} points: {averages}")






def cca_fun():
    # print("CCA_FUN")
    global res_prev, g_ssvep_result
    # 数据大于0.2s就用时间窗记录
    # print(f"fifo_queue.qsize():{fifo_queue.qsize()}")
    if fifo_queue.qsize() >= 200 * CH_NUM:
        with lock:
            for i in range(200):
                for j in range(CH_NUM):
                    eeg_data[j, i + int(SAMPLE_RATE * (WIN_SIZE - 0.2))] = fifo_queue.get()
        # 将上面处理过的数据往队首步进，空出队列后0.2s的位置，用来存放新数据
        for i in range(int(SAMPLE_RATE * (WIN_SIZE - 0.2))):
            for j in range(CH_NUM):
                eeg_data[j, i] = eeg_data[j, i + 200]


    shared_eeg_data[:] = eeg_data.flatten()  # 将更新后的数组展平成一维，并复制到共享内存
    # 每隔0.1s执行一次
    t = Timer(0.1, cca_fun)
    t.start()

InitCount=0


def analysis(shared_eeg_data, lock, shape):
    print("analysis_fun")
    global g_counter, res_prev, InitCount
    InitCount += 1
    if InitCount >= 6:
        with lock:
            eeg_data = np.frombuffer(shared_eeg_data.get_obj()).reshape(shape)  # 将共享数据重新构造为numpy数组
            window_data = eeg_data[:8, 2300:4300]
        print(window_data.shape)  # 8 * 2000
        filtered_data = filter(fs, window_data)

        # cca处理2s中的数据
        startTime = time.time()
        res, corr_coeffs, output = cca_user(filtered_data, freq_list, 1000, 450)
        endTime = time.time()
        print(f"频率为：{res}, 相关系数为：{corr_coeffs}, 时间：{endTime - startTime}")

        if corr_coeffs > THRD_CORR and res == res_prev:
            g_counter += 1
        else:
            g_counter = 0
        res_prev = res

        if g_counter >= THRD_CNT:
            g_ssvep_result = res
            print(f"g_ssvep_result: {g_ssvep_result}")
        else:
            g_ssvep_result = 99

        with open('results.txt', 'w') as f:
            SendData = f"{InitCount}+{res}+{g_ssvep_result},"
            f.write("----------------\n")
            f.seek(0)
            f.write(SendData)
            print(f"写入的数据: {SendData}")


def process_analysis(shared_eeg_data,lock, shape):
    while True:
        analysis(shared_eeg_data,lock, shape)
        time.sleep(0.5)

# load dll as my_dll
my_dll = ctypes.CDLL("C:/Users/Lenovo/Desktop/脑机接口/LinkMe.dll")

# init functions of dll
my_dll.dataProtocol.argtypes = (ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
my_dll.dataProtocol.restype = ctypes.c_int

my_dll.getElectricityValue.restype = ctypes.c_int

my_dll.getFallFlag.argtypes = (ctypes.POINTER(ctypes.c_int),)

my_dll.getData.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_double))

my_dll.getDataCurrIndex.argtypes = (ctypes.POINTER(ctypes.c_long),)

my_dll.getImpedance.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_double))

elecValue = -1
# 佩戴状态
fallFlag = []
# 包中的电位数据，n行9列
data_value = []
# 数据包序号，可选则用于判断接受的数据是否连续
data_current_index = []

is_received_data = True

data_buffer = []
lock = threading.Lock()

fs = 1000
window_size = 2 * fs


# 测试本地数据用此方法加载本地文件
def readOffLineData(path):
    # 打开文件
    with open(path, 'r') as file:
        each = file.read()
    data = each.split(" ")
    print(len(data))

    data = [int(num, 16) for num in data if num]
    print(len(data))
    print(type(data[0]))
    return data


global impedanceValue


# 加载dll解析linkme数据
def makeDataWithShape(data):
    data_array = (ctypes.c_ubyte * len(data))(*data)
    # 解析数据
    length = my_dll.dataProtocol(data_array, len(data))
    if length > 0:
        # 获取电位数据
        data_point = my_dll.getData()
        # 将返回值转换为二维数组
        data_value = [[data_point[i][j] for j in range(9)] for i in range(length)]

        for i in range(len(data_value)):
            for j in range(9):
                fifo_queue.put(data_value[i][j])
                # print(f"fifo_queue.qsize_sss:{fifo_queue.qsize()}")
    else:
        print("数据长度不够, 没有脑电数据", length)


def openSerial():
    import serial
    import serial.tools.list_ports

    # 查找所有可用串口
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("无串口设备。")
    else:
        print("可用的串口设备如下：")
        for comport in ports_list:
            print(list(comport)[0], list(comport)[1])
    print("分割线")

    # 从可用的串口中选择linkme设备使用的串口，当前测试使用串口3
    # 打开串口3
    port = "COM7"
    ser = serial.Serial(port, 460800)  # 打开COM3，将波特率配置为115200，（光纤传输也可以是460800）其余参数使用默认值
    if ser.isOpen():
        print("串口 %s 打开成功！" % port)
        print(ser.name)
    else:
        print("串口 %s 打开失败" % port)
    return ser


# 接收数据
def receiveData(ser, is_received_data):
    while is_received_data:
        try:
            com_input = ser.read(25 * 136)
        except:
            print("no enough bytes")
            break
        if com_input:  # 如果读取结果非空，则输出
            with lock:
                global data_buffer
                data_buffer += com_input


# 关闭串口
def closeSerial(ser):
    with lock:
        ser.close()
    if ser.isOpen():  # 判断串口是否关闭
        print("串口未关闭。")
    else:
        print("串口已关闭。")

def passData(ser,is_received_data):
    while is_received_data:
        each_length = 10 * 136
        global data_buffer
        if data_buffer != []:
            data = data_buffer[0: each_length]
            with lock:
                data_buffer = data_buffer[each_length:]
            makeDataWithShape(data)


if __name__ == "__main__":
    # 创建一个共享文件
    with open('results.txt', 'w') as f:
        f.write("----------------\n")
    # root = tk.Tk()
    # app = App(root)
    manager = multiprocessing.Manager()
    lock = multiprocessing.Lock()
    shared_eeg_data = multiprocessing.Array('d', eeg_data.flatten())  # 将数组展平成一维，并通过multiprocessing.Array共享
    shape = eeg_data.shape  # 记录数组形状以便重新构造
    # 创建多进程

    s = multiprocessing.Process(target=process_analysis, args=(shared_eeg_data,lock, shape))
    s.start()

    cca_fun()
    # 打开串口
    ser = openSerial()
    # 开启t线程接收数据到data_buffer缓冲区
    t = threading.Thread(target=receiveData, args=(ser, is_received_data))
    t.start()
    # 开启p线程解析数据并传输到queue
    p = threading.Thread(target=passData, args=(ser, is_received_data))
    p.start()
    # root.mainloop()
    while True:
        pass
    s.join()  # 等待子进程结束

    # 关闭线程
    is_received_data = False
    # 关闭串口
    closeSerial(ser)
