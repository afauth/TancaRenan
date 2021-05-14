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
from scipy import odr
from ROOT import TCanvas,TGraph, gApplication, TTree, TFile, TDatime, gStyle,TGraphErrors, TLegend

############################################################################
# This program is to select data to define the barometric
############################################################################

Y = 2018
############# List of files to analyse  ####################################
print(" ")
print(" Selecting data... ")
print(" ")
#Detector data
data = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/df_1.csv', sep=",", header = 0)
print(data.head())
print("Size of tanca file: ", data.shape[0], "lines")

# Selecting the time interval for the season
b = TDatime(Y,9,21,0,0,0)   # 1st day of wanted time
e = TDatime(Y,12,21,23,59,59) # last day
	
begin = int(b.Convert())
end = int(e.Convert())
	
data = data.drop(data[(data.Time < begin)].index)
data = data.drop(data[(data.Time > end)].index) 
#data = data.drop(["Time_pres"], axis = 1)
	
print("Size of new list: ", data.shape[0], "lines") 

########################## Data processing ###################################	

print(" ")
print(" Processing data... ")
print(" ")

#Summer 2017: N0 =  1826.1946847165734 +- 2.518606029946182   P0 =  938.9243184579706 +- 0.18746165067986792
#Autumn 2017: N0 =  1812.9813094497397 +- 2.2271385050327437   P0 =  941.4988703590028 +- 0.17724371835004743
#Winter 2017: N0 =  1800.1462032129261 +- 2.7240651243762186   P0 =  943.629114769497 +- 0.20162427133460115
#Spring 2017: N0 =  1826.7636754106911 +- 2.565934814334404   P0 =  937.9800266378625 +- 0.19788062528540631
#Summer 2018: N0 =  1853.2827821670776 +- 2.3321733894688226   P0 =  937.7346279010893 +- 0.20179351637934212
#Autumn 2018: N0 =  1854.7634833423406 +- 2.2511384905127083   P0 =  942.0866765005491 +- 0.19501209120327312
#Winter 2018: N0 =  1836.7501277485135 +- 2.7412236999000914   P0 =  941.9815096950488 +- 0.19449397179550082
#Spring 2018: N0 =  1847.3666634138506 +- 2.946140260232625   P0 =  939.6397688231526 +- 0.22199464867331364


N0 = 1836.7501277485135
P0 = 941.9815096950488

data["deltaN/N0"] = (data['Count']-N0)/N0
data = data.sort_values('pressure')
data = data.dropna()
data["dP"] = data["pressure"] - P0

dt = data.copy()
print("Ok")

del data['Count']
del data['pressure']

print(data.head())
data = data.sort_values('dP')
t1 =  data.groupby('dP').mean()
t2 =  data.groupby('dP').std()
t3 =  data.groupby('dP').size().reset_index(name='n')
t4 =  pd.merge_asof(t1, t2, on="dP")
t = pd.merge_asof(t4, t3, on="dP")
t.fillna(0, inplace=True)

t["error_x"] = 0.5*(2**(0.5))
t["error_y"] = t["deltaN/N0_y"]/np.sqrt(t['n'])

t = t.drop(t[(t.dP < -8)].index)
t = t.drop(t[(t.dP > 6)].index)
print(t.head)

print('N =', t['n'].sum())
print(' ')
pt = t.to_numpy()

#################### Plot ###############################################

def func(p, x): #linear fit 
	a, b = p
	return a * x + b

x = np.array(pt[:, 0])
print(x)
y = np.array(pt[:, 2])
#print(y)
ex = np.array(pt[:, 6])
#print(ex)
ey = np.array(pt[:, 7])
#print(ey)

data = odr.RealData(x, y, ex)
model = odr.Model(func)
odr = odr.ODR(data, model, [1,0])
out = odr.run()	
#print(out.summary())
popt = out.beta
perr = out.sd_beta
for i in range(len(popt)):
	print(str(popt[i])+" +- "+str(perr[i]))
fit = func(popt, x)

#Compute R²
SST =  np.sum((y - np.mean(y))**2)
SSRes = np.sum((y - fit)**2)
Rsquared = 1-SSRes/SST
print(SSRes, SST)
print("R2 =", Rsquared)

beta = popt[0]*(-1*10**3)
ebeta = perr[0]*(10**3)
textstr = '\n'.join([
	' '.join([r'$\beta\: [mbar^{-1}]= -(%0.2f$' %(beta, ), r'$\pm %0.2f$' %(ebeta, ), r')$ \times 10^{-3}$']),
	r'$R^2=%.4f$' %(Rsquared, )])
	
props = dict(boxstyle = 'Square', facecolor = 'white')


#Plotting
plt.style.use('seaborn-whitegrid')
fig, ax = plt.subplots( figsize=(4, 4))
ax.errorbar(x,y, xerr = ex, yerr=ey,fmt='.k', capsize=5, alpha=0.2)
ax.plot(x, fit, label='fit', color='r')
ax.text(0.05,0.05, textstr,transform=ax.transAxes, fontsize = 8,  bbox = props)
plt.title("Spring 2018")
plt.xlabel('$\Delta$P (mbar)')
plt.ylabel('$\Delta \mathcal{N} /\mathcal{N}_0 $')
plt.savefig('/home/renan/Mestrado/Result/CAMAC/Fig-ResBCSp2018.png', bbox_inches='tight')
plt.show()
