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
############################################################################

# Mode:
# 1: put together tanca and pressure data
# 2: baromectric correction
# 3: daily correction
mode = 2 
print('Selected mode ', mode)

##############################################################################################################

if mode == 1:

	print(" ")
	print(" Selecting data... ")
	print(" ")

	#Counts
	data_tanca2017 = pd.read_csv('/home/renan/Mestrado/Data/2017/2017dataframe.csv',sep=",", header = 0)
	data_tanca2018 = pd.read_csv('/home/renan/Mestrado/Data/2018/2018dataframe.csv',sep=",", header = 0)
	frames_tanca = [data_tanca2017,data_tanca2018]
	tanca =  pd.concat(frames_tanca)
	tanca = tanca.sort_values('Time')
	tanca = tanca.reset_index(drop = True)
	tanca['Time'] = tanca['Time'].apply(np.int64) 
	print(tanca.head())
	
	#Pressure
	data_pres2017 = pd.read_csv('/home/renan/Mestrado/Data/2017/pressure2017.csv',sep=",", header = 0)
	data_pres2017 = data_pres2017.drop(["Unnamed: 0"], axis = 1)
	data_pres2018 = pd.read_csv('/home/renan/Mestrado/Data/2018/pressure2018.csv',sep=",", header = 0)
	data_pres2018 = data_pres2018.drop(["Unnamed: 0"], axis = 1)
	frames_pres = [data_pres2017,data_pres2018]
	pres =  pd.concat(frames_pres)
	pres = pres.sort_values('Time')
	pres['Time'] = pres['Time'].apply(np.int64)
	pres = pres.dropna()
	pres = pres.reset_index(drop = True) 
	pres['Time_pres'] = pres['Time']  

	print(pres.head())
	
	# Merging by the closest aquisition time
	data = pd.merge_asof(tanca, pres, on="Time")
	data = data.drop(["Time_pres"], axis = 1)
		
	print(data.head())
	print(data.tail())
	data.to_csv('/home/renan/Mestrado/Code/CAMAC/df_1.csv', index = False, header = True)
	
##############################################################################################################

if mode == 2:
	
