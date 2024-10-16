import socket
import pygame
import ctypes
from pyvidplayer2 import VideoPlayer, Video
# 音量控制模块
from pygame.locals import *
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time
import pyautogui
import mmap
from threading import Timer
from mode_control import change_mode_send, blink_mode_send # 控制闪烁函数

# 初始化Pygame
pygame.init()

# 隐藏鼠标
# ctypes.windll.user32.ShowCursor(False)

# 设置Pygame窗口的分辨率（1920x1080）
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# win = pygame.display.set_mode((2560, 1440))

# 调试打印分辨率
screen_width, screen_height = win.get_size()
print(f"分辨率: {screen_width}x{screen_height}")

# 视频列表和当前视频索引
video_files = [r"./cctv/1.MP4", r"./cctv/2.MP4", r"./cctv/3.MP4", r"./cctv/4.MP4",
               r"./cctv/5.MP4", r"./cctv/6.MP4", r"./cctv/7.MP4", r"./cctv/10.MP4", r"./cctv/12.MP4"]
current_video_index = 0
# 鼠标点击位置以及对应频率
table_list = [  [26, 180, 180],
                [27, 720, 630],
                [29, 720, 990],
                [27.5, 720, 1350],
                [31, 720, 1710],

                [32, 1260, 810],
                [30.5, 1260, 1170],
                [22, 1260, 1530],

                [34.5, 1860, 810],
                [28.5, 1860, 1170],
                [32.5, 1860, 1530],

                [34, 2460, 810],
                [31.5, 2460, 1170],
                [28, 2460, 1530],

                [33.5, 3000, 630],
                [33, 3000, 990],
                [30, 3000, 1350],
                [29.5, 3000, 1710]
                 ]
# 按钮背景图片

image1 = pygame.image.load('./icon/wake_button.png')

image2 = pygame.image.load('./icon/next.png')
image3 = pygame.image.load('./icon/prev.png')
image4 = pygame.image.load('./icon/volume-up.png')
image5 = pygame.image.load('./icon/volume-down.png')

image6 = pygame.image.load('./icon/drink_water.png')
image7 = pygame.image.load('./icon/eat_food.png')
image8 = pygame.image.load('./icon/go_toilet.png')
image9 = pygame.image.load('./icon/turn_off.png')

image10 = pygame.image.load('./icon/medical_menu.png')
image10_1 = pygame.image.load('./icon/checkup.png')
image10_2 = pygame.image.load('./icon/medicine.png')

image11 = pygame.image.load('./icon/life_menu.png')
image11_1 = pygame.image.load('./icon/change_clothes.png')
image11_2 = pygame.image.load('./icon/wash.png')

image12 = pygame.image.load('./icon/fun_menu.png')
image12_1 = pygame.image.load('./icon/walk.png')
image12_2 = pygame.image.load('./icon/music.png')

image13 = pygame.image.load('./icon/return.png')

# 闪烁参数设置
host_master = '192.168.3.213'
host_slave = '192.168.3.214'
excel_topleft_right = '功能菜单频率相位设置右板.xlsx'
excel_topleft_left = '功能菜单频率相位设置左板.xlsx'
excel_mid_right = '频率相位设置右板.xlsx'
excel_mid_left = '频率相位设置左板.xlsx'
mbrightness = 2048
background_brightness = 512
# 鼠标悬停函数
def mouse_move(x, y, t):
    x = x -3840
    pyautogui.moveTo(x, y, duration=0.1)
    time.sleep(t)
# 鼠标点击函数
def mouse_click(x, y, button='left', clicks=1, interval=0.0):
    """
    在指定位置点击鼠标。
    参数:
    x (int): X 坐标。
    y (int): Y 坐标。
    button (str): 鼠标按键 ('left', 'right', 'middle')。默认为 'left'。
    clicks (int): 点击次数。默认为 1。
    interval (float): 多次点击之间的间隔时间。默认为 0 秒。
    """
    x = x - 3840
    pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)
    print(x, y)

