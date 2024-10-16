from scipy.signal import butter, filtfilt

def filter(fs, window_data):
    notch_freq = 50  # 震荡频率
    notch_width = 1  # 限波宽度

    # 计算限波滤波器系数
    nyq = 0.5 * fs
    low = (notch_freq - notch_width/2) / nyq
    high = (notch_freq + notch_width/2) / nyq
    b_notch, a_notch = butter(2, [low, high], btype='bandstop')

    # 定义带通滤波器参数
    lowcut = 6  # 低截止频率
    highcut = 90  # 高截止频率
    order = 4  # 滤波器阶数

    # 计算带通滤波器系数
    low = lowcut / nyq
    high = highcut / nyq
    b_bandpass, a_bandpass = butter(order, [low, high], btype='band')

    # 对每个通道进行限波滤波
    for i in range(window_data.shape[0]):
        window_data[i, :] = filtfilt(b_notch, a_notch, window_data[i, :])

    # 对每个通道进行带通滤波
    for i in range(window_data.shape[0]):
        window_data[i, :] = filtfilt(b_bandpass, a_bandpass, window_data[i, :])

    return window_data