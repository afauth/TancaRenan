#! /usr/bin/python3.5

import os
import sys
import math
import statistics
import time
from time import gmtime
import pandas as pd
import random
from datetime import datetime
from array import array
import numpy as np
from ROOT import TCanvas,TGraph, gApplication, TTree, TFile, TDatime, gStyle

###########################################################################
# The aim of this code is to select the data of pressure for a period from
# a file .dat given by Cepagri
###########################################################################

def main():

############# List of files to analyse  ####################################

	data = open('/home/renan/Mestrado/Data/2019/unicamp_2019.dat', 'r+')
	line = data.read().splitlines() #read lines getting rid of \n
	size = len(line)  
	 
	
######### Root Branches ####################################################

	fileRoot = TFile( 'Pressure2019.root', 'recreate' )
	t = TTree('t', 'data')
	P = (np.empty((1), dtype="d"))
	t.Branch('P',P,'P/D')	
	Time_s = (np.empty((1), dtype="d"))
	t.Branch('Time_s',Time_s,'Time_s/D')
	
############## Separating data #############################################
	
	
	b = TDatime(2019,1,1,0,0,0)    # 1st day of wanted time
	e = TDatime(2019,12,31,23,59,0)# last day
	
	begin = int(b.Convert())
	end = int(e.Convert())
	
	t_initial = begin # Jan/01/2019 in seconds
	fst_day = 1
	
	
	print(" ")
	print ("Separating data from ", b, " to ", e, "...")
	print(" ")
	
	p = []
	p_c = 0
	n = 0
	
	for i in range(size):
		info = line[i].split(",")
		if info[0] != '' and int(info[0]) == 111:
			x = list(info[3])
			if len(x) == 2:
				h = 0
				mn = int(x[0]+x[1]) 
			if len(x) == 3:
				h = int(x[0])
				mn = int(x[1]+x[2]) 
			if len(x) == 4:
				h = int(x[0]+x[1])
				mn = int(x[2]+x[3]) 
			
			day = int(info[2])
			t_day =  t_initial + (day-fst_day)*86400 + h*3600+ mn*60
			
			if t_day >= begin and t_day <= end and float(info[16]) >= 800 and float(info[16]) <= 2000:
				p_c = p_c + float(info[16])
				n += 1
				linep = t_day, float(info[16])
				
				if float(info[16]) < 900 or float(info[16]) > 2000:
					print('line:' , i, ' error in pressure:', float(info[16])) 
					break
				P[0] = float(info[16])
				Time_s[0] = t_day
				
				p.append(linep)
				t.Fill()
				
					 
	fileRoot.Write()
	p_mean = p_c/n
	
	
	Pres = open('/home/renan/Mestrado/Data/2019/pressure2019.txt', 'w')
	for i in range(len(p)):
		#dif = p[i][1]-p_mean
		Pres.write("%i %0.1f\n" % (p[i][0], p[i][1]))
	Pres.close()
	
	print ("Average pressure (hPa): ", p_mean)
	print(" ") 
	print('Done!')			
			
main()
