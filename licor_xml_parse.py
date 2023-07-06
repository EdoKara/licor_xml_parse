#! /usr/bin/env python
import numpy as np
import pandas as pd #pandas for table export
from bs4 import BeautifulSoup #bs4 for XML parsing
import regex as re #re for converting to the actual concentrations
from datetime import datetime #timing stuff
import serial #communicates to serial
import time #for the sleep() function

def conv_str_to_exp(inputstr): #useful function, converts from 1.0380e-2 format to the actual float

    """
    This function takes a string or list-like of form "1.012908e10" and extracts just the exponent (the "10" from "e10" in this ex.) then 
    extracts just the pre-exponent. Then it exponentiates the pre-exponent to get a normal, python-readable number out.
    """

    exponentpattern = re.compile(r"(?<=(.e))(-?|\+?)\d+") #regex matches everything after an 'e' in a number
    preexppattern = re.compile(r"\d+\.?\d+(?=e|\se)") #matches everything up to an e in a number
    
    if type(inputstr) is str: #this if/elif logic lets you pass a list of strings or just one string to the function. 
        try:
            exp = exponentpattern.search(inputstr).group()
        except:
            exp = 1
        try:
            preexp = preexppattern.search(inputstr).group()
        except:
            preexp = 0
        
        finally: 
            exp = float(exp)
            preexp = float(preexp)

        return(preexp*(10**exp))

    elif type(inputstr) is list:
        exp = []
        preexp = []
        for i in inputstr:
            try:
                exp.append(float(exponentpattern.search(i).group()))
            except:
                exp.append(1)
            try:
                preexp.append(float(preexppattern.search(i).group()))
            except:
                preexp.append(0)
        outlist = []

        for f in range(0,(len(exp))):
            outlist.append(preexp[f]**exp[f])
        return(outlist)
    else:
        print("no match of e notation!")

def export_file_now(csv:pd.DataFrame, filepath:str): #quick macro; edit if you need to.

    """
    This is basically a macro to abstract out the export details. Lets me do it as a one-liner to keep track
    of the logical flow of the program better. 
    """

    filestamp = datetime.now().strftime(format="%d%m%y%H%M") 
    #reads the datetime at the moment of file printing and makes it into a str
    csv.to_csv(path_or_buf=f"{filepath}/licor_{filestamp}") #format string to concatenate the filepath with the datetime.


portpath = "/dev/ttyUSB0" #modify this path to the name of the port. on Windows, it would be COM1, COM2, etc.
filepath="/home/ab/Desktop/licor_outfiles/"
ser = serial.Serial(portpath, timeout=1) #opens the serial port with the desired timeout 
test = pd.DataFrame(columns= ["Datetime","co2","h2o","celltemp","cellpres"]) #initialize the df with desired columns

export_interval = 1200 #20 minute interval

while True: #loop continuously; we only exit out into this loop after exporting the last csv

    starttime = time.time() #initialize a new start time 

    try: #this try-except allows the use of ctrl-C to interrupt the program. If you do, it will export the data in
         #buffer and stop. Then you'll have to restart it 

        while (time.time() - starttime) < export_interval: #the value on the right of the inequality defines the time interval (in s) between file exports

            line = ser.readline() #reads a line of the XML from the li-cor.
            soup = BeautifulSoup(line, "lxml") #converting the XML to an object for addl processing
            subset = soup.find_all("data",recursive=True) #returns a list of all lines. 

            sl = [] #initialize an empty list
            #needs to get fixed so it's resilient to nonetype errors.
            for i in subset: #iterate over the subsets in the <data> tag
                #testing every conversion for a nonetype error;
                try:
                    # co2 = str(i.find("co2").string)
                    co2 = conv_str_to_exp(str(i.find("co2").string)) 
                except: #all try/excepts are the same; if the conversion fails return nan.
                    co2 = np.nan
                try:
                    # h2o = str(i.find("h2o").string)
                    h2o = conv_str_to_exp(str(i.find("h2o").string)) 
                except:
                    h2o = np.nan
                try:
                    # celltemp = str(i.find("celltemp").string)
                    celltemp = conv_str_to_exp(str(i.find("celltemp").string)) 
                except:
                    celltemp = np.nan
                try:
                    # cellpres = str(i.find("cellpres").string)
                    cellpres = conv_str_to_exp(str(i.find("cellpres").string)) 
                except:
                    cellpres = np.nan

                line_to_read = pd.Series(data={"Datetime": datetime.now().strftime(format="%d/%m/%Y %H:%M:%S"), 
                      "co2":co2, 
                      "h2o":h2o, 
                      "celltemp":celltemp, 
                      "cellpres":cellpres}) 
                sl.append(line_to_read) #makes a pandas series out of the values from the searched tags in data. this is where I convert
                #number formats.

            for l in sl: #for each series (i.e. line of data reported):
                test = pd.concat([test, l.to_frame().T], ignore_index=True, axis=0, join='outer') # appends to the output file
                #print(test) #diagnostic print to see that things are working OK


            time.sleep(1) #sleep 0.9s and do it over again. 

        export_file_now(csv=test, filepath=filepath)
        print("Exported Successfully!")
    
    except KeyboardInterrupt:
        export_file_now(csv=test, filepath=filepath)
        print("\n exported successfully!")
        print("quitting.")
        exit()