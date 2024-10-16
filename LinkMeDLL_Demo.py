# --*-- coding:utf-8 --*--


# load dll
import ctypes
import threading

import time

# load dll as my_dll
my_dll = ctypes.CDLL("./LinkMe.dll")

# init functions of dll
my_dll.dataProtocol.argtypes = (ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)
my_dll.dataProtocol.restype = ctypes.c_int

my_dll.getElectricityValue.restype = ctypes.c_int

my_dll.getFallFlag.argtypes = (ctypes.POINTER(ctypes.c_int),)

my_dll.getData.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_double))

my_dll.getDataCurrIndex.argtypes = (ctypes.POINTER(ctypes.c_long),)

my_dll.getImpedance.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_double))

# 初始化变量
freq_list = [12, 13, 14, 15, 16, 17, 18]  # 频率列表
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


# 加载dll解析linkme数据
def makeDataWithShape(data):
    data_array = (ctypes.c_ubyte * len(data))(*data)
    # 解析数据
    dataSize = my_dll.dataProtocol(data_array, len(data))

    print(dataSize)
    if dataSize > 0:
        # 读取linkme电量
        elecValue = my_dll.getElectricityValue()
        print("电量是： ", elecValue)

        # 读取佩戴状态，
        # int * fallFlag = my_dll.getFallFlag();
        flag = [-1, -1, -1, -1, -1, -1, -1, -1]
        fallFlag = (ctypes.c_int * 8)(*flag)
        my_dll.getFallFlag(fallFlag)
        flag = [fallFlag[i] for i in range(len(flag))]

        print("new fallFlag = ", flag)
        # 通过指针访问整数
        # int_size = ctypes.sizeof(ctypes.c_int)
        # print("导联值， 0：佩戴； 1： 脱落。")
        # for i in range(8):
        #     element_address = ctypes.addressof(int_pointer.contents) + i * int_size
        #     element_pointer = ctypes.cast(element_address, ctypes.POINTER((ctypes.c_int)))
        #     fallFlag.append(element_pointer.contents.value)
        #     # 打印元素的值
        #     print(f"导联 {i} 的值: {element_pointer.contents.value}; address {i} : {element_address}")
        # print()

        # 读取阻抗值，
        # int * fallFlag = my_dll.getFallFlag();
        impedance = [-1, -1, -1, -1, -1, -1, -1, -1]
        impedanceData = (ctypes.c_double * 8)(*impedance)
        my_dll.getImpedance(1000, impedanceData)
        impedanceValue = [impedanceData[i] for i in range(len(impedance))]
        print("new impedanceData = ", impedanceValue)

        # 获取电位数据
        # double** eegData = getData();
        eegData = my_dll.getData()
        # 将返回值转换为二维数组
        data_value = [[eegData[i][j] for j in range(9)] for i in range(dataSize)]
        print("行数 = ", len(data_value))
        print("列数 = ", len(data_value[0]))
        # for i in range(len(data_value)):
        #     print("数据是: ", end=" ")
        #     for j in range(9):
        #         print(" %.14f" % data_value[i][j], end=", ")
        #     print()
        # print()

        # 获取当前数据索引

        DataCurrIndex = [-1 for i in range(int(dataSize / 5))]
        new_DataCurrIndex = (ctypes.c_long * len(DataCurrIndex))(*DataCurrIndex)

        my_dll.getDataCurrIndex(new_DataCurrIndex)
        data_current_index = [new_DataCurrIndex[i] for i in range(len(new_DataCurrIndex))]
        print("数据包序号前15是： ", end=" ")
        for i in range(len(new_DataCurrIndex)):
            print(data_current_index[i], end=", ")
        print()
    else:
        print("数据长度不够, 没有脑电数据", dataSize)


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
    port = "COM8"
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
        ser.close();
    if ser.isOpen():  # 判断串口是否关闭
        print("串口未关闭。")
    else:
        print("串口已关闭。")


if __name__ == "__main__":
    # 读取离线数据
    # data = readOffLineData("../offlinedata/testData2.txt")
    #
    # for i in range(20):
    #     print(data[i], end= ", ")
    #
    # print()
    #
    # # 解析数据
    # makeDataWithShape(data)

    # 打开串口
    ser = openSerial()
    # 开启子线程接收数据到data_buffer缓冲区
    t = threading.Thread(target=receiveData, args=(ser, is_received_data))
    # 开启线程
    t.start()

    index = 0
    # 接收数据, 接受的数据存放在data_buffer中
    while is_received_data:
        # receiveData(data_buffer, ser, is_received_data)
        each_length = 10 * 136

        if data_buffer != []:
            data = data_buffer[0: each_length]
            with lock:
                data_buffer = data_buffer[each_length:]
            # 解析数据
            # data = []
            makeDataWithShape(data)
            index += 1

        if index > 1000:
            is_received_data = False
            break

    # 关闭线程
    is_received_data = False
    # 关闭串口
    closeSerial(ser)
