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
for i in range(size):
	
	file = open(adress+line[i],'r+')
	line_file = file.readlines()
	size_file = len(line_file)
	print('Reading file '+line[i])	
	
	for j in range(size_file):
		
		if len(line_file[j].split())==9 and j>3: # select info from lines with counting	
			
			if float(line_file[j].split()[7]) >= 1000 and float(line_file[j].split()[7]) < 3000:
						
				N = float(line_file[j].split()[7]) # 7:D23
				epoch = float(line_file[j].split()[0])/1000
				line_signal = epoch, N
				signal.append(line_signal)
				tri.append(N)

print(len(signal))
ref = statistics.mean(tri)
d = []
for k in range(len(tri)):
	d.append(abs(tri[k]-ref))			
d.sort()
MAD = 7*statistics.median(d)
cutoff = ref - MAD

signal2 = []
check = 'n'
for i in range(len(signal)):
	if signal[i][1] <= cutoff:
		check = 'y'
	if signal[i][1] > ref-100:
		check = 'n'
	if check == 'n':
		l = signal[i][0], signal[i][1]
		signal2.append(l)
signal.clear()
print(len(signal2))	

signal2.sort(reverse=True)

signal3 = []
check = 'n'
for i in range(len(signal2)):
	if signal2[i][1] < cutoff+20:
		check = 'y'
	if signal2[i][1] > ref-100:
		check = 'n'
	if check == 'n':
		l = signal2[i][0], signal2[i][1]
		signal3.append(l)
signal2.clear()
print(len(signal3))

tanca = pd.DataFrame(signal3,columns=["Time", "Count"])
signal3.clear()


c_mean = tanca["Count"].mean()
tanca["dC"] = tanca["Count"] - c_mean
tanca["absdC"] = tanca["dC"].abs()
mad = np.median(tanca["absdC"].values)

tanca = tanca.drop(tanca[(abs(tanca.dC) > 6*mad)].index)

#tanca['Time'] =tanca['Time'].apply(np.int64)

#tanca['curve'] = ' '
#tanca.loc[(tanca.Count < tanca.Cout.shift(1) ), 'curve'] = 'I'

#tanca['check'] = ' '
#tanca.loc[(tanca.Count < 1050), 'check'] = 'del'
#print(tanca.loc[tanca['check'] == 'del'])
#mask=(tanca.check.shift(1) == 'del') & (tanca['Count'] < ref)
#tanca.loc[mask,'check'] = 'del'
#print(tanca.loc[tanca['check'] == 'del'])
#tanca = tanca.drop(tanca[(tanca['check'] == 'del') & (tanca.check.shift(1) == 'del')].index)
#print(tanca.shape[0])
#print(tanca.loc[tanca['check'] == 'del'])

#tanca = tanca.sort_values(by = 'Time', ascending = False)
#tanca.loc[mask,'check'] = 'del'
#tanca = tanca.drop(tanca[(tanca['check'] == 'del')].index)
#tanca = tanca.drop(['check'], axis = 1)
#print(tanca.shape[0])

tanca = tanca.drop(['dC', 'absdC'], axis = 1)
tanca.to_csv('/home/renan/Mestrado/Data/'+str(Y)+'/'+str(Y)+'dataframeD23.csv', index = False, header = True)

#t = tanca.to_numpy()
#x = np.array(t[:, 0])
#y = np.array(t[:, 1])

#fig, ax = plt.subplots()
#ax.plot(x, y)
#plt.show()
print("Done!")