# 初始化视频播放器
def load_video(index):
    video_path = video_files[index]
    video = Video(video_path)
    video.play()  # 自动播放新加载的视频
    return VideoPlayer(Video(video_path), (0, 0, screen_width, screen_height), preview_thumbnails=11)


vid = load_video(current_video_index)

# 中文字体
chinese_font_path = "C:/Windows/Fonts/simhei.ttf"

# 按钮属性定义
button_color = (255, 255, 255)  # 按钮颜色
button_hover_color = (0, 200, 0) # 回显颜色
button_text_color = (0, 0, 0) # 文字颜色
button_font = pygame.font.Font(chinese_font_path, 45)
button_alpha = 255  # 设置透明度 (0-255)
shadow_color = (125, 125, 125) # 阴影颜色

# 获取音量接口
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# 功能按钮矩形和文本
buttons = {
    # 左侧功能
    "next": {"rect": pygame.Rect(600, 540, 240, 180), "text": "节目 +", "visible": True, "num": 2},
    "prev": {"rect": pygame.Rect(600, 900, 240, 180), "text": "节目 -", "visible": True, "num": 3},
    "volume_up": {"rect": pygame.Rect(600, 1260, 240, 180), "text": "音量 +", "visible": True, "num": 4},
    "volume_down": {"rect": pygame.Rect(600, 1620, 240, 180), "text": "音量 -", "visible": True, "num": 5},
    # 右侧功能
    "drink_water": {"rect": pygame.Rect(2880, 540, 240, 180), "text": "喝水", "visible": True, "num": 6},
    "eat_food": {"rect": pygame.Rect(2880, 900, 240, 180), "text": "吃饭", "visible": True, "num": 7},
    "go_toilet": {"rect": pygame.Rect(2880, 1260, 240, 180), "text": "洗手间", "visible": True, "num": 8},
    "turn_off": {"rect": pygame.Rect(2880, 1620, 240, 180), "text": "关电视", "visible": True, "num": 9},

    # 功能菜单
    # pygame.Rect(1080, 540, 360, 1260)
    "medical_menu": {"rect": pygame.Rect(1080, 540, 360, 1260), "text": "医疗", "visible": True, "num": 10},
    "life_menu": {"rect": pygame.Rect(1680, 540, 360, 1260), "text": "生活", "visible": True, "num": 11},
    "fun_menu": {"rect": pygame.Rect(2280, 540, 360, 1260), "text": "娱乐", "visible": True, "num": 12},
}

# 医疗子菜单
medical_submenu = {
    # "visible": False属性可以不要，加上是控制属性的显示隐藏， 不加就是直接重绘制按钮
    "checkup": {"rect": pygame.Rect(1080, 720, 360, 180), "text": "体检", "visible": False, "num": 0},
    "medicine": {"rect": pygame.Rect(1080, 1080, 360, 180), "text": "药品", "visible": False, "num": 1},
    "return_medical": {"rect": pygame.Rect(1080, 1440, 360, 180), "text": "返回", "visible": False, "num": 2},
}

# 生活子菜单
life_submenu = {
    "change_clothes": {"rect": pygame.Rect(1680, 720, 360, 180), "text": "换衣服", "num": 0},
    "wash": {"rect": pygame.Rect(1680, 1080, 360, 180), "text": "洗漱", "num": 1},
    "return_life": {"rect": pygame.Rect(1680, 1440, 360, 180), "text": "返回", "num": 2},
}

# 娱乐子菜单
fun_submenu = {
    "walk": {"rect": pygame.Rect(2280, 720, 360, 180), "text": "散步","num": 0},
    "music": {"rect": pygame.Rect(2280, 1080, 360, 180), "text": "听音乐", "num": 1},
    "return_fun": {"rect": pygame.Rect(2280, 1440, 360, 180), "text": "返回", "num": 2}
}

# 唤醒功能菜单按钮矩形和文本
wake_button = {"rect": pygame.Rect(0, 0, 360, 360), "text": "功能菜单"}
wake_button["surface"] = button_font.render(wake_button["text"], True, button_text_color)

# 音量条位置
# volume_bar = {"rect": pygame.Rect(1680, 1900, 800, 200)}
volume_bar = {"rect": pygame.Rect(1460, 1900, 800, 150)}

