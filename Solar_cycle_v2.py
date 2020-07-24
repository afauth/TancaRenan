#! /usr/bin/python3.5

############################### Library ################################### 
import os
import sys
import math
import statistics
import time
import pandas as pd
import numpy as np
from array import array
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from ROOT import TCanvas,TGraph,TGaxis, gApplication,gPad, TTree, TFile, TDatime, gStyle,TGraphErrors, TLegend, kBlue, kRed, kWhite, kGreen
###########################################################################
# Code to verify the 11 years cicle using tanca and neutrons data
###########################################################################

def main():	
	
############################ Neutrons ################################### 
	
	print('Processing neutron data:')
	data_n = open('/home/renan/Mestrado/Data/NMDB/TSMB.txt', 'r+')
	
	line = data_n.readlines()
	size = len(line) 
	neutron_time = []
	neutron_count = []
	
	entries = 0   
	day0 = 1
	freq = []
	
	# loop to calculate dayle rate
	for j in range(size):
		
		if j > 23 and len(line[j].split()) == 2:
		
		 	date = (line[j].split()[0]).split("-")
		 	year = int(date[0])
		 	month = int(date[1])
		 	day = int(date[2])
		 	
		 	ti = (line[j].split()[1]).split(":")
		 	cout = float(ti[2].split(";")[1])

			# selecting date from a same day 
		 	if day==day0:
		 		T0 = TDatime(year,month,day,12,0,0)
		 		T1 = int(T0.Convert())
		 		freq.append(cout)
		 	else:
		 		if len(freq) != 0:
		 			neutron_time.append(float(T1))
		 			neutron_count.append(statistics.mean(freq))
					
		 			freq = []
		 			day0 = day
		 			entries += 1
	
	print('Entries: ', entries)
	print('Done!')
	
###################################### Muons #########################################

	print('Processing muon data:')
	
	# Approximate maximum and minimum signal without interference
	FILTER_min = 1500
	FILTER_max = 3000

	adress = '/home/renan/Mestrado/Data/'
	file = '/allfiles.txt'  # list with the files that are going to be used 
	
	year_ini = 2016
	period = 4 #years

	m = 0
	freq = []
	tri = []

	muon_count = []
	muon_time = []
	

	while m != period:
		year = year_ini + m
		print(' ')
		print('**************************')
		print ('Selecting data from ', year)
		print('**************************')
		print(' ')
		# files for each year are in different folders and in each folder there is one file named allfiles.txt
		path = adress +  str(year) + file 
		data = open(path, 'r+') # it is read the file alldata.txt 
		line = data.read().splitlines() # read lines getting rid of \n
		size = len(line)  
	 
		for i in range(size):
			tanca = open(adress +  str(year) + '/' + line[i])
			print('Reading file '+line[i])
			line_tanca = tanca.readlines()
			size_tanca = len(line_tanca)
			
			for j in range(size_tanca):
				
				# the information from the tanks begins at the fourth line and has 10 columns 
				if len(line_tanca[j].split())==9 and j>3: 
					Time = float(line_tanca[j].split()[0])
					
					
					if len(tri) == 0: # initial time if none data was already selected
						Time_ini = Time
					
					SCouple = float(line_tanca[j].split()[6]) #selecting the data from D13
					if SCouple >= FILTER_min and SCouple <= FILTER_max:
						tri.append(SCouple)
				
				
						
			if len(tri) != 0: # after a Xtank.txt was read
				Time_fin = Time # last time of the file
				T = (Time_ini + Time_fin)/2000
				C = statistics.mean(tri) # mean count
				
				
				muon_time.append(T)   # put the result of the average time on a list
				muon_count.append(C)  # put the mean count on other list
				
			
			tri = [] #reseting		
		m += 1 
		
