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
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from scipy.optimize import curve_fit
from scipy.optimize import leastsq
from scipy.optimize import least_squares
from scipy import odr
from scipy.signal import find_peaks
#########################################################################################

# Mode:
# 1: Counts with pressure
# 2: Check the egreement of the barometric correction
# 3: Check variation
# 4: Fit harmonics

mode = 4 #1,2, 3, 4
print('Selected mode ', mode)

##############################################################################################################

print(" ")
print(" Selecting data... ")
print(" ")

#############################################################################################
if mode == 1:
	
	data = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/df_1.csv', sep=",", header = 0)
	#data = data.drop(["CountB", "Date Time"], axis = 1)
	print(data.head())
	
	#Grouping by BIN
	g = []
	value = 0
	l = 0
	BIN = 600

	while len(g) != data.shape[0]:
		if l < BIN:
			g.append(value)
			l += 1
		else:
			value += 1
			l = 0
	data['grp'] = g
	data = data.groupby('grp').mean()
	data.index.name = None

	fig, axs2 = plt.subplots(2,1, constrained_layout = True,  figsize=(12, 6))
	axs2[0].plot(data['Time'], data['Count'], '-')
	axs2[0].set_ylabel('Count (Hz)')
	axs2[0].set_xlabel('Time')
	axs2[0].grid(b=True, linestyle=':', which='major', axis='both')

	axs2[1].plot(data['Time'], data['pressure'], '-', color = 'red')
	axs2[1].set_ylabel('Pressure (mbar)')
	axs2[1].set_xlabel('Time')
	axs2[1].grid(b=True, linestyle=':', which='major', axis='both')
	
	plt.savefig('/home/renan/Mestrado/Result/CAMAC/Fig-CountPressureYear_v2.png', bbox_inches='tight')
	plt.show()
	
	data["Date Time"] = pd.to_datetime(data["Time"], unit='s')
	data['year'] = pd.DatetimeIndex(data['Date Time']).year
	data['month'] = pd.DatetimeIndex(data['Date Time']).month
	data['day'] = pd.DatetimeIndex(data['Date Time']).day
	data.head()
	data['Season_ref'] = data['day'] + 100*data['month']
	data["Season"] = np.nan

	data.loc[(data['Season_ref'] < 321), 'Season'] = 'Summer'
	data.loc[(data['Season_ref'] >= 321) & (data['Season_ref'] < 621), 'Season'] = 'Autumn'
	data.loc[(data['Season_ref'] >= 621) & (data['Season_ref'] < 923), 'Season'] = 'Winter'
	data.loc[(data['Season_ref'] >= 923) & (data['Season_ref'] < 1222), 'Season'] = 'Spring'
	data.loc[(data['Season_ref'] >= 1222), 'Season'] = 'Summer'

	#data = data.drop(data[(data.Season_ref >= 20181221)].index) 
	data = data.drop(["month","day", "Time"], axis = 1)

	data['hour'] = pd.DatetimeIndex(data['Date Time']).hour
	data['minute'] = pd.DatetimeIndex(data['Date Time']).minute
	data["min"] = np.nan
	data.loc[(data['minute'] < 5), 'min'] = 0
	data.loc[(data['minute'] >= 5) & (data['minute'] < 15), 'min'] = 10
	data.loc[(data['minute'] >= 15) & (data['minute'] < 25), 'min'] = 20
	data.loc[(data['minute'] >= 25) & (data['minute'] < 35), 'min'] = 30
	data.loc[(data['minute'] >= 35) & (data['minute'] < 45), 'min'] = 40
	data.loc[(data['minute'] >= 45) & (data['minute'] < 55), 'min'] = 50
	data.loc[(data['minute'] >= 55), 'min'] = 60
	data['Time'] = data['hour']+data['min']/60
	data = data.drop(["hour", "minute","min", "Date Time"], axis = 1)

	print(data.head())
	print("Done")
	print(" ")


	print ("Working on Summer data...")
	S = data.drop(data[(data.Season != "Summer")].index) 
	S  = S.drop(["Season"], axis = 1)
	
	S17 = S.drop(S[(S.year != 2017)].index)
	S17 = S17.groupby('Time').mean().reset_index()
	S18 = S.drop(S[(S.year != 2018)].index) 
	S18 = S18.groupby('Time').mean().reset_index()
	print(S17.head(),S18.head())
	print('Done')
	
	print ("Working on Autumn data...")
	A = data.drop(data[(data.Season != "Autumn")].index) 
	A  = A.drop(["Season"], axis = 1)
	
	A17 = A.drop(A[(A.year != 2017)].index)
	A17 = A17.groupby('Time').mean().reset_index()
	A18 = A.drop(A[(A.year != 2018)].index) 
	A18 = A18.groupby('Time').mean().reset_index()
	print(A17.head(),A18.head())
	print('Done')

	print ("Working on Winter data...")
	W = data.drop(data[(data.Season != "Winter")].index) 
	W  = W.drop(["Season"], axis = 1)
	
	W17 = W	.drop(W[(W.year != 2017)].index)
	W17 = W17.groupby('Time').mean().reset_index()
	W18 = W.drop(W[(W.year != 2018)].index) 
	W18 = W18.groupby('Time').mean().reset_index()
	print(W17.head(),W18.head())
	print('Done')
	
	print ("Working on Spring data...")
	P = data.drop(data[(data.Season != "Spring")].index) 
	P  = P.drop(["Season"], axis = 1)
	
	P17 = P.drop(P[(P.year != 2017)].index)
	P17 = P17.groupby('Time').mean().reset_index()
	P18 = P.drop(P[(P.year != 2018)].index) 
	P18 = P18.groupby('Time').mean().reset_index()
	print(P17.head(),P18.head())
	print('Done')
	
	print (' ')
	
	# loking for P0:
	S17_2 = S17.drop(S17[(S17.Time < 13 )].index) 
	S17_2 = S17_2.drop(S17_2[(S17_2.Time > 16 )].index) 
	delta = (S17_2['Count'] - S17_2['Count'].mean()).abs()
	p0_S17 = S17_2.loc[(S17_2.Count- S17_2.Count.mean()).abs() == delta.min(), 'pressure'].mean()
	print(S17_2)
	print(p0_S17)
	del S17_2
	
	S18_2 = S18.drop(S18[(S18.Time  < 13 )].index) 
	S18_2 = S18_2.drop(S18_2[(S18_2.Time > 16 )].index) 
	delta = (S18_2['Count'] - S18_2['Count'].mean()).abs()
	p0_S18 = S18_2.loc[(S18_2.Count- S18_2['Count'].mean()).abs() == delta.min(), 'pressure'].mean()
	del S18_2
	
	A17_2 = A17.drop(A17[(A17.Time  < 13  )].index) 
	A17_2 = A17_2.drop(A17_2[(A17_2.Time > 16 )].index) 
	delta = (A17_2['Count'] - A17_2['Count'].mean()).abs()
	p0_A17 = A17_2.loc[(A17_2.Count- A17_2['Count'].mean()).abs() == delta.min(), 'pressure'].mean()
	del A17_2
	
	A18_2 = A18.drop(A18[(A18.Time  < 13  )].index) 
	A18_2 = A18_2.drop(A18_2[(A18_2.Time > 16 )].index) 
	delta = (A18_2['Count'] - A18_2['Count'].mean()).abs()
	p0_A18 = A18_2.loc[(A18_2.Count- A18_2['Count'].mean()).abs() == delta.min(), 'pressure'].mean()
	del A18_2
	
	W17_2 = W17.drop(W17[(W17.Time  < 13  )].index) 
	W17_2 = W17_2.drop(W17_2[(W17_2.Time > 16 )].index) 
	delta = (W17_2['Count'] - W17_2['Count'].mean()).abs()
	p0_W17 = W17_2.loc[(W17_2.Count- W17_2['Count'].mean()).abs() == delta.min(), 'pressure'].mean()
	print(p0_W17)
	del W17_2
	
	W18_2 = W18.drop(W18[(W18.Time  < 13  )].index) 
	W18_2 = W18_2.drop(W18_2[(W18_2.Time > 16 )].index) 
	delta = (W18_2['Count'] - W18_2['Count'].mean()).abs()
	p0_W18 = W18_2.loc[(W18_2.Count- W18_2['Count'].mean()).abs() == delta.min(), 'pressure'].mean()
	del W18_2
	
	P17_2 = P17.drop(P17[(P17.Time  < 13  )].index) 
	P17_2 = P17_2.drop(P17_2[(P17_2.Time > 16 )].index) 
	delta = (P17_2['Count'] - P17_2['Count'].mean()).abs()
	p0_P17 = P17_2.loc[(P17_2.Count- P17_2['Count'].mean()).abs() == delta.min(), 'pressure'].mean()
	del P17_2
	
	P18_2 = P18.drop(P18[(S18.Time  < 13 )].index) 
	P18_2 = P18_2.drop(P18_2[(P18_2.Time > 16 )].index) 
	delta = (P18_2['Count'] - P18_2['Count'].mean()).abs()
	p0_P18 = P18_2.loc[(P18_2.Count- P18_2['Count'].mean()).abs() == delta.min(), 'pressure'].mean()
	del P18_2
	
	print( 'Summer 2017: N0 = ', S17.Count.mean(), '+-', S17.Count.std()/S17.shape[0], '  P0 = ', p0_S17)
	print( 'Autumn 2017: N0 = ', A17.Count.mean(), '+-', A17.Count.std()/A17.shape[0], '  P0 = ', p0_A17)
	print( 'Winter 2017: N0 = ', W17.Count.mean(), '+-', W17.Count.std()/W17.shape[0], '  P0 = ', p0_W17)
	print( 'Spring 2017: N0 = ', P17.Count.mean(), '+-', P17.Count.std()/P17.shape[0], '  P0 = ', p0_P17)
	print( 'Summer 2018: N0 = ', S18.Count.mean(), '+-', S18.Count.std()/S17.shape[0], '  P0 = ', p0_S18)
	print( 'Autumn 2018: N0 = ', A18.Count.mean(), '+-', A18.Count.std()/A17.shape[0], '  P0 = ', p0_A18)
	print( 'Winter 2018: N0 = ', W18.Count.mean(), '+-', W18.Count.std()/W17.shape[0], '  P0 = ', p0_W18)
	print( 'Spring 2018: N0 = ', P18.Count.mean(), '+-', P18.Count.std()/P17.shape[0], '  P0 = ', p0_P18)
	
	
