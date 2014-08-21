#!/usr/bin/env python

#	DAQ_GUI.py - 12/9/2013. Written by David Purdie as part of the openlabtools initiative
#   A GUI that performs semi real time plotting (updated every 10s) of data sampled from the 
#   ADS1115 chip using the Adafruit Python libraries
#   Partly adapted from: 
#	http://hardsoftlucid.wordpress.com/various-stuff/realtime-plotting/
# 	http://code.activestate.com/recipes/82965-threads-tkinter-and-asynchronous-io/  

import pylab
import Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tkMessageBox
import time
from Adafruit_ADS1x15 import ADS1x15
import numpy as np
import threading
import Queue

class realtimeplot(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()

	def initialize(self):								# Create Tkinter interface
		
		self.sample = 0									# This is a flag used to determine if we are sampling or not
		self.period = 1									# Default sampling period to 1 second
		self.values = np.zeros(shape=(0,2))				# Array to store data in
		self.data_queue = Queue.Queue()					# Queue to share data between the two threads
		
		self.fig = pylab.figure(1)						# Create pylab plot
		self.ax = self.fig.add_subplot(111)
		self.ax.grid(True)
		self.ax.set_title("Voltage Plot")
		self.ax.set_xlabel("Time (seconds)")
		self.ax.set_ylabel("Voltage (mV)")
		self.ax.axis([0,100,0,3500])
		self.line1=self.ax.plot(0,0,'r-')
		
		self.canvas = FigureCanvasTkAgg(self.fig, master=self)											# Create canvas to 
		self.canvas.show()																				# embed pylab plot 
		self.canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)						# in Tkinter
			
		quit_button = Tkinter.Button(master=self, width=30, height=1,font=('Calibri', 10),
									 text='Quit', bg = 'light grey', command=self._quit)				# Quit GUI button
												   
		quit_button.pack(side=Tkinter.BOTTOM)
		
		stop_button = Tkinter.Button(master=self, width=30, height = 1, font=('Calibri', 10),			# Stop sampling button
									 text='Stop Sampling and Save Data to File', fg='black',
									 bg='light grey', command = self.stop_pressed)
		stop_button.pack(side=Tkinter.BOTTOM)
		
		self.fileName = Tkinter.StringVar()																# Entry box for user
		Tkinter.Entry(master=self, width = 20, textvariable = self.fileName).pack(side=Tkinter.BOTTOM)	# to input desired file
																										# name which is stored in
		fileNameLabel = Tkinter.Label(master=self, bg ='light grey',									# variable fileName
								      text='Enter File Name')					
		fileNameLabel.pack(side=Tkinter.BOTTOM)
		
		start_button = Tkinter.Button(master=self, width = 30, height = 1, font=('Calibri', 10),		# Start sampling button
								   text='Start Sampling', fg='black', bg="light grey", 
								   command = self.start_pressed)
		start_button.pack(side=Tkinter.BOTTOM)
		
		self.numSamples = Tkinter.Scale(master=self,label="Number of samples to display in plot: ",			# Create slider to
									bg = 'light grey', from_=10, to=3600,sliderlength=60,				# set number of samples
									length=self.ax.get_frame().get_window_extent().width,				# to show in plot
									orient=Tkinter.HORIZONTAL)
		self.numSamples.pack(side=Tkinter.BOTTOM)
		self.numSamples.set(100)
		
		frequpdate = Tkinter.Button(master=self, width = 30, height = 1, font=('Calibri', 10),			# Button to update 
									text='Update Sampling Frequency', fg='black', bg='light grey',      # sampling frequency
									command = self.freq_pressed)
		frequpdate.pack(side=Tkinter.BOTTOM)
		
		self.freqget = Tkinter.StringVar()																# Create string to store
		Tkinter.Entry(master=self, width = 20, textvariable = self.freqget).pack(side=Tkinter.BOTTOM)	# frequency value from
																										# user input
		freqlabel = Tkinter.Label (master=self, bg ='light grey',										# Create label above
								   text='Enter Sampling Frequency (Hz) - Max 16Hz:')					# frequency input
		freqlabel.pack(side=Tkinter.BOTTOM)
		
		self.frequency_now = Tkinter.StringVar()														# Create string to store
		current_freq_label = Tkinter.Label(master=self, font=('Calibri', 20), fg = 'blue', 				# current sample															
										   bg='light grey', wraplength = 3000,							# frequency and label to
										   textvariable = self.frequency_now)							# display the frequency
		current_freq_label.pack(side=Tkinter.BOTTOM)
				
		current_freq_title = Tkinter.Label(master=self, font=('Calibri', 10), fg='black',				# Create title above 
										   bg='light grey', wraplength = 1000,							# current sampling 
										   text = 'Current Sampling Frequency (Hz) ')					# frequency label
		current_freq_title.pack(side=Tkinter.BOTTOM)
		
		self.sample_value_string = Tkinter.StringVar()													# Create label to display
		sample_value = Tkinter.Label(master=self, font=('Calibri', 50), fg = 'red', bg="light grey",	# last adc conversion 
									 wraplength = 3000, textvariable = self.sample_value_string)		# result
		sample_value.pack(side=Tkinter.BOTTOM)
		
		sample_value_label = Tkinter.Label(master=self, font=('Calibri', 15), fg = 'black',				# Create title above
										   bg='light grey', wraplength = 1000,							# last conversion result
										   text = 'Voltage reading (mV)')								# label
		sample_value_label.pack(side=Tkinter.BOTTOM)
		
		self.frequency_now.set("1.0")			# Set initial output of last adc sample to 0, and current sapling 
		self.sample_value_string.set("0")		# frequency to 1Hz
		
	def _quit(self):																	# Function called by quit GUI button
		if self.sample == 1:
			self.sample = 0
		if tkMessageBox.askokcancel('Quit?', 'Are you sure you want to quit?'):
			self.quit()    
			self.destroy() 
		
	def start_pressed(self):															# Function called by start sampling button
		if self.sample == 0:
				self.sample = 1	
				
				# Begin adc conversions on pin A0, pga = 4096, sps =16. If you want to use a different 
				# input pin, input voltage range, or sampling rate higher then 16Hz then change this line
				adc.startContinuousConversion(0, 4096, 16)
				# self.t_last represents the time of the last sample												
				self.t_last=time.time()				
				self.StartTime = self.t_last
				
				# Create thread samples ADC values and places them in self.data_queue,
				# this queue is used to share the results between the sampling thread and
				# the Tkinter thread
				self.thread1 = threading.Thread(target=self.SampleADC)			
				self.thread1.start()
				
				self.after(10000, self.RealtimePloter)
				self.after(20, self.ProcessQueue)

	def stop_pressed(self):																# Function called by stop sampling button
		if self.sample == 1:
			if tkMessageBox.askokcancel('Stop Sampling?', 'Are you sure you want to Stop Sampling? '):
				self.sample = 0
				
				# Find the string that the user has inputed into the "enter file name" input
				dataFile = self.fileName.get()
				# If nothing has been input to this box, save the file as "dataFile.txt
				if (len(dataFile) == 0):
					dataFile = "dataFile"
				# Add the user input file name to the directory where we will save the file
				dataFile=''.join(["/home/pi/Documents/",dataFile, ".txt"])
				# Try to save the data to file
				try:
					np.savetxt(dataFile, self.values, fmt='%.1f', delimiter=' , ')	
				# If this fails save the file under a default name "DataFile.txt" so the data isn't lost!
				except:
					np.savetxt("/home/pi/Documents/BreadLab/breadDataFile.txt", self.values, fmt='%.1f', delimiter=' , ')
				
	def freq_pressed(self):																# Function called by update frequency
		frequency = float(self.freqget.get())											# button
		self.period = 1.0 / frequency
		self.frequency_now.set(frequency)
				
	def ProcessQueue(self):																# Process data queue, called 
		if (self.sample == 1):															# every 20ms
			
			# while there is still data in the queue:
			while self.data_queue.qsize():
				# try to take data out of the queue
				try:
					queue_values = self.data_queue.get(0)
				     # Append what we have taken from the queue to the numpy array (self.values) storing our sampled data values / times
					self.values = np.append(self.values, [queue_values], 0)	
					# Update the tkinter label displaying the ads1115 output, we must do this here and not in the sampling function as we must
					# keep tkinter in the same thread  
					self.sample_value_string.set(queue_values[0])			
				except Queue.Empty:
					pass
			self.after(20, self.ProcessQueue)
			
	def RealtimePloter(self):															# Update plot function, called every
																						# 10 seconds
		if (self.sample == 1):
			self.after(10000,self.RealtimePloter)
			# numSamples.get() is the value of the slider in the GUI, if the total number of samples
			# is less then this value just plot all the samples instead
			NumberSamples=min(len(self.values),self.numSamples.get())				
			CurrentXAxis = self.values[-NumberSamples:,1]						# Take the last NumberSamples elements from the
			CurrentYAxis = self.values[-NumberSamples:,0]						# self.values array and set as x and y axis
			self.ax.axis([CurrentXAxis.min(),CurrentXAxis.max(),				# Set axis limits, we set the y scale to the max and min sampled values																
						  max(0,CurrentYAxis.min()-100),						# +/- 100
						  CurrentYAxis.max()+100])			
						  
			self.line1[0].set_data(CurrentXAxis,CurrentYAxis)					# Set the line dispalying the data
			self.canvas.draw()													# Update the plot
			
	def SampleADC(self):																# Function to sample adc, this runs
		while (self.sample):															# in a separate thread
			if (time.time() - self.t_last > self.period):								# Only sample if the current time is greater then the
																						# last sample time by an amount equal to the sampling period
				LastSample = round(adc.getLastConversionResults(),1)
				samples = np.array([LastSample, round(time.time()-self.StartTime,2)])	# Create 1x2 numpy array with the sampled value and sample time
				self.data_queue.put(samples)											# Add the array to self.data_queue
				self.t_last += self.period												# Update the time of the last sample by the sampling period

if __name__ == "__main__":
	ADS1115 = 0x01						# Initialize adc
	adc = ADS1x15(ic=ADS1115)
	app = realtimeplot(None)
	app.title('Real Time Plot')
	app.configure(bg = 'light grey')
	app.mainloop()

