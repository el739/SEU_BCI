import time
import tkinter as tk
from tkinter import Frame, Label
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading
from threading import Timer
import os
import ctypes
import queue
from filter import filter
from CCA_NO_downSample import cca_no_downsample
from CCA_user import cca_user
import multiprocessing
from multiprocessing import shared_memory
from multiprocessing import Array, Lock
from matplotlib.collections import LineCollection

# 初始化变量
freq_list = [26, 27, 29, 27.5, 31, 32, 30.5, 22,
             34.5, 28.5, 32.5, 34, 31.5, 28, 33.5, 33, 30, 29.5]
WIN_SIZE = 5
SAMPLE_RATE = 1000
CH_NUM = 9
fs = 1000
InitCount = 0
eeg_data = np.zeros((CH_NUM, SAMPLE_RATE * WIN_SIZE))
shared_eeg_data = multiprocessing.Array('d', eeg_data.flatten())
shared_filtered_data = multiprocessing.Array('d', 8*2000)
shared_output = multiprocessing.Array('d' , len(freq_list))
shape = eeg_data.shape
file_path = 'eeg_data.txt'
shm_name = "my_shared_memory"
shm = shared_memory.SharedMemory(name=shm_name)
lock = Lock()  # 同样需要锁来避免竞争条件
filtered_data=np.zeros((8,2000))

def get_eeg_data():
    """持续读取 EEG 数据并更新共享数据。"""
    with lock:
        array = np.ndarray(eeg_data.flatten().shape, eeg_data.dtype, buffer=shm.buf)
        shared_eeg_data[:] = array
        time.sleep(0.1)

def calculate():
    get_eeg_data()
    with lock:
        eeg_data = np.frombuffer(shared_eeg_data.get_obj()).reshape(shape)
    # global InitCount
    # InitCount += 1
    # if InitCount >= 6:
    with lock:
        window_data = eeg_data[:8, 2300:4300]  # 截取数据窗口
    filtered_data = filter(fs, window_data)
    # print(filtered_data)
    shared_filtered_data[:] = filtered_data.flatten()
    res, corr_coeffs, output = cca_no_downsample(filtered_data, freq_list, 1000)
    # print(output)
    shared_output[:] = output
    a=Timer(0.05,calculate)
    a.start()