#############################################################################################
if mode == 2:
	
	data = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/df_1.csv', sep=",", header = 0)
	#data = data.drop(["Date Time", "Count", "pressure"], axis = 1)
	print(data.head())
	
	#Grouping by BIN
	g = []
	value = 0
	l = 0
	BIN = 600

	while len(g) != data.shape[0]:
		if l < BIN:
			g.append(value)
			l += 1
		else:
			value += 1
			l = 0
	data['grp'] = g
	data = data.groupby('grp').mean()
	data.index.name = None

	data["Date Time"] = pd.to_datetime(data["Time"], unit='s')
	data['year'] = pd.DatetimeIndex(data['Date Time']).year
	data['month'] = pd.DatetimeIndex(data['Date Time']).month
	data['day'] = pd.DatetimeIndex(data['Date Time']).day
	data.head()
	data['Season_ref'] = data['day'] + 100*data['month']
	data["Season"] = np.nan

	data.loc[(data['Season_ref'] < 321), 'Season'] = 'Summer'
	data.loc[(data['Season_ref'] >= 321) & (data['Season_ref'] < 621), 'Season'] = 'Autumn'
	data.loc[(data['Season_ref'] >= 621) & (data['Season_ref'] < 923), 'Season'] = 'Winter'
	data.loc[(data['Season_ref'] >= 923) & (data['Season_ref'] < 1222), 'Season'] = 'Spring'
	data.loc[(data['Season_ref'] >= 1222), 'Season'] = 'Summer'

	#data.loc[(data['Season'] == 'Summer'), 'DeltaN'] = data['DeltaN'] + 0.004 # for some reason the variation in summer is 0.4% lower than other seasons
	data = data.drop(data[(data.Season_ref >= 20181221)].index) 
	data = data.drop(["month","day", "Season_ref", "Time"], axis = 1)

	data['hour'] = pd.DatetimeIndex(data['Date Time']).hour
	data['minute'] = pd.DatetimeIndex(data['Date Time']).minute
	data["min"] = np.nan
	
	data.loc[(data['minute'] < 15), 'min'] = 0
	data.loc[(data['minute'] >= 15) & (data['minute'] < 45), 'min'] = 30
	data.loc[(data['minute'] >= 45), 'min'] = 60
	data['Time'] = data['hour']+data['min']/60
	data = data.drop(["hour", "minute","min", "Date Time"], axis = 1)

	print(data.head())
	print("Done")
	print(" ")


	print ("Working on Summer data...")
	S = data.drop(data[(data.Season != "Summer")].index) 
	S  = S.drop(["Season"], axis = 1)
	
	S17 = S.drop(S[(S.year != 2017)].index)
	S17 = S17.groupby('Time').mean().reset_index()
	S17['DeltaN'] = (S17['Count']-1824.6738306351733)/1824.6738306351733
	S17['betaDP'] = 0.00131*(S17['pressure']-940.0896845079528)
	
	S18 = S.drop(S[(S.year != 2018)].index) 
	S18 = S18.groupby('Time').mean().reset_index()
	S18['DeltaN'] = (S18['Count']-1853.6409361046228)/1853.6409361046228
	S18['betaDP'] = 0.0022*(S18['pressure']-939.0807204801451)
	print(S17.head(),S18.head())
	print('Done')
	
	print ("Working on Autumn data...")
	A = data.drop(data[(data.Season != "Autumn")].index) 
	A  = A.drop(["Season"], axis = 1)
	
	A17 = A.drop(A[(A.year != 2017)].index)
	A17 = A17.groupby('Time').mean().reset_index()
	A17['DeltaN'] = (A17['Count']-1813.4978557170987  )/1813.4978557170987 
	A17['betaDP'] = 0.0012*(A17['pressure']-942.8996141656197 )
	
	A18 = A.drop(A[(A.year != 2018)].index) 
	A18 = A18.groupby('Time').mean().reset_index()
	A18['DeltaN'] = (A18['Count']-1855.2920033816633)/1855.2920033816633
	A18['betaDP'] = 0.002*(A18['pressure']-943.5036734848951)
	
	print(A17.head(),A18.head())
	print('Done')

	print ("Working on Winter data...")
	W = data.drop(data[(data.Season != "Winter")].index) 
	W  = W.drop(["Season"], axis = 1)
	
	W17 = W	.drop(W[(W.year != 2017)].index)
	W17 = W17.groupby('Time').mean().reset_index()
	W17['DeltaN'] = (W17['Count']-1801.5428793179133)/1801.5428793179133
	W17['betaDP'] = 0.00132*(W17['pressure']-945.5097331908373)
	
	W18 = W.drop(W[(W.year != 2018)].index) 
	W18 = W18.groupby('Time').mean().reset_index()
	W18['DeltaN'] = (W18['Count']-1838.0144166229234)/1838.0144166229234
	W18['betaDP'] = 0.00127*(W18['pressure']-943.3450296021144)
	print(W17.head(),W18.head())
	print('Done')
	
	print ("Working on Spring data...")
	P = data.drop(data[(data.Season != "Spring")].index) 
	P  = P.drop(["Season"], axis = 1)
	
	P17 = P.drop(P[(P.year != 2017)].index)
	P17 = P17.groupby('Time').mean().reset_index()
	P17['DeltaN'] = (P17['Count']-1827.257073544645)/1827.257073544645
	P17['betaDP'] = 0.0013*(P17['pressure']- 939.2542285737853)
	
	P18 = P.drop(P[(P.year != 2018)].index) 
	P18 = P18.groupby('Time').mean().reset_index()
	P18['DeltaN'] = (P18['Count']- 1847.6912937590403)/ 1847.6912937590403 
	P18['betaDP'] = 0.0009*(P18['pressure']-940.9217076223374)
	print(P17.head(),P18.head())
	print('Done')
	
	fig, axs = plt.subplots(2,4, constrained_layout = True,  figsize=(13, 6))
	
	axs[0][0].set_xlim([0,24])
	axs[0][0].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[0][0].plot(S17['Time'], S17['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[0][0].plot(S17['Time'], S17['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[0][0].plot(S17['Time'], S17['DeltaN'] + S17['betaDP'], '-', color = 'red', label = 'dN/N0_c')
	axs[0][0].set_ylabel('Variation (%)')
	axs[0][0].set_xlabel('UTC Time [hour]')
	axs[0][0].set_title('Summer 2017')
	axs[0][0].grid(b=True, linestyle=':', which='major', axis='both')
	axs[0][0].legend()
	
	axs[1][0].set_xlim([0,24])
	axs[1][0].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[1][0].plot(S18['Time'], S18['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[1][0].plot(S18['Time'], S18['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[1][0].plot(S18['Time'], S17['DeltaN'] + S18['betaDP'], '-', color = 'red', label = 'dN/N0_c')
	axs[1][0].set_ylabel('Variation (%)')
	axs[1][0].set_xlabel('UTC Time [hour]')
	axs[1][0].set_title('Summer 2018')
	axs[1][0].grid(b=True, linestyle=':', which='major', axis='both')
	axs[1][0].legend()

	axs[0][1].set_xlim([0,24])
	axs[0][1].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[0][1].plot(A17['Time'], A17['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[0][1].plot(A17['Time'], A17['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[0][1].plot(A17['Time'], A17['DeltaN'] + A17['betaDP'], '-', color = 'red', label = 'dN/N0_c')	
	axs[0][1].set_ylabel('Variation (%)')
	axs[0][1].set_xlabel('UTC Time [hour]')
	axs[0][1].set_title('Autumn 2017')
	axs[0][1].grid(b=True, linestyle=':', which='major', axis='both')
	axs[0][1].legend()
	
	axs[1][1].set_xlim([0,24])
	axs[1][1].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[1][1].plot(A18['Time'], A18['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[1][1].plot(A18['Time'], A18['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[1][1].plot(A17['Time'], A17['DeltaN'] + A17['betaDP'], '-', color = 'red', label = 'dN/N0_c')
	axs[1][1].set_ylabel('Variation (%)')
	axs[1][1].set_xlabel('UTC Time [hour]')
	axs[1][1].set_title('Autumn 2018')
	axs[1][1].grid(b=True, linestyle=':', which='major', axis='both')
	axs[1][1].legend()

	axs[0][2].set_xlim([0,24])
	axs[0][2].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[0][2].plot(W17['Time'], W17['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[0][2].plot(W17['Time'], W17['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[0][2].plot(W17['Time'], W17['DeltaN'] + W17['betaDP'], '-', color = 'red', label = 'dN/N0_c')
	axs[0][2].set_ylabel('Variation (%)')
	axs[0][2].set_xlabel('UTC Time [hour]')
	axs[0][2].set_title('Winter 2017')
	axs[0][2].grid(b=True, linestyle=':', which='major', axis='both')
	axs[0][2].legend()
	
	axs[1][2].set_xlim([0,24])
	axs[1][2].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[1][2].plot(W18['Time'], W18['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[1][2].plot(W18['Time'], W18['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[1][2].plot(W18['Time'], W18['DeltaN'] + W18['betaDP'], '-', color = 'red', label = 'dN/N0_c')
	axs[1][2].set_ylabel('Variation (%)')
	axs[1][2].set_xlabel('UTC Time [hour]')
	axs[1][2].set_title('Winter 2018')
	axs[1][2].grid(b=True, linestyle=':', which='major', axis='both')
	axs[1][2].legend()

	axs[0][3].set_xlim([0,24])
	axs[0][3].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[0][3].plot(P17['Time'], P17['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[0][3].plot(P17['Time'], P17['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[0][3].plot(P17['Time'], P17['DeltaN'] + P17['betaDP'], '-', color = 'red', label = 'dN/N0_c')
	axs[0][3].set_ylabel('Variation (%)')
	axs[0][3].set_xlabel('UTC Time [hour]')
	axs[0][3].set_title('Spring 2017')
	axs[0][3].grid(b=True, linestyle=':', which='major', axis='both')
	axs[0][3].legend()
	
	axs[1][3].set_xlim([0,24])
	axs[1][3].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[1][3].plot(P18['Time'], P18['DeltaN'], '-', color = 'green', label = 'dN/N0')
	axs[1][3].plot(P18['Time'], P18['betaDP'], '-', color = 'blue', label = 'bdP')
	axs[1][3].plot(P18['Time'], P18['DeltaN'] + P18['betaDP'], '-', color = 'red', label = 'dN/N0_c')
	axs[1][3].set_ylabel('Variation (%)')
	axs[1][3].set_xlabel('UTC Time [hour]')
	axs[1][3].set_title('Spring 2018')
	axs[1][3].grid(b=True, linestyle=':', which='major', axis='both')
	axs[1][3].legend()
	
	plt.savefig('/home/renan/Mestrado/Result/CAMAC/Fig-DailyDeltaNxdelatP.png', bbox_inches='tight')
	plt.show()



#############################################################################################
if mode == 3:
	data = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/df_2.csv', sep=",", header = 0)
	#data = data.drop(["Count", "Date Time","pressure" ], axis = 1)
	#Grouping by BIN
	g = []
	value = 0
	l = 0
	BIN = 600

	while len(g) != data.shape[0]:
		if l < BIN:
			g.append(value)
			l += 1
		else:
			value += 1
			l = 0
	data['grp'] = g
	data = data.groupby('grp').mean()
	data.index.name = None

	data["Date Time"] = pd.to_datetime(data["Time"], unit='s')
	data['year'] = pd.DatetimeIndex(data['Date Time']).year
	data['month'] = pd.DatetimeIndex(data['Date Time']).month
	data['day'] = pd.DatetimeIndex(data['Date Time']).day
	data.head()
	data['Season_ref'] = data['day'] + 100*data['month']
	data["Season"] = np.nan

	data.loc[(data['Season_ref'] < 321), 'Season'] = 'Summer'
	data.loc[(data['Season_ref'] >= 321) & (data['Season_ref'] < 621), 'Season'] = 'Autumn'
	data.loc[(data['Season_ref'] >= 621) & (data['Season_ref'] < 923), 'Season'] = 'Winter'
	data.loc[(data['Season_ref'] >= 923) & (data['Season_ref'] < 1222), 'Season'] = 'Spring'
	data.loc[(data['Season_ref'] >= 1222), 'Season'] = 'Summer'
	
	data = data.drop(data[(data.Season_ref >= 20181221)].index) 
	data = data.drop(["month","day", "Season_ref", "Time"], axis = 1)

	data['hour'] = pd.DatetimeIndex(data['Date Time']).hour
	data['minute'] = pd.DatetimeIndex(data['Date Time']).minute
	data["min"] = np.nan
	data.loc[(data['minute'] < 5), 'min'] = 0
	data.loc[(data['minute'] >= 5) & (data['minute'] < 15), 'min'] = 10
	data.loc[(data['minute'] >= 15) & (data['minute'] < 25), 'min'] = 20
	data.loc[(data['minute'] >= 25) & (data['minute'] < 35), 'min'] = 30
	data.loc[(data['minute'] >= 35) & (data['minute'] < 45), 'min'] = 40
	data.loc[(data['minute'] >= 45) & (data['minute'] < 55), 'min'] = 50
	data.loc[(data['minute'] >= 55), 'min'] = 60
	data['Time'] = data['hour']+data['min']/60
	data = data.drop(["hour", "minute","min", "Date Time"], axis = 1)
	#data['dNc'] = data['DeltaN'] + data["beatDP"] 
	#data  = data.drop(["beatDP"], axis = 1)
	print(data.head())
	print("Done")
	print(" ")

	print ("Working on Summer data...")
	
	S = data.drop(data[(data.Season != "Summer")].index) 
	S  = S.drop(["Season"], axis = 1)
	
	S17 = S.drop(S[(S.year != 2017)].index)
	S17e = S.groupby('Time').std().reset_index()
	S17n = S.groupby('Time').size().reset_index(name='n')
	S17e = pd.merge(S17e, S17n, on='Time' , how='left')
	print(S17e.head())
	S17e['Error_Nc17'] = S17e['Nc']/np.sqrt(S17n["n"])
	S17e['Error_N017'] = S17e['Count']/np.sqrt(S17n["n"])
	S17e  = S17e.drop(["Nc", "n","year", "Count"], axis = 1)
	S17 = S17.groupby('Time').mean().reset_index()
	S17 = pd.merge(S17, S17e, on='Time' , how='left')
	S17  = S17.drop(["year"], axis = 1)
	S17.columns = ['Time', 'Count17', 'Nc17', 'Error_Nc17', 'Error_N017']
 	
	S18 = S.drop(S[(S.year != 2018)].index)
	S18e = S.groupby('Time').std().reset_index()
	S18n = S.groupby('Time').size().reset_index(name='n')
	S18e = pd.merge(S18e, S18n, on='Time' , how='left')
	S18e['Error_Nc18'] = S18e['Nc']/np.sqrt(S18n["n"])
	S18e['Error_N018'] = S18e['Count']/np.sqrt(S18n["n"])
	S18e  = S18e.drop(["Nc", "n","year", "Count"], axis = 1)
	S18 = S18.groupby('Time').mean().reset_index()
	S18 = pd.merge(S18, S18e, on='Time' , how='left')
	S18  = S18.drop(["year"], axis = 1)
	S18.columns = ['Time', 'Count18', 'Nc18', 'Error_Nc18', 'Error_N018']
	
	S = pd.merge(S17, S18, on='Time' , how='left')
	del S17
	del S18
	
	S.to_csv('/home/renan/Mestrado/Code/CAMAC/Summer.csv', index = False, header = True)
	print(S.head())
	
	print ("Working on Autumn data...")
	
	A = data.drop(data[(data.Season != "Autumn")].index) 
	A  = A.drop(["Season"], axis = 1)
	
	A17 = A.drop(A[(A.year != 2017)].index)
	A17e = A.groupby('Time').std().reset_index()
	A17n = A.groupby('Time').size().reset_index(name='n')
	A17e = pd.merge(A17e, A17n, on='Time' , how='left')
	A17e['Error_Nc17'] = A17e['Nc']/np.sqrt(A17n["n"])
	A17e['Error_N017'] = A17e['Count']/np.sqrt(A17n["n"])
	A17e  = A17e.drop(["Nc", "n","year", "Count"], axis = 1)
	A17 = A17.groupby('Time').mean().reset_index()
	A17 = pd.merge(A17, A17e, on='Time' , how='left')
	A17  = A17.drop(["year"], axis = 1)
	A17.columns = ['Time', 'Count17', 'Nc17', 'Error_Nc17', 'Error_N017']
	
	A18 = A.drop(A[(A.year != 2018)].index)
	A18e = A.groupby('Time').std().reset_index()
	A18n = A.groupby('Time').size().reset_index(name='n')
	A18e = pd.merge(A18e, A18n, on='Time' , how='left')
	A18e['Error_Nc18'] = A18e['Nc']/np.sqrt(A18n["n"])
	A18e['Error_N018'] = A18e['Count']/np.sqrt(A18n["n"])
	A18e  = A18e.drop(["Nc", "n","year", "Count"], axis = 1)
	A18 = A18.groupby('Time').mean().reset_index()
	A18 = pd.merge(A18, A18e, on='Time' , how='left')
	A18  = A18.drop(["year"], axis = 1)
	A18.columns = ['Time', 'Count18', 'Nc18', 'Error_Nc18', 'Error_N018']
	
	A = pd.merge(A17, A18, on='Time' , how='left')
	del A17
	del A18
	
	A.to_csv('/home/renan/Mestrado/Code/CAMAC/Autumn.csv', index = False, header = True)
	print(A.head())
	
	print ("Working on Winter data...")
	
	W = data.drop(data[(data.Season != "Winter")].index) 
	W  = W.drop(["Season"], axis = 1)
	
	W17 = W.drop(W[(W.year != 2017)].index)
	W17e = W.groupby('Time').std().reset_index()
	W17n = W.groupby('Time').size().reset_index(name='n')
	W17e = pd.merge(W17e, W17n, on='Time' , how='left')
	W17e['Error_Nc17'] = W17e['Nc']/np.sqrt(W17n["n"])
	W17e['Error_N017'] = W17e['Count']/np.sqrt(W17n["n"])
	W17e  = W17e.drop(["Nc", "n","year", "Count"], axis = 1)
	W17 = W17.groupby('Time').mean().reset_index()
	W17 = pd.merge(W17, W17e, on='Time' , how='left')
	W17  = W17.drop(["year"], axis = 1)
	W17.columns = ['Time', 'Count17', 'Nc17', 'Error_Nc17', 'Error_N017']
	
	W18 = W.drop(W[(W.year != 2018)].index)
	W18e = W.groupby('Time').std().reset_index()
	W18n = W.groupby('Time').size().reset_index(name='n')
	W18e = pd.merge(W18e, W18n, on='Time' , how='left')
	W18e['Error_Nc18'] = W18e['Nc']/np.sqrt(W18n["n"])
	W18e['Error_N018'] = W18e['Count']/np.sqrt(W18n["n"])
	W18e  = W18e.drop(["Nc", "n","year", "Count"], axis = 1)
	W18 = W18.groupby('Time').mean().reset_index()
	W18 = pd.merge(W18, W18e, on='Time' , how='left')
	W18  = W18.drop(["year"], axis = 1)
	W18.columns = ['Time', 'Count18', 'Nc18', 'Error_Nc18', 'Error_N018']
	
	W = pd.merge(W17, W18, on='Time' , how='left')
	del W17
	del W18
	
	W.to_csv('/home/renan/Mestrado/Code/CAMAC/Winter.csv', index = False, header = True)
	print(W.head())

	print ("Working on Spring data...")
	
	P = data.drop(data[(data.Season != "Spring")].index) 
	P  = P.drop(["Season"], axis = 1)
	
	P17 = P.drop(P[(P.year != 2017)].index)
	P17e = P.groupby('Time').std().reset_index()
	P17n = P.groupby('Time').size().reset_index(name='n')
	P17e = pd.merge(P17e, P17n, on='Time' , how='left')
	P17e['Error_Nc17'] = P17e['Nc']/np.sqrt(P17n["n"])
	P17e['Error_N017'] = P17e['Count']/np.sqrt(P17n["n"])
	P17e  = P17e.drop(["Nc", "n","year", "Count"], axis = 1)
	P17 = P17.groupby('Time').mean().reset_index()
	P17 = pd.merge(P17, P17e, on='Time' , how='left')
	P17  = P17.drop(["year"], axis = 1)
	P17.columns = ['Time', 'Count17', 'Nc17', 'Error_Nc17', 'Error_N017']
	
	P18 = P.drop(P[(P.year != 2018)].index)
	P18e = P.groupby('Time').std().reset_index()
	P18n = P.groupby('Time').size().reset_index(name='n')
	P18e = pd.merge(P18e, P18n, on='Time' , how='left')
	P18e['Error_Nc18'] = P18e['Nc']/np.sqrt(P18n["n"])
	P18e['Error_N018'] = P18e['Count']/np.sqrt(P18n["n"])
	P18e  = P18e.drop(["Nc", "n","year", "Count"], axis = 1)
	P18 = P18.groupby('Time').mean().reset_index()
	P18 = pd.merge(P18, P18e, on='Time' , how='left')
	P18  = P18.drop(["year"], axis = 1)
	P18.columns = ['Time', 'Count18', 'Nc18', 'Error_Nc18', 'Error_N018']
	
	P = pd.merge(P17, P18, on='Time' , how='left')

	del P17
	del P18
	
	P.to_csv('/home/renan/Mestrado/Code/CAMAC/Spring.csv', index = False, header = True)
	print(P.head())
	
	print("Done")
	

	fig, axs = plt.subplots(2,2, constrained_layout = True, figsize=(7, 6))
	
	axs[0][0].set_xlim([0,24])
	axs[0][0].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[0][0].plot(S['Time'], (S['Nc17']/S['Count17'].mean()-1)*100, '-', color = 'green', label = r'$(\Delta \mathcal{N} /\mathcal{N}_0)_b$')
	axs[0][0].plot(S['Time'], (S['Count17']/S['Count17'].mean()-1)*100, '-', color = 'blue', label = r'$\Delta \mathcal{N} /\mathcal{N}_0$')
	axs[0][0].set_ylabel('$\Delta \mathcal{N} /\mathcal{N}_0$ (%)')
	axs[0][0].set_xlabel('GMT Time [hour]')
	axs[0][0].set_title('Summer')
	axs[0][0].grid(b=True, linestyle=':', which='major', axis='both')
	axs[0][0].legend()
	
	axs[0][1].set_xlim([0,24])
	axs[0][1].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[0][1].plot(A['Time'], (A['Nc17']/A['Count17'].mean()-1)*100, '-', color = 'green', label = 'Barometric Correction')
	axs[0][1].plot(A['Time'], (A['Count17']/A['Count17'].mean()-1)*100, '-', color = 'blue', label = 'Raw')
	axs[0][1].set_ylabel('$\Delta \mathcal{N} /\mathcal{N}_0$ (%)')
	axs[0][1].set_xlabel('GMT Time [hour]')
	axs[0][1].set_title('Autumn')
	axs[0][1].grid(b=True, linestyle=':', which='major', axis='both')
	#axs[0][1].legend()
	
	axs[1][0].set_xlim([0,24])
	axs[1][0].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[1][0].plot(W['Time'], (W['Nc17']/W['Count17'].mean()-1)*100, '-', color = 'green', label = 'Barometric Correction')
	axs[1][0].plot(W['Time'], (W['Count17']/W['Count17'].mean()-1)*100, '-', color = 'blue', label = 'Raw')
	axs[1][0].set_ylabel('$\Delta \mathcal{N} /\mathcal{N}_0$ (%)')
	axs[1][0].set_xlabel('GMT Time [hour]')
	axs[1][0].set_title('Winter')
	axs[1][0].grid(b=True, linestyle=':', which='major', axis='both')
	#axs[1][0].legend()
	
	axs[1][1].set_xlim([0,24])
	axs[1][1].xaxis.set_major_locator(ticker.IndexLocator(base=2, offset=0))
	axs[1][1].plot(P['Time'], (P['Nc17']/P['Count17'].mean()-1)*100, '-', color = 'green', label = 'Barometric Correction')
	axs[1][1].plot(P['Time'], (P['Count17']/P['Count17'].mean()-1)*100, '-', color = 'blue', label = 'Raw')
	axs[1][1].set_ylabel('$\Delta \mathcal{N} /\mathcal{N}_0$ (%)')
	axs[1][1].set_xlabel('GMT Time [hour]')
	axs[1][1].set_title('Spring')
	axs[1][1].grid(b=True, linestyle=':', which='major', axis='both')
	#axs[1][1].legend()
	
	plt.savefig('/home/renan/Mestrado/Result/CAMAC/Fig-Daily.png', bbox_inches='tight')
	plt.show()
###################################################################################################

if mode == 4:

	#Summer
	Summer = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/Summer.csv', sep=",", header = 0)
	Summer["error_time"] = 5/60
	print(Summer.head())
	Sm = Summer.to_numpy()
	#Autumn
	Autumn = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/Autumn.csv', sep=",", header = 0)
	Autumn["error_time"] = 5/60
	print(Autumn.head())
	Au = Autumn.to_numpy()
	#Winter
	Winter = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/Winter.csv', sep=",", header = 0)
	Winter["error_time"] = 5/60
	print(Winter.head())
	Wn = Winter.to_numpy()
	#Spring
	Spring = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/Spring.csv', sep=",", header = 0)
	Spring["error_time"] = 5/60
	print(Spring.head())
	Sp = Spring.to_numpy()
	
	def error(ea, b, eb, c, ec, d, ed, e, ee, f):
		return math.sqrt((ea)**2 + ((math.sin((2*math.pi*f/24)+c))**2)*(eb**2) + ((b*math.cos((2*math.pi*f/24)+c))**2)*(ec**2) + ((math.sin((2*math.pi*f/22)+e))**2)*(ed**2) + ((e*math.cos((2*math.pi*f/12)+e))**2)*(ee**2))  
	
	def diurnalerror(N,eN,N0,eN0):
		return math.sqrt(((1/N0)**2)*(eN**2)+((N/(N0**2))**2)*(eN0**2))
	
	fig, axs = plt.subplots(2,2, constrained_layout = True, figsize=(7, 6))
	
	print('Working on summer fit...')
	A_guess = 1
	B1_guess = 0.00116
	T1_guess = 24
	phi1_guess = 0
	B2_guess = -0.00218
	T2_guess = 12
	phi2_guess = 0
	t = np.array(Sm[:, 0])
	y = np.array(Sm[:, 2])
	ey = np.array(Sm[:, 3])
	#print(ey)
	ex = np.array(Sm[:, 9])
	
	first_guess = A_guess + B1_guess*np.cos((2*math.pi*t/24)+phi1_guess) + B2_guess*np.cos((2*math.pi*t/12)+phi2_guess)
	optimize_func = lambda x: x[0] + x[1]*np.sin((2*math.pi*t/24)+x[2]) + x[3]*np.sin((2*math.pi*t/12)+x[4])-y
	A, B1, phi1, B2, phi2 = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]).x
	f_sum = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]) 
	fit = A + B1*np.sin((2*math.pi*t/24)+phi1) + B2*np.sin((2*math.pi*t/12)+phi2)
	param_sum = [A, B1, phi1, B2, phi2]
	Sum_ChiSq = np.sum(((y-fit)**2)/(fit))
	Sum_ndf = len(y)-1
	J = f_sum.jac
	cov = np.linalg.inv(J.T.dot(J))
	varS = np.sqrt(np.diagonal(cov))
	data_sum = {'Time' : y, 'Fit' : fit}
	# Looking for peaks
	peaks, _ = find_peaks(fit, height=0)
	CP_sum = fit[peaks[0]]
	tCP = t[peaks[0]]
	CPsum_error = error(varS[0], B1, varS[1], phi1, varS[2], B2, varS[3], phi2, varS[4], tCP)
	D_sum = fit[peaks[1]]
	tD = t[peaks[1]]
	Dsum_error = error(varS[0], B1, varS[1], phi1, varS[2], B2, varS[3], phi2, varS[4], tD)
	print(tD)
	
	axs[0][0].set_xlim([0, 24])
	axs[0][0].xaxis.set_major_locator(ticker.LinearLocator(13))
	axs[0][0].errorbar(t,(y),xerr= ex, yerr=ey,fmt='.k', capsize=5, alpha =0.1, label = r'$\mathcal{N}_b$')
	axs[0][0].plot(t, (fit), color='red', label = r'$f(t)$')
	axs[0][0].set_ylabel('Count Rate (Hz)')
	axs[0][0].set_xlabel('GMT Time [hour]')
	axs[0][0].set_title('Summer')
	axs[0][0].legend()
	axs[0][0].grid(b=True, linestyle=':', which='major', axis='both')
	
	print('Working on autumn fit...')
	A_guess = 1
	B1_guess = 0.0012
	T1_guess = 20.838
	phi1_guess = 6.99
	B2_guess = -0.00266
	T2_guess = 11.421
	phi2_guess = 14.704
	t = np.array(Au[:, 0])
	y = np.array(Au[:, 2])
	ey = np.array(Au[:, 3])
	ex = np.array(Au[:, 9])

	first_guess = A_guess + B1_guess*np.cos((2*math.pi*t/24)+phi1_guess) + B2_guess*np.cos((2*math.pi*t/12)+phi2_guess)
	optimize_func = lambda x: x[0] + x[1]*np.sin((2*math.pi*t/24)+x[2]) + x[3]*np.sin((2*math.pi*t/12)+x[4])-y
	A, B1, phi1, B2, phi2 = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]).x
	f_au = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]) 
	fit = A + B1*np.sin((2*math.pi*t/24)+phi1) + B2*np.sin((2*math.pi*t/12)+phi2)
	param_aut = [A, B1, phi1, B2, phi2]
	Au_ChiSq = np.sum(((y-fit)**2)/(fit))
	Au_ndf = len(y)-1
	J = f_au.jac
	cov = np.linalg.inv(J.T.dot(J))
	varA = np.sqrt(np.diagonal(cov))
	peaks, _ = find_peaks(fit, height=0)
	CP_aut = fit[peaks[0]]
	tCP = t[peaks[0]]
	CPaut_error = error(varA[0], B1, varA[1], phi1, varA[2], B2, varA[3], phi2, varA[4], tCP)
	D_aut = fit[peaks[1]]
	tD = t[peaks[1]]
	Daut_error = error(varA[0], B1, varA[1], phi1, varA[2], B2, varA[3], phi2, varA[4], tD)
	print(tD)
	
	axs[0][1].set_xlim([0,24])
	axs[0][1].xaxis.set_major_locator(ticker.LinearLocator(13))
	axs[0][1].errorbar(t,(y), xerr= ex, yerr=ey,fmt='.k', capsize=5, alpha =0.1)
	axs[0][1].plot(t, (fit), label='fit', color='red')
	axs[0][1].set_ylabel('Count Rate (Hz)')
	axs[0][1].set_xlabel('GMT Time [hour]')
	axs[0][1].set_title('Autumn')
	axs[0][1].grid(b=True, linestyle=':', which='major', axis='both')

	
	print('Working on winter fit...')
	A_guess = 1
	B1_guess = 0.004
	T1_guess = 8
	phi1_guess = 2
	B2_guess = 0.01
	T2_guess = 8
	phi2_guess = 10

	x0 = [A_guess, B1_guess, T1_guess, phi1_guess, B2_guess, T2_guess, phi2_guess]
	t = np.array(Wn[:, 0])
	y = np.array(Wn[:, 2])
	ey = np.array(Wn[:, 3])
	ex = np.array(Wn[:, 9])
	first_guess = A_guess + B1_guess*np.cos((2*math.pi*t/24)+phi1_guess) + B2_guess*np.cos((2*math.pi*t/12)+phi2_guess)
	optimize_func = lambda x: x[0] + x[1]*np.sin((2*math.pi*t/24)+x[2]) + x[3]*np.sin((2*math.pi*t/12)+x[4])-y
	A, B1, phi1, B2, phi2 = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]).x
	f_win = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]) 
	fit = A + B1*np.sin((2*math.pi*t/24)+phi1) + B2*np.sin((2*math.pi*t/12)+phi2)
	param_win = [A, B1, phi1, B2, phi2]
	Win_ChiSq = np.sum(((y-fit)**2)/(fit))
	Win_ndf = len(y)-1
	J = f_win.jac
	cov = np.linalg.inv(J.T.dot(J))
	varW = np.sqrt(np.diagonal(cov))
	CP_win = fit[peaks[0]]
	tCP = t[peaks[0]]
	CPwin_error = error(varW[0], B1, varW[1], phi1, varW[2], B2, varW[3], phi2, varW[4], tCP)
	D_win = fit[peaks[1]]
	tD = t[peaks[1]]
	Dwin_error = error(varW[0], B1, varW[1], phi1, varW[2], B2, varW[3], phi2, varW[4], tD)
	print(tD)
	
	axs[1][0].set_xlim([0,24])
	axs[1][0].xaxis.set_major_locator(ticker.LinearLocator(13))
	axs[1][0].errorbar(t,(y),xerr= ex, yerr=ey,fmt='.k', capsize=5, alpha =0.1)
	axs[1][0].plot(t, (fit), label='fit', color='red')
	axs[1][0].set_ylabel('Count Rate (Hz)')
	axs[1][0].set_xlabel('GMT Time [hour]')
	axs[1][0].set_title('Winter')
	axs[1][0].grid(b=True, linestyle=':', which='major', axis='both')
	
	
	print('Working on spring fit...')
	A_guess = -12
	B1_guess = -13.5
	T1_guess =  24
	phi1_guess = 10.6
	B2_guess = -0.00356
	T2_guess = 12
	phi2_guess = 15.4718
	t = np.array(Sp[:, 0])
	y = np.array(Sp[:, 2])
	ey = np.array(Sp[:, 3])
	ex = np.array(Sp[:, 9])
	first_guess = A_guess + B1_guess*np.cos((2*math.pi*t/24)+phi1_guess) + B2_guess*np.cos((2*math.pi*t/12)+phi2_guess)
	optimize_func = lambda x: x[0] + x[1]*np.sin((2*math.pi*t/24)+x[2]) + x[3]*np.sin((2*math.pi*t/12)+x[4])-y
	A, B1, phi1, B2, phi2 = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]).x
	f_sp = least_squares(optimize_func, [A_guess, B1_guess, phi1_guess, B2_guess, phi2_guess]) 
	fit = A + B1*np.sin((2*math.pi*t/24)+phi1) + B2*np.sin((2*math.pi*t/12)+phi2)
	param_spr = [A, B1, phi1, B2, phi2]
	Sp_ChiSq = np.sum(((y-fit)**2)/(fit))
	Sp_ndf = len(y)-1
	J = f_sp.jac
	cov = np.linalg.inv(J.T.dot(J))
	varSp = np.sqrt(np.diagonal(cov))
	CP_sp = fit[peaks[0]]
	tCP = t[peaks[0]]
	CPsp_error = error(varSp[0], B1, varSp[1], phi1, varSp[2], B2, varSp[3], phi2, varSp[4], tCP)
	D_sp = fit[peaks[1]]
	tD = t[peaks[1]]
	Dsp_error = error(varSp[0], B1, varSp[1], phi1, varSp[2], B2, varSp[3], phi2, varSp[4], tD)
	print(tD)
	
	axs[1][1].set_xlim([0,24])
	axs[1][1].xaxis.set_major_locator(ticker.LinearLocator(13))
	axs[1][1].errorbar(t,(y),xerr= ex, yerr=ey,fmt='.k', capsize=5, alpha =0.1)
	axs[1][1].plot(t, (fit), label='fit', color='red')
	axs[1][1].set_ylabel('Count Rate (Hz)')
	axs[1][1].set_xlabel('GMT Time [hour]')
	axs[1][1].set_title('Spring')
	axs[1][1].grid(b=True, linestyle=':', which='major', axis='both')
	
	print(" ")
	print("Summer:", param_sum, Sum_ChiSq, Sum_ndf)
	print("Autumn:", param_aut, Au_ChiSq, Au_ndf)
	print("Winter:", param_win, Win_ChiSq, Win_ndf)
	print("Spring:", param_spr, Sp_ChiSq, Sp_ndf)
	
	print(" ")
	print("Error:")
	print("Summer:", varS)
	print("Autumn:", varA)
	print("Winter:", varW)
	print("Spring:", varSp)
	
	print("")
	print("Variations:")
	print("Summer: ", "Compton-Getting = ", CP_sum, "+-", CPsum_error," Diurnal = ", D_sum, "+-", Dsum_error)
	print("Autumn:", "Compton-Getting = ", CP_aut, "+-", CPaut_error," Diurnal = ", D_aut, "+-", Daut_error)
	print("Winter:", "Compton-Getting = ", CP_win, "+-", CPwin_error," Diurnal = ", D_win, "+-", Dwin_error)
	print("Spring:", "Compton-Getting = ", CP_sp, "+-", CPsp_error," Diurnal = ", D_sp, "+-", Dsp_error)
	
	plt.savefig('/home/renan/Mestrado/Result/CAMAC/Fig-DailyFit.png', bbox_inches='tight')
	plt.show()
	
	print("")
	print('Diurnal variation:')
	print("Summer: ", (D_sum/Summer.Count17.mean()), "+-", diurnalerror(D_sum,Dsum_error,Summer.Count17.mean(),Summer.Count17.std()/math.sqrt(Summer.shape[0])))
	print("Autumn: ", (D_aut/Autumn.Count17.mean()), "+-", diurnalerror(D_aut,Daut_error,Autumn.Count17.mean(),Autumn.Count17.std()/math.sqrt(Autumn.shape[0])))
	print("Winter: ", (D_win/Winter.Count17.mean()), "+-", diurnalerror(D_win,Dwin_error,Winter.Count17.mean(),Winter.Count17.std()/math.sqrt(Winter.shape[0])))
	print("Spring: ", (D_sp/Spring.Count17.mean()), "+-", diurnalerror(D_sp,Dsp_error,Spring.Count17.mean(),Spring.Count17.std()/math.sqrt(Spring.shape[0])))
	# By the fit cuves:
	# Summe : Cp = 1819.94747513 (6.5)



	

