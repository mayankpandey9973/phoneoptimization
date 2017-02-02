#!/usr/bin/python2.7
import os
import os.path
import numpy as np
import sys, getopt
import math
import csv

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import dateutil.parser as dparser

from scipy import misc
from timeit import default_timer as timer



def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')



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

print newid

#Print call count by area ID
#For each areaId, tally the number of calls
if True:
    callCountByAreaId = [0]*newid
    for cl in clarr:
        callCountByAreaId[cl[2]] += 1
    plt.plot(callCountByAreaId)
    plt.ylabel('call count')
    plt.show()

#For each time interval, plot number of successful calls
#Time interval - 30mins resolution
NumIntervals = 24
callCount = [1]*NumIntervals
successCount = [0]*NumIntervals
successPercent = [0]*NumIntervals
if False:
    for cl in clarr:
        timeInterval = cl[4]/(60*60)
        callCount[timeInterval] += 1
        if(cl[6] == 1):
            successCount[timeInterval] += 1
        successPercent[timeInterval] = 100 * successCount[timeInterval]/callCount[timeInterval]
    print(successPercent)
    ind = np.arange(NumIntervals)  # the x locations for the groups
    width = 0.9       # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, successPercent, width, color='b')

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Call Success Percentage')
    ax.set_xticks(ind)
    ax.set_xticklabels(('12am','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','12pm',
                        '1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm'),
                       fontsize=6)
    autolabel(rects1)
    plt.show()

#Plot average duration of successful calls in a call interval
NumIntervals = 24
callCount = [0]*NumIntervals
successCount = [1]*NumIntervals
successPercent = [0]*NumIntervals
successCallTime = [0]*NumIntervals
successAvgCallTime = [0]*NumIntervals

if True:
    for cl in clarr:
        timeInterval = cl[4]/(60*60)
        callCount[timeInterval] += 1
        if(cl[6] == 1):
            successCount[timeInterval] += 1
            successCallTime[timeInterval] += cl[5]
        successPercent[timeInterval] = 100 * successCount[timeInterval]/callCount[timeInterval]


    for i in range(NumIntervals):
        successAvgCallTime[i] = successCallTime[i]/successCount[i]

    print(successAvgCallTime)
    print(successCount)
    
    ind = np.arange(NumIntervals)  # the x locations for the groups
    width = 0.9       # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, successAvgCallTime, width, color='#007020')

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Average Successful Call Duration (seconds)')
    ax.set_xticks(ind)
    ax.set_xticklabels(('12am','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','12pm',
                        '1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm'),
                       fontsize=6)
    autolabel(rects1)
    plt.show()

