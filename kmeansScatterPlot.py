#!/usr/bin/python2.7
import os
import os.path
import numpy as np
import sys, getopt
import math
import csv
import datetime

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import dateutil.parser as dparser

from scipy import misc
from sklearn.cluster import KMeans
from timeit import default_timer as timer



# Objects of CallLog have the following fields -- all integers
# 0 phoneId - 5 digit phoneID
# 1 phoneNum - 10 digit phine number
# 2 phoneRegion - 4 digit telcom circle (4 digits-similar to area code)
# 3 dayOfWeek - 1..7 -- Monday is 1, Sunday = 7
# 4 timeOfDay is in seconds from the start of the day, i.e., 12:00AM, between 0 to 86399
# 5 callDuration is in seconds
# 6 callStatus is as reported in the call log files. 1=Pass, 0=Fail, 2=Error
# 7 callVendor - 0=Exotel, 1=Tringo, 2=other

clarr = np.load('callLogAll.npy')

#map area codes<->Unique IDs
acode2id = {} #acode/telco circle -> ID
id2acode = {} #id -> acode/telco circle

#Assign IDs instead of acode to all call
newid = 0
for cl in clarr:
    acode = cl[2]
    if not(acode in acode2id):
        acode2id[acode] = newid
        id2acode[newid] = acode
        cl[2] = newid
        newid += 1
    else:
        id = acode2id[acode]
        cl[2] = id

        
SuccCount = 0
SuccCallArray = np.full(((clarr[:,0]).size,1),0,dtype=int)
for cl in clarr:
    if cl[6] == 1:
        SuccCallArray[SuccCount][0] = cl[4]
        SuccCount += 1

NumClusters = 3
        
kmeans = KMeans(n_clusters=NumClusters, init='k-means++', n_init=10, max_iter=300, tol=0.0001, random_state=0).fit(SuccCallArray[:SuccCount])

CC = kmeans.cluster_centers_
ClusterCenters = CC.flatten()

#Scatterplot of all calls
VertResolv = 1000 #Vertical Resolution

start = 0
sz = 700000
X = clarr[start:(start+sz+NumClusters),4] #Call time
print X.size
Y = np.random.random_integers(0, VertResolv, (X.size)) #Random height
area = np.full((X.size),3, dtype=int)

X[-NumClusters:] = ClusterCenters
Y[-NumClusters:] = 500
area[-NumClusters:] = 50

colarray = ['#ff0000' for i in range(X.size)]
#print colarray
for i in range(X.size):
    if clarr[i+start][6] == 1:
        colarray[i] = '#00ee00'
    elif clarr[i+start][6] == 0:
        colarray[i] = '#ddddff'
    else:
        colarray[i] = '#ff0000'
colarray[-NumClusters:] = ['#000000']*NumClusters

ind = [0,  3600,  7200, 10800, 14400, 18000, 21600, 25200, 28800,32400, 36000, 39600, 43200, 46800, 50400, 54000, 57600, 61200,64800, 68400, 72000, 75600, 79200, 82800]

#X = [2, 82000]
#Y = [500, 500]
fig, ax = plt.subplots()
ax.set_ylabel('')
ax.set_xticks(ind)
ax.set_xticklabels(('12am','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','12pm',
                    '1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm'),
                   fontsize=6)

ax.set_yticklabels((""))

plt.scatter(X, Y, s=area, c=colarray, alpha=0.5,edgecolors='none')

plt.show()

print("Recommended Call Times")
for time in ClusterCenters:
    print str(datetime.timedelta(seconds=time))
    

