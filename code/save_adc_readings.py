#	save_adc_readings.py - 12/9/2013. Written by David Purdie as part of the openlabtools initiative
#   Uses the adafruit python libraries to sample the ADS1115 at a user defined sampling frequency,
# 	saving results to a .txt file

from Adafruit_ADS1x15 import ADS1x15
import time
import numpy as np

pga = 6144					# Set full-scale range of programable gain amplifier (page 13 of data sheet), change depending on the input voltage range
ADS1115 = 0x01				# Specify that the device being used is the ADS1115, for the ADS1015 used 0x00
adc = ADS1x15(ic=ADS1115)	# Create instance of the class ADS1x15 called adc

# Function to print sampled values to the terminal
def logdata():

	print "sps value should be one of: 8, 16, 32, 64, 128, 250, 475, 860, otherwise the value will default to 250"
		
	frequency = input("Input sampling frequency (Hz):     ")	# Get sampling frequency from user
	sps = input("Input sps (Hz) :     ")						# Get ads1115 sps value from the user
	time1 = input("Input sample time (seconds):     ")			# Get how long to sample for from the user
	
	period = 1.0 / frequency		# Calculate sampling period

	datapoints = int(time1*frequency)		# Datapoints is the total number of samples to take, which must be an integer
	dataarray=np.zeros([datapoints,2])		# Create numpy array to store value and time at which samples are taken

	print "Press ENTER to start sampling"
	raw_input()
	
	time.sleep(1)							# Reduces jitter

	startTime=time.time()					# Time of first sample
	t1=startTime							# T1 is last sample time
	t2=t1									# T2 is current time
	
	for x in range (0,datapoints) :			# Loop in which data is sampled
			
			dataarray[x,1] = time.time()-startTime					# Time of sample
			dataarray[x,0]= adc.readADCSingleEnded(0, pga, sps)		# Take a sample

			while (t2-t1 < period) :		# Check if t2-t1 is less then sample period, if it is then update t2
				t2=time.time()				# and check again		
			t1+=period						# Update last sample time by the sampling period
					
	return (dataarray)

dataarray = logdata()						# Call function to log data

printchoice=raw_input("Do you want to save data to CSV (Y/N): ")	# Ask user if they want to save sampled values

if (printchoice == "Y" or "y") :
		np.savetxt('dataSamples.txt',dataSamples, fmt='%.3f', delimiter = ',')	# Save dataSamples to the file 'dataSamples.txt' using comma separated values
	
	
	

