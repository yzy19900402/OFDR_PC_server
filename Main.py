import Data_Processor as dp
import numpy as np
import matplotlib.pyplot as plt
import time
import socket
import sys
import multiprocessing
import threading
from scipy import signal

name = 'temp'
flag = False
lflag = False
inst = dp.Data_Processor()
ymax = 0
fs = 125e6
Data_length = 65536
stop_thread = False


def on_key_press(event):
	global flag
	global lflag
	global ymax
	global stop_thread
	if event.key in 'Q':
		inst.close()
		stop_thread = True
	if event.key in 's':
		inst.save_data()
	if event.key in 'c':
		inst.shot_wave()
	if event.key in 'r':
		inst.reset()


# if event.key in 't':
# 	lflag = not lflag;
# 	inst.t_deconv()
# if event.key in 'v':
# 	flag = not flag;
# if event.key in 'r':
# 	ymax = 0;
# if event.key in 'u':
# 	inst.update_reference()
# if event.key in '+':
# 	inst.inc_bw()
# if event.key in '-':
# 	inst.dec_bw()

def draw_run():
	# t = list(range(0, len(self.Trigger) - 1)) / fs
	# plt.plot(t * 1e3, self.ADC_data_A)
	# plt.xlabel("Time(ms)")
	# plt.ylabel("Voltage")
	# plt.title("ADC channel A signal")
	# plt.grid()
	# plt.show()

	global lflag
	global flag
	global stop_thread
	global ymax
	print('started\n')
	fig = plt.figure()
	fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
	fig.canvas.mpl_connect('key_press_event', on_key_press)
	plt.ion()
	index = np.arange(0, Data_length)
	t_us = index / fs * 1e6
	plt.draw()
	while True:
		if stop_thread:
			break
		if not inst.if_ready():
			continue
		plt.clf()
		# inst.socket_run();
		if not lflag:
			pass  # plt.ylim([0, 10])
		else:
			pass  # plt.ylim([0, ymax])
		# plt.xlim([0,6.4])
		plt.xlabel('Time(us)')
		plt.ylabel('Voltage(mV)')
		ADC_data_A, ADC_data_B, DAC_data, CMP_Delay, Dn, Trigger, Up, COMP_in = inst.get_data()
		if flag:
			plt.plot(t_us, DAC_data, linewidth=0.8)
			plt.plot(t_us, inst.get_shot(), linewidth=0.8)
		else:
			# print(DAC_data)
			plt.subplot(2, 2, 1)
			plt.plot(t_us, DAC_data/4.9, linewidth=0.8)
			plt.grid()
			plt.subplot(2, 2, 2)
			plt.plot(t_us, ADC_data_A, linewidth=0.8)
			plt.grid()
			f, t, Zxx = signal.stft(ADC_data_A, fs, nperseg=1000, noverlap=900)
			plt.subplot(2, 2, 3)
			plt.pcolormesh(t * 1e6, f / 1e6, np.abs(Zxx))
			plt.title('Short-time fft')
			plt.ylabel('Frequency(MHz)')
			plt.xlabel('Time(\u03BCs)')
			plt.grid()
			plt.ylim(0,30)
			plt.subplot(2, 2, 4)
			freq = np.fft.fftfreq(Data_length, d=1/fs)
			sp = np.fft.fft(ADC_data_A)
			plt.plot(freq/1e6, np.abs(sp)/Data_length)
			plt.xlabel('Frequency(MHz)')
			plt.xlim(0, 30)
			plt.grid()


		if lflag:
			temp = np.max(DAC_data)
			if temp > ymax:
				ymax = temp
		plt.draw()
		plt.pause(0.01)


if __name__ == '__main__':
	ss_t = threading.Thread(target=inst.run, args=())
	ss_t.setDaemon(True)
	ss_m = threading.Thread(target=draw_run, args=())
	ss_m.setDaemon(True)
	ss_t.start()
	ss_m.start()
	ss_t.join()
	ss_m.join()