# 图片索引
images = [
    "", "", image2, image3, image4, image5, image6, image7, image8, image9, image10, image11, image12
]
images_medical = [image10_1, image10_2, image13]
images_life = [image11_1, image11_2, image13]
images_fun = [image12_1, image12_2, image13]
# 渲染功能按钮文本
for button in buttons.values():
    button["surface"] = button_font.render(button["text"], True, button_text_color)

for button in medical_submenu.values():
    button["surface"] = button_font.render(button["text"], True, button_text_color)

for button in life_submenu.values():
    button["surface"] = button_font.render(button["text"], True, button_text_color)

for button in fun_submenu.values():
    button["surface"] = button_font.render(button["text"], True, button_text_color)

# 功能菜单是否被唤醒
menu_awake = False
medical_menu_open = False
life_menu_open = False
fun_menu_open = False
# 子菜单绘制完的状态
sub_button_finish = False

# 跟踪音量显示时间
show_volume = False
last_click_time = 0
volume_display_duration = 3  # 显示时间为3 秒


# 创建一个带有透明度的表面并在其上绘制按钮
def draw_button(surface, rect, text_surface, color, alpha):
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    button_surface.fill((*color, alpha))
    # 计算文本的水平和垂直坐标
    text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2))
    button_surface.blit(text_surface, text_rect.topleft)
    surface.blit(button_surface, (rect.x, rect.y))

#square : 图片在按钮表面的长宽
def draw_button3(surface, rect, text_surface, color, image, alpha, x, square, shadow_color, border_radius):
    # 创建一个支持透明度的按钮表面
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # 创建一个支持透明度的阴影表面
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # 绘制阴影 (在阴影表面上绘制阴影)
    shadow_offset = 8  # 阴影偏移量
    shadow_rect = shadow_surface.get_rect()
    pygame.draw.rect(shadow_surface, shadow_color, shadow_rect, border_radius=border_radius)

    # 设置阴影透明度
    shadow_surface.set_alpha(alpha)

    # 将阴影表面绘制到目标表面上
    surface.blit(shadow_surface, (rect.x + shadow_offset, rect.y + shadow_offset))

    # 绘制带有圆角的按钮
    pygame.draw.rect(button_surface, color, button_surface.get_rect(), border_radius=border_radius)

    # 调整图片大小以适应按钮的正方形区域
    image = pygame.transform.scale(image, (square, square))

    # 计算图片的左上角坐标，使图片的中心位于按钮表面的中心
    image_width, image_height = image.get_size()
    image_x = (rect.width - image_width) // 2
    image_y = (rect.height - image_height) // 2

    # 在按钮表面上绘制图片，-20 可以使图片稍微上移
    button_surface.blit(image, (image_x, image_y - 20))

    # 设置按钮表面的透明度
    button_surface.set_alpha(alpha)

    # 计算文本的水平和垂直坐标
    text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2 + x))
    button_surface.blit(text_surface, text_rect.topleft)

    # 将按钮表面绘制到目标表面上
    surface.blit(button_surface, (rect.x, rect.y))



result = 99

def RecieveFromSharedData():
    global result
    with open('results.txt', 'r') as f:
        # 读取所有内容
        received_data = f.read().strip()  # 去除末尾的空白字符（包括换行符）
        received_data=received_data.split(',')[0]
        # 输出读取的数据
        print(f"读取的数据: {received_data}")
        if(received_data != "----------------"):  #等待有效数据
            print(f"解析后的数据: ID:{received_data.split('+')[0]},res:{received_data.split('+')[1]},result:{received_data.split('+')[2]}")
            id = received_data.split('+')[0]
            res = received_data.split('+')[1]
            result = float(received_data.split('+')[2])
            print(type(result))

        if (result != 99):
            index = next((i for i, sublist in enumerate(table_list) if result in sublist), None)
            print(index)
            mouse_move(table_list[index][1], table_list[index][2], 1)

            mouse_click(table_list[index][1], table_list[index][2])
            mouse_move(3000, 200,0)
            time.sleep(2)

    # 每隔3s执行一次
    t = Timer(2, RecieveFromSharedData)
    t.start()