####################### Putting togheter muon and neutron data ##############################

	# the first date from muons data must coincide with the last neutrons date
	
	dt_ref = time.gmtime(int(muon_time[0])) #fst tanca date
	
	for i in range(len(neutron_time)):
		dt = time.gmtime(int(neutron_time[i]))
		if dt_ref[0] == dt[0] and dt_ref[1] == dt[1] and dt_ref[2] == dt[2]: # Checking were the year/month/day is the same on both
			line_ref = i #this is the last position of neutrons list before the time coincidence
			break
		
	mean_neutron = statistics.mean(neutron_count) # average of neutrons count
	mean_muon = statistics.mean(muon_count)       # average of muons count
	
	
	# Making a convertion rate, with (relative neutron rate)/(relative muon rate at the first date)
	rate = (neutron_count[line_ref]/mean_neutron)/(muon_count[0]/mean_muon) 
	
	# List were it will be added the 'converted' data
	muon_data = []
	neutron_data = []
	
	for i in range(0, line_ref):
		line_neutron = neutron_time[i], neutron_count[i]/mean_neutron #relative rate
		neutron_data.append(line_neutron)
		
	for j in range(len(muon_count)):
		line_muon = muon_time[j], rate*muon_count[j]/mean_muon #conversion of relative rate
		muon_data.append(line_muon)
	

	# Arranging to mothly average 
	
	all_data = []
	month_neutron = time.gmtime(int(neutron_data[0][0]))[1]
	neutron_info = []
	neutron_dt = []
	neutron = []
	for k in range(len(neutron_data)):
		if time.gmtime(int(neutron_data[k][0]))[1] == month_neutron:
			neutron_info.append(float(neutron_data[k][1]))
			neutron_dt.append(int(neutron_data[k][0]))
			
		else:
			if len(neutron_info) != 0:	
				line_n = statistics.mean(neutron_dt), statistics.mean(neutron_info)
				neutron.append(line_n)
				all_data.append(line_n)
				month_neutron = time.gmtime(int(neutron_data[k][0]))[1]
				neutron_info = []
				neutron_dt = []	
	
	
	month_muon = time.gmtime(int(muon_data[0][0]))[1]
	muon_info = []
	muon_dt = []
	muon = []
	for k in range(len(muon_data)):
		if time.gmtime(int(muon_data[k][0]))[1] == month_muon:
			muon_info.append(float(muon_data[k][1]))
			muon_dt.append(float(muon_data[k][0]))
			
		else:
			if len(muon_info) != 0:	
				line_m = statistics.mean(muon_dt), statistics.mean(muon_info)
				muon.append(line_m)
				all_data.append(line_m)
				month_muon = time.gmtime(int(muon_data[k][0]))[1]
				muon_info = []
				muon_dt = []				
	
	print (' ')
	print('Cosmic Ray rate:')
	for k in range(len(all_data)):
		print (time.gmtime(int(all_data[k][0]))[1], '/', time.gmtime(int(all_data[k][0]))[0], ': ', all_data[k][1])


############################### Selecting sunspot data ################################################

	file_sun = open('/home/renan/Mestrado/Data/Sunspot/sunspot.txt', 'r+')
	line_sun = file_sun.readlines()
	s_sun = len(line_sun)
	
	print (' ')
	print('Number of sunspot:')
	sunspot = []
	for i in range(s_sun):
		if i > 9:
			for j in range(len(line_sun[i].split())):
				if j > 0:
					T = TDatime(int(line_sun[i].split()[0]),j,15,12,0,0)
					T1 = int(T.Convert())
					line_s = T1, float(line_sun[i].split()[j])
					if int(line_sun[i].split()[0])>=2010 and int(line_sun[i].split()[0])<2019:
						sunspot.append(line_s)
					print(j, '/', line_sun[i].split()[0], ': ', float(line_sun[i].split()[j]))
							 	
################################### Plotting ####################################################
	
	data =   np.array(all_data)
	sun = np.array(sunspot)
	m = np.array(muon)
	
	
	y = data[:,1]
	x = np.zeros(shape=(len(all_data),1), dtype='datetime64[s]')
	# converting the time to UTC at x axis
	for i in range(len(all_data)):
		d = time.strftime('%Y-%m-%d' , time.localtime(int(all_data[i][0])))
		dt = datetime.strptime(d,"%Y-%m-%d").date()
		x[i] = dt
		
		if int(all_data[i][0])==int(muon[0][0]):
			ref = i		
	
	ref_loop = 0 
	tcd = 'n'

	fig,ax = plt.subplots()
	lines = []
	l1 = 'n'
	l2 = 'n'
	
	for x1, x2, y1,y2 in zip(x, x[1:], y, y[1:]):
	
		if ref_loop >= ref:  # if the date is higher than the first date, than it is muon data and it'll be plotted a blue line
			ax.plot([x1, x2], [y1, y2], 'b')
			l1 = 'y'
		else:
			ax.plot([x1, x2], [y1, y2], 'k') 
			l2 = 'y'
		
		if l1 == 'y' and len(lines) == 0: 
			line1, = ax.plot([x1, x2], [y1, y2], 'k') #legend
			lines.append(l1)
		if l2 == 'y' and len(lines) == 1:
			line2, = ax.plot([x1, x2], [y1, y2], 'b') #legend
			lines.append(l2)
		ref_loop += 1
		
	print(lines)	
	ax.legend([line1, line2], ['TSMB Data', 'Tanca Data'], loc='upper left', frameon=True) #legend format
	
	ax = plt.gca()
	formatter = mdates.DateFormatter("%b/%Y")
	ax.xaxis.set_major_formatter(formatter)
	ax.set_xlabel("Year")
	ax.set_ylabel("Cosmic Ray Relative Rate")
	
	
	# then, plotting the sunspot number
	ys = sun[:,1]
	xs = np.zeros(shape=(len(sun),1), dtype='datetime64[s]')
	for i in range(len(sun)):
		d = time.strftime('%Y-%m-%d' , time.localtime(int(sunspot[i][0])))
		dt = datetime.strptime(d,"%Y-%m-%d").date()
		xs[i] = dt	
	
	
	ax2=ax.twinx() #use the same x axis
	ax2.plot(xs, ys, "r", label = 'Sunspot Number')
	ax2.legend(loc='upper right', frameon=True)
	ax2.set_ylabel("Sunspot number",color="r")
	# making a second y axis
	for tl in ax2.get_yticklabels():
   		tl.set_color('r')
	
	
	plt.show()
		
		
main()
