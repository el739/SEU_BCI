import threading
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.widgets import Slider
import time

import DataAnalysis2 as DA
from DataAnalysis2 import shared_eeg_data
from DataAnalysis2 import eeg_data


# 假设 eeg_data 是一个 numpy 数组
CH_NUM = 9  # 8 个通道
SAMPLE_RATE = 1000  # 每秒 256 个采样点
WIN_SIZE = 5  # 时间窗口大小为 3 秒




class App:
    def __init__(self, root):
        self.root = root
        self.root.title("实时显示八个动态折线图")

        # 创建一个 4x2 的网格布局
        self.figure, self.axes = plt.subplots(4, 2, figsize=(12, 10))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x=0, y=0)

        def nnpp (shared_eeg_data, lock, shape):
            with lock:
                eeg_data = np.frombuffer(shared_eeg_data.get_obj()).reshape(shape)


        # 创建折线图，每个图表对应一个通道
        self.lines = []
        for i, ax in enumerate(self.axes.flat):
            line, = ax.plot(np.arange(0, 400), eeg_data[i, :400])  # 每个通道绘制一条线，限制 x 轴到 400
            self.lines.append(line)
            ax.set_title(f"通道 {i + 1}")
            ax.set_xlim(0, 400)  # 设置 x 轴范围为 0 到 400
            ax.set_ylim(np.min(eeg_data), np.max(eeg_data))  # 设置 y 轴范围

        # 添加滚动条，用于选择显示窗口
        ax_slider = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        self.slider = Slider(ax_slider, '选取时间段', 1, eeg_data.shape[1], valinit=10, valstep=1)

        self.slider.on_changed(self.update_average)

        # 启动动画，实时更新折线图
        self.ani = animation.FuncAnimation(self.figure, self.update, interval=100, blit=True)

    def update(self, frame):
        # 更新每个通道的折线图，只显示前 400 个数据点
        for i in range(8):
            self.lines[i].set_ydata(eeg_data[i, :400])
        self.canvas.draw()  # 重绘画布
        return self.lines

    def update_average(self, val):
        # 计算指定时间段的平均值
        window_size = int(self.slider.val)
        averages = []
        for i in range(8):
            if window_size > eeg_data.shape[1]:
                averages.append(np.mean(eeg_data[i]))
            else:
                averages.append(np.mean(eeg_data[i][-window_size:]))
        print(f"Averages over the last {window_size} points: {averages}")


# # 启动 Tkinter 应用程序
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    label1 = tk.Label(root, text="通道", bg="green", font=('Arial', 20))
    label1.place(x=0, y=0)

    # 创建一个退出按钮
    quit_button = tk.Button(root, text="退出", command=root.quit, font=('Arial', 20))
    quit_button.place(x=1500, y=850)

    root.mainloop()