class App:
    def __init__(self, root):
        self.update_average_timer = None
        self.is_animating = True
        self.root = root
        self.root.title("1")
        self.root.attributes('-fullscreen', True)
        # 主窗口布局
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧图表区域
        self.chart_frame = tk.Frame(self.main_frame)
        self.chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 右侧控制区域
        self.control_frame = tk.Frame(self.main_frame, width=200)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建一个图表布局
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 创建动态折线数据  
        self.num_lines = 8  
        self.num_points = 2000  
        data = np.zeros((self.num_lines, self.num_points))  
        segments = np.array([np.column_stack([np.arange(self.num_points), data[i]]) for i in range(self.num_lines)])  

        # 创建 LineCollection  
        self.line_collection = LineCollection(segments, linewidths=1)  
        self.ax.add_collection(self.line_collection)  

        self.ax.set_title("EEG Data")
        self.ax.set_xlim(0, 2000)
        self.ax.set_ylim(-50, 1500)
        self.ax.legend()  # 显示图例

        # 创建频率输出图
        self.figure_output, self.ax_output = plt.subplots()
        self.canvas_output = FigureCanvasTkAgg(self.figure_output, master=self.chart_frame)
        self.canvas_output.draw()
        self.canvas_output.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.line_output, = self.ax_output.plot([], [], 'ro-')
        self.ax_output.set_title("Frequency Output")
        self.ax_output.set_xlabel("Frequency (Hz)")
        self.ax_output.set_ylabel("Output")
        self.ax_output.set_xlim(0, 40)
        self.ax_output.set_ylim(-1, 1)

        # 控制区域的控件
        self.refresh_button = tk.Button(self.control_frame, text="停止刷新", command=self.toggle_refresh)
        self.refresh_button.pack(pady=10)

        self.x_range_label = tk.Label(self.control_frame, text="X轴范围:")
        self.x_range_label.pack()
        self.x_range_entry = tk.Entry(self.control_frame)
        self.x_range_entry.pack(pady=5)
        self.x_range_entry.bind("<Return>", self.update_x_range)

        self.y_range_label = tk.Label(self.control_frame, text="Y轴范围:")
        self.y_range_label.pack()
        self.y_range_entry = tk.Entry(self.control_frame)
        self.y_range_entry.pack(pady=5)
        self.y_range_entry.bind("<Return>", self.update_y_range)

        # 启动实时更新
        self.update_average_timer = Timer(0.01, self.update)  # 设定0.1秒一次
        self.update_average_timer.start()

        self.ani = animation.FuncAnimation(self.figure_output, self.update, interval=10, blit=True)

    def toggle_refresh(self):
        """切换刷新状态。"""
        self.is_animating = not self.is_animating
        self.refresh_button.config(text="停止刷新" if self.is_animating else "启动刷新")
        if self.is_animating:
            # 恢复所有动画
            self.ani.resume()
            self.update_average_timer = Timer(0.01, self.update)
            self.update_average_timer.start()
        else:
            # 暂停所有动画
            self.ani.pause()
            self.update_average_timer.cancel()  # 取消定时器

    def update_x_range(self, event):
        """更新X轴范围。"""
        try:
            x_max = int(self.x_range_entry.get())
            self.ax.set_xlim(0, x_max)
            self.canvas.draw()
        except ValueError:
            print("请输入有效的数字作为X轴范围。")

    def update_y_range(self, event):
        """更新Y轴范围。"""
        try:
            y_max = int(self.y_range_entry.get())
            self.ax.set_ylim(-y_max, y_max)
            self.canvas.draw()
        except ValueError:
            print("请输入有效的数字作为Y轴范围。")

    def update(self, frame):
        if not self.is_animating:
            return
        with lock:
            filtered_data = np.frombuffer(shared_filtered_data.get_obj()).reshape(8,2000)
        # print(filtered_data)
        
        segments = np.array([np.column_stack([np.arange(self.num_points), filtered_data[i] + 1000 * i - 4000]) for i in range(self.num_lines)])  
        self.line_collection.set_segments(segments)  
        
        # self.canvas.draw()
        self.canvas.draw_idle() #! 只更新需要更新的图形
        output = np.frombuffer(shared_output.get_obj()).reshape(len(freq_list))

        print(output)
            # 检查输出并更新频率图
        if output.size > 0 and output.shape[0] == len(freq_list):
                self.output_data = output  # 更新 output 数据

                # 清空原有的柱状图数据
                self.ax_output.clear()

                # 使用频率和输出数据绘制柱状图
                bar_width = 0.5
                bar_color = 'pink'
                bars = self.ax_output.bar(freq_list, self.output_data, width=bar_width, color=bar_color)
                # 在每个柱子上方添加数值标签
                for bar, freq, value in zip(bars, freq_list, self.output_data):
                    self.ax_output.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{value:.2f}',ha='center', va='bottom')

                # 设置标题和标签
                self.ax_output.set_title("Frequency Output")
                self.ax_output.set_xlabel("Frequency (Hz)")
                self.ax_output.set_ylabel("Output")

                # 设置Y轴范围为0到1
                self.ax_output.set_ylim(0, 1)

                # 设置X轴范围为freq_list的最小值到最大值
                self.ax_output.set_xlim(min(freq_list) - 1, max(freq_list) + 1)  # 留出一些边缘空间

                self.canvas_output.draw()  # 确保画布被更新

        return self.line_collection

if __name__ == "__main__":
    a=threading.Thread(target=calculate)
    a.start()
    root = tk.Tk()

    app = App(root)

    # 退出按钮
    quit_button = tk.Button(root, text="退出", command=root.quit, font=('Arial', 20))
    quit_button.place(x=20, y=20)
    root.mainloop()