#Summer 2017: N0 =  1824.6738306351733 +- 0.03607422277468887   N0 =  940.0896845079528
#Autumn 2017: N0 =  1813.4978557170987 +- 0.03542549405115493   N0 =  942.8996141656197
#Winter 2017: N0 =  1801.5428793179133 +- 0.04130315004419156   N0 =  945.5097331908373
#Spring 2017: N0 =  1827.257073544645 +- 0.04289147896876177   N0 =  939.2542285737853
#Summer 2018: N0 =  1853.6409361046228 +- 0.04385309050012138   N0 =  939.0807204801451
#Autumn 2018: N0 =  1855.2920033816633 +- 0.03703676495598588   N0 =  943.5036734848951
#Winter 2018: N0 =  1838.0144166229234 +- 0.04045998461486951   N0 =  943.3450296021144
#Spring 2018: N0 =  1847.6912937590403 +- 0.05137107918893519   N0 =  940.9217076223374


	print(" ")
	print(" Start processing... ")
	print(" ")
	
	data = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/df_1.csv',sep=",", header = 0)
	data["Date Time"] = pd.to_datetime(data["Time"], unit='s')
	data['year'] = pd.DatetimeIndex(data['Date Time']).year
	data['month'] = pd.DatetimeIndex(data['Date Time']).month
	data['day'] = pd.DatetimeIndex(data['Date Time']).day
	data.head()
	
	print(" ")
	print(" Separating data per season... ")
	
	data['Season_ref'] = data['day'] + 100*data['month'] + 10000*data['year']
	data["Season"] = np.nan
	data.loc[(data['Season_ref'] < 20170321), 'Season'] = 'Summer17'
	data.loc[(data['Season_ref'] >= 20170321) & (data['Season_ref'] < 20170621), 'Season'] = 'Autumn17'
	data.loc[(data['Season_ref'] >=  20170621) & (data['Season_ref'] < 20170921), 'Season'] = 'Winter17'
	data.loc[(data['Season_ref'] >= 20170921) & (data['Season_ref'] < 20171221), 'Season'] = 'Spring17'
	data.loc[(data['Season_ref'] >= 20171221) & (data['Season_ref'] < 20180321), 'Season'] = 'Summer18'
	data.loc[(data['Season_ref'] >= 20180321) & (data['Season_ref'] < 20180621), 'Season'] = 'Autumn18'
	data.loc[(data['Season_ref'] >=  20180621) & (data['Season_ref'] < 20180921), 'Season'] = 'Winter18'
	data.loc[(data['Season_ref'] >= 20180921) & (data['Season_ref'] < 20181221), 'Season'] = 'Spring18'
	data = data.drop(data[(data.Season_ref >= 20181221)].index) 
	
	data = data.drop(["year","month","day", "Season_ref"], axis = 1)
	print(data.head())
	print("Done")
	print(" ")
		
	data['dp'] = np.nan
	data.loc[(data['Season'] == "Summer17") , 'dp'] = data['pressure'] - 938.9243184579706
	data.loc[(data['Season'] == "Autumn17") , 'dp'] = data['pressure'] - 941.4988703590028
	data.loc[(data['Season'] == "Winter17") , 'dp'] = data['pressure'] - 943.629114769497
	data.loc[(data['Season'] == "Spring17") , 'dp'] = data['pressure'] - 937.9800266378625
	data.loc[(data['Season'] == "Summer18") , 'dp'] = data['pressure'] - 937.7346279010893
	data.loc[(data['Season'] == "Autumn18") , 'dp'] = data['pressure'] - 942.0866765005491
	data.loc[(data['Season'] == "Winter18") , 'dp'] = data['pressure'] - 941.9815096950488
	data.loc[(data['Season'] == "Spring18") , 'dp'] = data['pressure'] - 939.6397688231526
		
	data['N0'] = np.nan
	data.loc[(data['Season'] == "Summer17") , 'N0'] = 1826.1946847165734
	data.loc[(data['Season'] == "Autumn17") , 'N0'] = 1812.9813094497397
	data.loc[(data['Season'] == "Winter17") , 'N0'] = 1800.1462032129261
	data.loc[(data['Season'] == "Spring17") , 'N0'] = 1826.7636754106911
	data.loc[(data['Season'] == "Summer18") , 'N0'] = 1853.2827821670776
	data.loc[(data['Season'] == "Autumn18") , 'N0'] = 1854.7634833423406
	data.loc[(data['Season'] == "Winter18") , 'N0'] = 1836.7501277485135
	data.loc[(data['Season'] == "Spring18") , 'N0'] = 1847.3666634138506
	
	
	#data = data.drop(['dp'], axis = 1)
	data = data.dropna()
	
	print(data.head())
	
	print(" ")
	#print(" Calculating mean pressure... ")
	
	print(" ")
	print("Making the correction... ")
	
	data['beta'] = np.nan
	data.loc[(data['Season']=='Summer17'), 'beta'] = 0.0013
	data.loc[(data['Season']=='Autumn17'), 'beta'] = 0.0016
	data.loc[(data['Season']=='Winter17'), 'beta'] = 0.0013
	data.loc[(data['Season']=='Spring17'), 'beta'] = 0.0016
	data.loc[(data['Season']=='Summer18'), 'beta'] = 0.002
	data.loc[(data['Season']=='Autumn18'), 'beta'] = 0.0021
	data.loc[(data['Season']=='Winter18'), 'beta'] = 0.0014
	data.loc[(data['Season']=='Spring18'), 'beta'] = 0.001
	
	data['betaDP'] = data['beta']*data['dp']
	data['Nc'] = data['N0']*(1+(((data['Count']-data['N0'])/data['N0'])+data['betaDP']))
	data = data.drop(["beta", "dp", "Season", 'N0', 'Date Time', 'pressure','betaDP' ], axis = 1)
	print(data.head())
	#data = data.drop(["beta", "dP", "Season" ], axis = 1)
	data.to_csv('/home/renan/Mestrado/Code/CAMAC/df_2II.csv', index = False, header = True)
	print("Done")

##############################################################################################################

if mode == 3:

