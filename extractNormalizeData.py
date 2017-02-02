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


'''
Instructions to run:
specify addrBookFileName and callLogFileList below.
The program creates a saved numpy array for fast processing

'''



debug = False
#Addressbook filename
addrBookFileName = 'csvdata/addressbook.csv'
#Calllog filename
callLogFileList = ['csvdata/callLogs_1000_1100.csv',
                   'csvdata/callLogs_1100_1200.csv',
                   'csvdata/callLogs_1200_1300.csv',
                   'csvdata/callLogs_1300_1400.csv']

# Objects of CallLog have the following fields -- all integers
# <phoneId, phoneRegion, timeOfDay, callTime, callStatus>
# phoneId - 5 digit phoneID
# phoneNum - 10 digit phine number
# phoneRegion - 4 digit telcom circle (leading 4 digits-similar to area code)
# dayOfWeek - 1..7 -- Monday is 1, Sunday = 7
# timeOfDay is in seconds from the start of the day, i.e., 12:00AM, between 0 to 86399
# callDuration is in seconds
# callStatus is as reported in the call log files. 1=Pass, 0=Fail, 2=Error
# callVendor - 0=Exotel, 1=Tringo, 2=other
class CallLog:
    phoneId = 0
    phoneNum = 0
    phoneRegion = 0
    dayOfWeek = 0
    timeOfDay = 0
    callDuration = 0
    callStatus = 0
    callVendor = 0
#Now read all the call log files and deposit the data into the array of callLog objects
callLogList = []

newIdNum = 80000

#Process Addressbook file
if os.path.isfile(addrBookFileName) and os.access(addrBookFileName, os.R_OK):
    print "Processing " + addrBookFileName
else:
    print >>sys.stderr, "Either " + addrBookFileName + " is missing or is not readable"
    exit(1)
    
addrFile = open(addrBookFileName, 'rb')
reader = csv.reader(addrFile)

#Created from the addressbook file
id2phone = {} #Map ID to phonenum str->str
phone2id = {} #Map Phonenum to ID str->str

rownum = 0
for row in reader:
    if rownum == 0:
        header = row
    else:
        #Enter phone_number->id into table.
        phone2id[row[1]] = row[0]
        #Enter id->phone_number into table.
        id2phone[row[0]] = row[1]
        if debug and rownum < 2:
            #Print values of a few rows
            colnum = 0
            for col in row:
                print '%-20s: *%s*' % (header[colnum], col)
                colnum += 1
    rownum += 1

if debug:
    #Iterate through phone2id and id2phone tables
    count = 0 
    for phone, id in phone2id.iteritems():
        print 'phone=%s id=%s' % (phone,id)
        count += 1
        if count > 10:
            break
    count = 0 
    for id, phone in id2phone.iteritems():
        print 'id=%s phone=%s' % (id, phone)
        count += 1
        if count > 10:
            break
        

#Now read all the call log files and deposit the data into callLogList

for callLogFileName in callLogFileList:
    #Open file
    if os.path.isfile(callLogFileName) and os.access(callLogFileName, os.R_OK):
        print "Processing " + callLogFileName
    else:
        print >>sys.stderr, "Either " + callLogFileName + " is missing or is not readable"
        exit(1)
        
    callLogFile = open(callLogFileName, 'rb')
    reader = csv.reader(callLogFile)
    rownum = 0
    for row in reader:
        if rownum == 0:
            header = row
        else:
            if debug and rownum < 3:
                print("row=",row)

            #First fix some data problems in call logs. 3 types of problems detected
            #  Problem 1. Malformatted phone numbers
            #  Problem 2. Phone numbers not found in address.csv
            #  Problem 3. Date/time fields empty in some cases
            
            #Some phone numbers have a 'o' instead of '0'. Do the change
            pnum = row[4]
            isnum = all(char.isdigit() for char in pnum)
            if not isnum:
                print >>sys.stderr, "Phone format problem", pnum
                #Known problem s/o/0/
                fixstr = ''
                for c in pnum:
                    if c == 'o':
                        fixstr += '0'
                    else:
                        fixstr += c
                pnum = fixstr

            #Detect and fix problems in phoneid
            if not(pnum in phone2id):
                phoneId = newIdNum
                phone2id[pnum] = phoneId
                newIdNum += 1
                print >>sys.stderr, "phone number not in addressbook", pnum, " new ID=", phoneId
            else:
                phoneId = phone2id[pnum]

            #Detect and fix potential problems in date/time of call
            if(row[8] != 'None'):
                dp = dparser.parse(row[8])
            elif(row[7] != 'None'):
                dp = dparser.parse(row[7])
            else:
                print >>sys.stderr, "Date format problem", row
                print "ignoring row"
                continue
    

            #Create callLog entry and insert in table
            cl = CallLog()
            cl.phoneNum = int(pnum)
            cl.phoneId = phoneId
            cl.phoneRegion = int(pnum[:4])
            cl.dayOfWeek = dp.weekday()
            cl.timeOfDay = dp.hour * 3600 + dp.minute * 60 + dp.second
            cl.callDuration = int(row[9])
            if row[10] == 'pass':
                cl.callStatus = 1
            elif row[10] == 'fail':
                cl.callStatus = 0
            else: 
                cl.callStatus = 2 #error case
            if row[3] == 'exotel':
                cl.callVendor = 0
            elif row[3] == 'tringo':
                cl.callVendor = 1
            else:
                cl.callVendor = 2
                
            if debug and rownum < 3:
                #print("ID=%s Pnum=%s Regn=% Time=%s Dur=%s Stat=%s" %
                #(phoneNum, phoneId, phoneRegion, timeOfDay, callDuration, callStatus))
                print(cl.phoneNum, cl.phoneId, cl.phoneRegion, cl.dayOfWeek,
                      cl.timeOfDay, cl.callDuration, cl.callStatus,cl.callVendor)
            callLogList.append(cl)
        rownum += 1
        
print "Processed %d entries. Creating Numpy Array" % (len(callLogList))

callLogArray = np.zeros([len(callLogList),8],dtype=int)
for ndx, clog in enumerate(callLogList):
    callLogArray[ndx] = [clog.phoneId, clog.phoneNum, clog.phoneRegion,
                         clog.dayOfWeek, clog.timeOfDay, clog.callDuration,
                         clog.callStatus, clog.callVendor]

    

print "Saving numpy binary array"
#Binary data
np.save('callLogAll.npy', callLogArray)

if debug:
    #Test saving of array
    cla = np.load('callLogAll.npy')
    result = (cla == callLogArray)
    for i in range(0,len(callLogList)):
        if i < 10:
            print result[i]
            for j in range(0, 7):
                if result[i][j] == False:
                    print >>sys.stderr, "Loading file error ", i, " ", j



