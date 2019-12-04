import numpy as np
import matplotlib.pyplot as plt
import time
import socket
import math
import sys
from scipy import signal
import binascii
import struct

TARGET_IP = ''
TARGET_PORT = 8000
Data_length = 65536  # the data length for u64, 8bytes
UDP_MAX = 32768  # the max byte length for UDP
# ADC_Offset = 135  # The bias of the ADC chip
COLUMN_NUM = math.floor(UDP_MAX / 8)
TARGET = (TARGET_IP, TARGET_PORT)
folder = './data/'


# Socket part capture the data
class Data_Processor:
    global Data_length
    ss = 0
    Depth = math.floor(Data_length * 8 / UDP_MAX)
    stop_thread = False
    i = 0
    data = 0
    ADC_data_A = np.zeros(Data_length, dtype=np.int16)
    ADC_data_B = np.zeros(Data_length, dtype=np.int16)
    DAC_data = np.zeros(Data_length, dtype=np.uint16)
    Other = np.zeros(COLUMN_NUM, dtype=np.uint16)
    Trigger = np.zeros(Data_length, dtype=np.uint8)
    Up = np.zeros(Data_length, dtype=np.uint8)
    Dn = np.zeros(Data_length, dtype=np.uint8)
    CMP_in = np.zeros(Data_length, dtype=np.uint8)
    CMP_Delay = np.zeros(Data_length, dtype=np.uint8)
    data_ready = False
    temp_buffer = np.zeros([math.floor(Data_length*8/UDP_MAX),UDP_MAX],dtype=np.uint8)

    def __init__(self):
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ss.bind(TARGET)
        self.stop_thread = False

    def close(self):
        self.stop_thread = True

    def reset(self):
        self.i = self.Depth - 1;

    def run(self):
        if self.stop_thread:
            self.stop_thread = False

        while True:
            if self.stop_thread:
                self.ss.close()
                print('closed!!!!!!!!!!!!!')
                break
            else:
                self.ss.settimeout(1.0)
                try:
                    data, addrRsv = self.ss.recvfrom(UDP_MAX)
                except:
                    #print('Try failed')
                    pass
                else:
                    print(self.i)
                    if (self.data_ready == False):
                        if data[3] == 0xaa:
                            self.i = 0;

                    if data[3] == 0x55:
                        if self.i == self.Depth - 1:
                            self.data_ready = True

                    self.temp_buffer[self.i,:] = np.frombuffer(data,dtype=np.uint8)
                    self.i = (self.i + 1) % self.Depth


                    # Debug_test = self.DAC_data
                    # print(Debug_test)
                    # break

    def save_data(self):
        pass

    def shot_wave(self):
        pass

    def get_shot(self):
        return self.DAC_data

    def if_ready(self):
        return self.data_ready

    def get_data(self):
        data = self.temp_buffer.tobytes();
        self.data = np.frombuffer(self.temp_buffer, np.uint16)
        data_temp = np.reshape(self.data, [Data_length, 4])
        ADC_data_A = data_temp[:, 0]
        ADC_data_B = data_temp[:, 1]
        DAC_data = data_temp[:, 2]
        Other = data_temp[:, 3]
        CMP_Delay = Other % 2
        Dn = (Other // 2) % 16
        CMP_in = (Other // 2 ^ 5) % 2
        Trigger = (Other // 2 ^ 6) % 2
        Up = (Other // 2 ^ 7) % 2
        self.data_ready = False
        return ADC_data_A - np.mean(ADC_data_A), ADC_data_B - np.mean(ADC_data_B), DAC_data / (
                2 ^ 13), CMP_Delay, Dn, Trigger, Up, CMP_in
    # def BitReverse(self, Source, bitSize):
    #     ret = np.zeros(len(Source), np.uint8)
    #     for index in range(len(Source)):
    #         int_data = (Source[index])
    #         binary = bin(int_data)
    #         reverse = binary[-1:1:-1]
    #         reverse = reverse + (bitSize - len(reverse))*'0'
    #         ret[index] = reverse
    #     return ret
    #
    # def ByteReverse(self, Source):
    #     ret = np.zeros(len(Source), np.uint16)
    #     for index in range(len(Source)):
    #         ByteReverse = (Source[index])[::-1]
    #         ret[index] = ByteReverse.encode('hex')
    #     return ret
