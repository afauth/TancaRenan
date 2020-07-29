import math
import statistics
import time
import itertools 
import pandas as pd
from datetime import datetime
from array import array
import numpy as np
from statistics import mean 
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from ROOT import TCanvas,TGraph, gApplication, TTree, TFile, TDatime, gStyle,TGraphErrors, TLegend

###########################################################################
# TACA data selecting#
###########################################################################

input_year = input('Year: ')
Y = int(input_year)

############# List of files to analyse  ####################################
print(" ")

#Detector data
data = open('/home/renan/Mestrado/Data/'+str(Y)+'/allfiles.txt', 'r+')  
adress = '/home/renan/Mestrado/Data/'+ str(Y) + '/'
line = data.read().splitlines() #read lines getting rid of \n
size = len(line)  
tri = []    
signal = []
m = 1
while m != 3:
	if m == 1:
		print('First Processing ...')
	if m == 2: 
		print('Second Processing ...')
		print(" ")
	
	for i in range(size):
	
		file = open(adress+line[i],'r+')
		line_file = file.readlines()
		size_file = len(line_file)
		if m == 2:
			print('Reading file '+line[i])
				
		for j in range(size_file):
		
			if len(line_file[j].split())==9 and j>3: # select info from lines with counting	
				
				if m == 1:
					if float(line_file[j].split()[8]) > 1000 and float(line_file[j].split()[8]) < 3000:
						tri.append(float(line_file[j].split()[8]))
				
				else:
					if float(line_file[j].split()[8]) >= tri_m-n*MAD and float(line_file[j].split()[8]) <= tri_m+n*MAD:
						N = float(line_file[j].split()[8])
						epoch = float(line_file[j].split()[0])/1000
						line_signal = epoch, N
						signal.append(line_signal)
					
	if m == 1:
		#Calculate MADimport itertools 
		tri_m = statistics.mean(tri)
		d_tri = []
		for k in range(len(tri)):
			d_tri.append(abs(tri[k]-tri_m))			
		d_tri.sort()
		MAD = statistics.median(d_tri)
		print(" ")
		print("Mean Count/s = ", tri_m, "; MAD = ", MAD)  
		print(" ")
		input_n = input('Choose n ( n*MAD) =  ')
		n = float(input_n)
	
	m += 1

print("Writting info file ... ")
F = open('/home/renan/Mestrado/Data/'+str(Y)+'/data'+ str(Y) +'.txt', 'w')
for i in range(len(signal)):
	F.write("%0.4f %0.1f\n" % (signal[i][0], signal[i][1]))
F.close()
print("Done!")

