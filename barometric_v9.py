#! /usr/bin/python3.5

import os
import sys
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

############################################################################
# This program is to select data to define the barometric
############################################################################

input_year = input('Year: ')
Y = int(input_year)

############# List of files to analyse  ####################################
print(" ")
print(" Selecting data... ")
print(" ")
#Detector data
data_tanca = pd.read_csv('/home/renan/Mestrado/Data/'+str(Y)+'/data'+str(Y)+'.txt', sep=" ", header=None)
data_tanca.columns = ["Time", "Count"]
print("Size of tanca file: ", data_tanca.shape[0], "lines") 

#Pressure data 
data_pres = pd.read_csv('/home/renan/Mestrado/Data/'+str(Y)+'/pressure'+str(Y)+'.txt', sep=" ", header=None)
data_pres.columns = ["Time", "pressure"]
print("Size of pressure file: ", data_pres.shape[0], "lines") 
print(" ")
print("OK")
########################## Data processing ###################################	
print(" ")
print(" Processing data... ")
print(" ")

data_tanca["logN"] = np.log(data_tanca['Count'])
data_tanca['Time'] = data_tanca['Time'].apply(np.int64)


g = []
value = 0
l = 0
while len(g) != data_pres.shape[0]:
	if l < 3:
		g.append(value)
		l += 1
	else:
		value += 1
		l = 0

data_pres["grp"] = g
data_pres = data_pres.groupby('grp').mean()
data_pres.index.name = None
p_mean = data_pres["pressure"].mean()
data_pres["dP"] = data_pres["pressure"] - p_mean
data_pres["absdP"] = data_pres["dP"].abs()
mad = 5*np.median(data_pres["absdP"].values)

print("Suggestion: Do not use pressure data where the variation is |",mad,"|")
input_answer = input('Would you like to follow the suggestion ? (yes/no) ')
answer = str(input_answer)
if answer == 'yes':
	print("removing rows...")
	data_pres = data_pres[abs(data_pres.dP) <= mad]
	data_pres = data_pres.reset_index(drop=True)
del data_pres["pressure"]
del data_pres["absdP"]

print("Merging Data: ")
data_tanca = data_tanca.sort_values('Time')
data_pres = data_pres.sort_values('Time')
data = pd.merge_asof(data_tanca, data_pres, on="Time")
dt = data.copy()
print("Ok")

del data['Time']
del data['Count']

data = data.sort_values('dP')

t1 =  data.groupby('dP').mean()
t2 =  data.groupby('dP').std()
t = pd.merge_asof(t1, t2, on="dP")
t.fillna(0, inplace=True)

pt = t.to_numpy()

#################### Plot ###############################################

def func(x, a, b): #linear fit  
	return a * x + b

x = np.array(pt[:, 0])
y = np.array(pt[:, 1])
ex = np.zeros(len(x))
ey = np.array(pt[:, 2])

popt, pcov = curve_fit(func, x, y)
N = func(np.array(x), *popt)

#Compute R²
SST =  np.sum((y - np.mean(y))**2)
SSReg = np.sum((N - np.mean(y))**2)
Rsquared = SSReg/SST


print("R2 =", Rsquared)

textstr = '\n'.join((
	r'$\alpha\: [mbar^{-1}]=%0.2e$' %(popt[0], ),
	r'$R^2=%.4f$' %(Rsquared, )))
props = dict(boxstyle = 'Square', facecolor = 'white')


#Plotting
plt.style.use('seaborn-whitegrid')
fig, ax = plt.subplots()
ax.errorbar(x,y, yerr=ey,fmt='.k', capsize=5)
ax.plot(x, N, label='fit')
ax.text(0.05,0.05, textstr,transform=ax.transAxes, fontsize = 14,  bbox = props)
plt.title(Y)
plt.xlabel('$\Delta$P (mbar)')
plt.ylabel('ln(N)')
plt.show()