#Summer: [1821.2552945239297, 4.615559985054662, -2.89584528168147, -3.299611693212075, -4.316800931100053] 0.048024757212485655 144
#Autumn: [1810.4994679214092, 5.2014466117252365, 9.914523033393278, -3.5107806563339135, 14.46731435402001] 0.03979480489793503 144
#Winter: [1797.6278933865792, 6.878648056679901, 3.5133849893614237, 3.5908227683984086, 11.466462343743183] 0.057474437229965404 144
#Spring: [1824.2607552298007, -5.980611423747746, 13.058249216270992, -4.428336657398886, 14.403463132823765] 0.05016420236930673 144

	print(" ")
	print(" Selecting data... ")
	print(" ")

	Y = 2017
	data = pd.read_csv('/home/renan/Mestrado/Code/CAMAC/df_2.csv', sep=",", header = 0)

	
	param_sum= [1821.2552945239297, 4.615559985054662, -2.89584528168147, -3.299611693212075, -4.316800931100053]
	param_aut= [1810.4994679214092, 5.2014466117252365, 9.914523033393278, -3.5107806563339135, 14.46731435402001]
	param_win= [1797.6278933865792, 6.878648056679901, 3.5133849893614237, 3.5908227683984086, 11.466462343743183]
	param_spr= [1824.2607552298007, -5.980611423747746, 13.058249216270992, -4.428336657398886, 14.403463132823765]


	# change seconds to date
	data["Time2"] = data["Time"]
	data["Date Time"] = pd.to_datetime(data["Time2"], unit='s')
	# separating information
	data['year'] = pd.DatetimeIndex(data['Date Time']).year
	data.head()
	data = data.drop(data[(data.year != Y)].index)
	data['month'] = pd.DatetimeIndex(data['Date Time']).month
	data.head()
	data['day'] = pd.DatetimeIndex(data['Date Time']).day
	data.head()
	data['hour'] = pd.DatetimeIndex(data['Date Time']).hour
	data.head()
	data['minute'] = pd.DatetimeIndex(data['Date Time']).minute
	data.head()
	data['seconds'] = pd.DatetimeIndex(data['Date Time']).second
	data.head()

	data["Hour"] = (3600*data["hour"]+60*data["minute"]+data["seconds"])/3600
	data['Season_ref'] = 100*data['month']+data['day']
	data = data.drop(["year", "month", "day", "hour", "minute", "seconds"], axis = 1)
	data["Season"] = np.nan
	data.loc[(data['Season_ref'] < 321), 'Season'] = 'Summer'
	data.loc[(data['Season_ref'] >= 321) & (data['Season_ref'] < 621), 'Season'] = 'Autumn'
	data.loc[(data['Season_ref'] >= 621) & (data['Season_ref'] < 921), 'Season'] = 'Winter'
	data.loc[(data['Season_ref'] >= 921) & (data['Season_ref'] < 1221), 'Season'] = 'Spring'
	data = data.drop(data[(data.Season_ref >= 1221)].index)
	
	data = data.drop(["Season_ref"], axis = 1)

	data["f(t)"] = np.nan
	data.loc[(data['Season'] == "Summer"), 'f(t)'] = param_sum[0] + param_sum[1]*np.sin((2*math.pi*data["Hour"]/24)+param_sum[2]) + param_sum[3] *np.sin((2*math.pi*data["Hour"]/12)+param_sum[4])
	data.loc[(data['Season'] == "Autumn"), 'f(t)'] = param_aut[0] + param_aut[1]*np.sin((2*math.pi*data["Hour"]/24)+param_aut[2]) + param_aut[3] *np.sin((2*math.pi*data["Hour"]/12)+param_aut[4])
	data.loc[(data['Season'] == "Winter"), 'f(t)'] = param_win[0] + param_win[1]*np.sin((2*math.pi*data["Hour"]/24)+param_win[2]) + param_win[3] *np.sin((2*math.pi*data["Hour"]/12)+param_win[4])
	data.loc[(data['Season'] == "Spring"), 'f(t)'] = param_spr[0] + param_spr[1]*np.sin((2*math.pi*data["Hour"]/24)+param_spr[2]) + param_spr[3] *np.sin((2*math.pi*data["Hour"]/12)+param_spr[4])
	
	data['N0'] = np.nan
	data.loc[(data['Season'] == "Summer") , 'N0'] = 1824.6738306351733
	data.loc[(data['Season'] == "Autumn") , 'N0'] = 1813.4978557170987
	data.loc[(data['Season'] == "Winter") , 'N0'] = 1801.5428793179133
	data.loc[(data['Season'] == "Spring") , 'N0'] = 1827.257073544645

	data["NcII"] = data['N0']*(data["Nc"]/data["f(t)"])

	data = data.drop(["Date Time", "Season", "Hour", "f(t)", "Time2", "N0"], axis = 1)
	print(data.head())
	data.to_csv('/home/renan/Mestrado/Code/CAMAC/df_final.csv', index = False, header = True)