"""接收脑电数据结果"""
RecieveFromSharedData()

# Pygame应用程序的主循环
running = True

# 读取excel表进行分区背光的设置（左上功能菜单刺激位置）
change_mode_send(host_master, host_slave)
blink_mode_send(excel_topleft_right, excel_topleft_left, host_master, host_slave, mbrightness, background_brightness)

while running:
    # 从Pygame事件队列中获取所有事件
    events = pygame.event.get()
    for event in events:
        # 如果触发了退出事件（例如，关闭窗口），关闭视频并退出应用程序
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            running = False
            break

        # 检测鼠标点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # 检查唤醒功能菜单按钮
            if wake_button["rect"].collidepoint(mouse_pos):
                menu_awake = not menu_awake  # 切换功能菜单的状态
                if menu_awake:
                    # 功能菜单绘制完毕开始闪烁
                    blink_mode_send(excel_mid_right, excel_mid_left, host_master, host_slave, mbrightness, background_brightness)
                else:
                    # 读取excel表进行分区背光的设置（二级界面菜单刺激位置）
                    # 切换闪烁位置状态
                    blink_mode_send(excel_topleft_right, excel_topleft_left, host_master, host_slave, mbrightness, background_brightness)
                # 关闭所有子菜单
                medical_menu_open = False
                life_menu_open = False
                fun_menu_open = False

            # 检查功能按钮， 进行功能操作
            if menu_awake and not medical_menu_open and not life_menu_open and not fun_menu_open:
                for key, button in buttons.items():
                    if button["rect"].collidepoint(mouse_pos):
                        if key == "prev":
                            current_video_index = (current_video_index - 1) % len(video_files)
                        elif key == "next":
                            current_video_index = (current_video_index + 1) % len(video_files)
                        elif key == "volume_up":
                            current_volume = volume.GetMasterVolumeLevelScalar()
                            volume.SetMasterVolumeLevelScalar(min(current_volume + 0.1, 1.0), None)
                            show_volume = True
                            last_click_time = time.time()
                        elif key == "volume_down":
                            current_volume = volume.GetMasterVolumeLevelScalar()
                            volume.SetMasterVolumeLevelScalar(max(current_volume - 0.1, 0.0), None)
                            show_volume = True
                            last_click_time = time.time()
                        elif key == "turn_off":
                            vid.close()
                            pygame.quit()
                            running = False
                            change_mode_send(host_master, host_slave)  # 切换闪烁状态
                            break

                        # 重新加载视频（如果切换视频）
                        if key in ["prev", "next"]:
                            vid.close()
                            vid = load_video(current_video_index)
                            vid.video.play()  # 自动播放新加载的视频

                        # 打开医疗子菜单
                        if key == "medical_menu":
                            medical_menu_open = True
                            buttons["medical_menu"]["visible"] = False
                            for b in medical_submenu.values():
                                b["visible"] = True
                        elif key == "life_menu":
                            life_menu_open = True
                            buttons["life_menu"]["visible"] = False
                        elif key == "fun_menu":
                            fun_menu_open = True
                            buttons["fun_menu"]["visible"] = False
                        break

            # 检查医疗子菜单按钮
            if medical_menu_open:
                print('已经打开子菜单')
                for key, button in medical_submenu.items():
                    if button["visible"] and button["rect"].collidepoint(mouse_pos):
                        if key == "return_medical":
                            print('已经关闭子菜单')
                            medical_menu_open = False
                            buttons["medical_menu"]["visible"] = True
                            for b in medical_submenu.values():
                                b["visible"] = False
                        break

            # 检查生活子菜单按钮
            if life_menu_open:
                for key, button in life_submenu.items():
                    if button["rect"].collidepoint(mouse_pos):
                        if key == "return_life":
                            life_menu_open = False
                            buttons["life_menu"]["visible"] = True
                        break

            # 检查娱乐子菜单按钮
            if fun_menu_open:
                for key, button in fun_submenu.items():
                    if button["rect"].collidepoint(mouse_pos):
                        if key == "return_fun":
                            fun_menu_open = False
                            buttons["fun_menu"]["visible"] = True
                            # for b in fun_submenu.values():
                            #     b["visible"] = False 这些是可以不要的，控制二级菜单的隐藏属性
                        break

    # 用白色填充窗口背景
    win.fill("white")

    # 更新视频播放器的状态，传入事件列表
    vid.update([])
    # vid.update(events) 传入events就是点击后暂停

    # 在窗口中绘制视频帧
    vid.draw(win)  # 保持视频播放器的绘制

    # 绘制唤醒功能菜单按钮
    color = button_hover_color if wake_button["rect"].collidepoint(pygame.mouse.get_pos()) else button_color
    # draw_button(win, wake_button["rect"], wake_button["surface"], color, button_alpha)
    draw_button3(win, wake_button["rect"], wake_button["surface"], color, image1, button_alpha, 150, 300, shadow_color, 20)
    # 如果功能菜单被唤醒，绘制功能按钮
    if menu_awake:
        # if not medical_menu_open and not life_menu_open and not fun_menu_open:
        for button in buttons.values():
            if button["visible"]:
                color = button_hover_color if button["rect"].collidepoint(pygame.mouse.get_pos()) else button_color
                # draw_button(win, button["rect"], button["surface"], color, button_alpha)
                draw_button3(win, button["rect"], button["surface"], color, images[button["num"]], button_alpha, 68, 150, shadow_color, 20)

        # 如果医疗子菜单被唤醒，绘制医疗子菜单按钮
        if medical_menu_open:
            for button in medical_submenu.values():
                if button["visible"]:
                    color = button_hover_color if button["rect"].collidepoint(pygame.mouse.get_pos()) else button_color
                    # draw_button(win, button["rect"], button["surface"], color, button_alpha)
                    draw_button3(win, button["rect"], button["surface"], color, images_medical[button["num"]],button_alpha,68, 150, shadow_color, 20)

        # 如果生活子菜单被唤醒，绘制生活子菜单按钮
        if life_menu_open:
            for button in life_submenu.values():
                color = button_hover_color if button["rect"].collidepoint(pygame.mouse.get_pos()) else button_color
                # draw_button(win, button["rect"], button["surface"], color, button_alpha)
                draw_button3(win, button["rect"], button["surface"], color, images_life[button["num"]], button_alpha, 68,150, shadow_color, 20)

        # 如果娱乐子菜单被唤醒，绘制娱乐子菜单按钮
        if fun_menu_open:
            for button in fun_submenu.values():
                # if button["visible"]:
                color = button_hover_color if button["rect"].collidepoint(pygame.mouse.get_pos()) else button_color
                # draw_button(win, button["rect"], button["surface"], color, button_alpha)
                draw_button3(win, button["rect"], button["surface"], color, images_fun[button["num"]], button_alpha, 68,150, shadow_color, 20)

    # 显示音量水平
    if show_volume:
        current_volume = volume.GetMasterVolumeLevelScalar()
        pygame.draw.rect(win, (0, 0, 0), volume_bar["rect"])  # 黑色背景
        fill_width = int(volume_bar["rect"].width * current_volume)
        pygame.draw.rect(win, (0, 200, 0), pygame.Rect(volume_bar["rect"].x, volume_bar["rect"].y, fill_width,
                                                       volume_bar["rect"].height))  # 绿色音量条
        # 显示音量百分比
        volume_percentage_text = button_font.render(f"{int(current_volume * 100)}%", True, (0, 200, 0))
        # 音量条文本位置
        text_rect = volume_percentage_text.get_rect(
            center=(volume_bar["rect"].x + volume_bar["rect"].width + 50,
                    volume_bar["rect"].y + volume_bar["rect"].height // 2))
        win.blit(volume_percentage_text, text_rect)
        # 倒计时结束，音量条消失
        if time.time() - last_click_time > volume_display_duration:
            show_volume = False
    # 刷新窗口以显示最新内容
    pygame.display.update()

    # 等待16毫秒（大约每秒60帧）
    pygame.time.wait(16)
