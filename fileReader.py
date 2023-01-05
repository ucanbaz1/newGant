from contextlib import nullcontext
import os
import re
import fileinput
from datetime import datetime,timedelta
import io

#Start of the python file to run filereader.py Gets path and then assign time format.    
#Datetime formats to read log files. Which time formats matches, that one used. And It can change for every log files.
patternTFormat = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\,\d{3}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
# patternNFormat = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}|(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2}).(\d+)"
patternNFormat= r"(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2}).(\d+)"
patternCommissioningTimeFormat = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\,\d{3}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}|(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2}).(\d+)|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}"
patternAMPMFormat=r"\[(\d{2})/(\d{2})/(\d{4}) (\d{1,2}):(\d{2}):(\d{2}) ([AP]M)\]"
#gets container and vms time difference format
patternForTimeDifference=r"([A-Za-z]+) ([0-9]+) ([A-Za-z]+) ([0-9]+)  ([0-9]+):([0-9]+):([0-9]+) ([+-][0-9]+)"

timeDict={}
def getLineNumber(path, filename):
    # Open the log file
    with open(os.path.join(path, filename), 'r') as f:
        # Initialize the line number to 0
        countLine = 0
        timeRun =""
        timeChange =""
        timeDifference=""
        timeDifferenceCount=0
        updateType=False
        ntpCount=0
        # Iterate over the lines in the file
        for line in f:
            if timeDifferenceCount<1:
                try:
                    DifferenceMatch = re.search(patternForTimeDifference, line).group() # Finds Monday 12 September 2022  10:18:46 +0300 time format
                    timeDifference = (re.search("( [+-][0-9]+)",line).group()).strip(" ") # Finds +0300 time format
                    hour = int(timeDifference[2])
                    minute = int(timeDifference[3])
                    second = int(timeDifference[4])
                    timeDifferenceSTR=str(timedelta(hours=hour, minutes=minute, seconds=second,))+".000"
                    if DifferenceMatch:
                        timeDifferenceCount+=1
                except:
                    nullcontext
            # Increment the line number
            countLine += 1
            # Check if the current line is the special line
            if line.__contains__("Run chronyd with tmp NTP conf file to set system clock"):
                #get the line date if the line is found 2022-09-12 10:06:09,597
                timeRun = re.search(patternCommissioningTimeFormat,line).group()
                countTask=countLine
            if timeRun !="" and line.__contains__("changed:") and countLine-countTask<10:
                # Return the line number if the line is found
                timeChange = re.search(patternCommissioningTimeFormat,line).group()
                try:
                    if datetime.strptime((timeChange), '%Y-%m-%d %H:%M:%S,%f'):
                        timeFormat = '%Y-%m-%d %H:%M:%S,%f'
                except:
                    nullcontext
                try:
                    if datetime.strptime((timeChange), '%Y-%m-%d %H:%M:%S.%f'):
                        timeFormat = '%Y-%m-%d %H:%M:%S.%f'
                except:
                    nullcontext
                try:
                    if datetime.strptime((timeChange), '%Y-%m-%dT%H:%M:%S.%f'):
                        timeFormat = '%Y-%m-%dT%H:%M:%S.%f'
                except:
                    nullcontext
                try:
                    if datetime.strptime((timeChange), '%Y-%m-%dT%H:%M:%S%z'):
                        timeFormat = '%Y-%m-%dT%H:%M:%S%z'
                except:
                    nullcontext
                
                if datetime.strptime((timeChange), timeFormat) > datetime.strptime((timeRun), timeFormat):
                    timeUpdate=datetime.strptime((timeChange), timeFormat)-datetime.strptime((timeRun), timeFormat)
                    if str(timeUpdate).__contains__("."):
                        timeUpdate = str(timeUpdate).rstrip("000")
                    else:
                       timeUpdate = str(timeUpdate)+".000"
                    updateType=True
                elif datetime.strptime((timeChange), timeFormat) < datetime.strptime((timeRun), timeFormat):
                    timeUpdate=datetime.strptime((timeRun), timeFormat)-datetime.strptime((timeChange), timeFormat)
                    if str(timeUpdate).__contains__("."):
                        timeUpdate = "-"+str(timeUpdate).rstrip("000")
                    else:
                        timeUpdate = "-"+str(timeUpdate)+".000"
                    updateType=True   
                else:
                    if (timeDifferenceSTR=="00:00:00.000" and updateType==False) or (not timeDifferenceSTR=="00:00:00.000" and updateType==False):
                        break     
                #Checks if commissioning file if line has "-" signature it is less then ntp time 
                if timeUpdate.__contains__("-"):
                    if timeDifference.__contains__("+"):
                        plus = True
                        timeUpdate=str(timedelta(hours=int(timeUpdate[1])+hour,minutes=int(timeUpdate[3:5])+minute, seconds=int(timeUpdate[6:8])+second, milliseconds=int(timeUpdate[9:])))
                    elif timeDifference.__contains__("-"):
                        timeUpdate=str(timedelta(hours=int(timeUpdate[1])-hour,minutes=int(timeUpdate[3:5])-minute, seconds=int(timeUpdate[6:8])-second, milliseconds=int(timeUpdate[9:])))
                        plus = False
                    minus = True
                    timeUpdate = str(timeUpdate).rstrip("000")
                else:
                    if timeDifference.__contains__("+"):
                        timeUpdate=str(timedelta(hours=int(timeUpdate[0])+hour,minutes=int(timeUpdate[2:4])+minute, seconds=int(timeUpdate[5:7])+second, milliseconds=int(timeUpdate[8:])))
                        plus = True
                    elif timeDifference.__contains__("-"):
                        timeUpdate=str(timedelta(hours=int(timeUpdate[0])-hour,minutes=int(timeUpdate[2:4])-minute, seconds=int(timeUpdate[5:7])-second, milliseconds=int(timeUpdate[8:])))
                        plus = False
                    minus = False
                    timeUpdate = str(timeUpdate).rstrip("000")
                if plus ==True or plus==False:
                    if len(timeUpdate)<6:
                        timeUpdate = str(timeUpdate) + "00.000"
                    timeDict[filename]=[countLine,timeUpdate,minus,timeDifferenceSTR,plus]
                #Adds key and value to the dictionary all datas
                else:
                    if len(timeUpdate)<6:
                        timeUpdate = str(timeUpdate) + "00.000"
                    timeDict[filename]=[countLine,timeUpdate,minus]
                #Return Dictionary
                return timeDict  

# List all the files in the directory
def fileReader(path):   
    for filename in os.listdir(path):
        # Skip files that are not log files
        if not filename.endswith(".log"):
            continue
        #If log file name contains stackApi but it is not stackApiServer this statements block updates log file name
        if filename.__contains__("stackApi") and not filename == "stackApiServer.log":
            os.rename(path+"/"+filename,path+"/"+"stackApiServer.log")
            filename="stackApiServer.log"
        
        # Open the file in read mode
        with open(os.path.join(path, filename), 'r') as f:
            # Read the first line of the file
            line = f.readline()
            if line.startswith("ÿþ[\x00B") or line.startswith("|\x00"):
                encod=True
            else:
                encod=False

        isCommissioning = False       
        if "configure" not in filename:
             isConfigure =False

        # get variable from dictionary
        if filename in timeDict: 
            isCommissioning=True
            isConfigure=True
            lineNumber=timeDict[filename][0]
            getTime=timeDict[filename][1]
            minus=timeDict[filename][2]
            getTime = getTime.replace(".", ":")
            delta = getTime.split(":")
            try:
                timeDifferenceSTR=timeDict[filename][3]
                timeDifferenceSTR = timeDifferenceSTR.replace(".", ":")
                timeDelta = timeDifferenceSTR.split(":")
                plus=timeDict[filename][4]
            except:
                nullcontext

        lineCount=1
        """ If log files encode type is utf-16le format we have to use different format to read lines and then 
        we have to change log file encode type to be same all log format.
        """
        if encod:  
            with open(path+"/"+filename, 'rb') as f: # open utf-16le log file as binary
                text_file = io.TextIOWrapper(f, encoding='utf-16le') # with the 'utf-16le' encoding
                contents = text_file.read()  # Read the contents of the text file
            # Convert the contents to ASCII encoding
            line = contents.encode('ascii', errors='ignore') 
            # Convert the contents to ASCII decoding
            line = line.decode('ascii') 
            if(os.path.exists(filename) and os.path.isfile(filename)): #deletes old log
                os.remove(filename)
            #Save the ASCII-encoded contents to a new file
            with open(path+"/"+filename, 'w') as f: 
                f.write(line)
        if "configure" in filename and isConfigure:
            delta = getTime.split(":")
        for line in fileinput.input(os.path.join(path, filename), inplace=True):
            # Read the lines of the log file
            try:   
                # Read lines and if lines is expected time format modify line.              
                matchNFormat = re.search(patternNFormat, line).group()
                matchTFormat = re.findall(patternTFormat, line)
                if matchNFormat and not matchTFormat:
                    for matches in matchNFormat:
                        # İf log file  commissioning or configure update time because of ntp server
                        if isCommissioning or isConfigure:
                            if lineCount<int(lineNumber) or ((lineCount>=int(lineNumber) and (plus ==True or plus==False))):
                                if (plus ==True or plus==False) and lineCount==int(lineNumber) and not "configure" in filename:
                                    delta=timeDelta
                                if minus: # If minus true, line's time is less than ntp server
                                    newMatchNFormat=datetime.strptime((newMatch), '%Y-%m-%d %H:%M:%S.%f') - timedelta(
                                        hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]), milliseconds=int(delta[3]))  
                                elif not minus: #If minus false, line's time is bigger than ntp server
                                    newMatchNFormat = datetime.strptime((newMatch), '%Y-%m-%d %H:%M:%S.%f')+ timedelta(
                                        hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]), milliseconds=int(delta[3]))
                                timeUpdate=str(newMatchNFormat).rstrip("000")
                                if timeUpdate.endswith(":"):
                                    timeUpdate = timeUpdate + "00"
                                if not timeUpdate.__contains__("."):
                                    timeUpdate = timeUpdate + ".000"
                                line=line.replace(newMatch,timeUpdate) # Update line with updated time
                    #2022-11-30 04:14: 
                    #If encod true log file has [12/20/2022 2:01:53 PM] date time like this. So this if statement block removes this line.
                    if encod:
                        try:
                            matchAMPM = re.search(patternAMPMFormat,line).group() # find [12/20/2022 2:01:53 PM] date format
                            line = line.replace(matchAMPM,"") #replace with null space
                            line = line.lstrip() # remove left space of line
                        except:
                            nullcontext   
                    print(line, end='') # This print line writes the lines to log file
            except:
                nullcontext
            
            try:
                matchTFormat = re.findall(patternTFormat, line)
                if matchTFormat:
                    for matches in matchTFormat:
                        # These statements checks line time format and updates to a new time format
                        if matches[10]=="T" and len(matches)<20:
                            line = line.replace(matches, matches[:10] + " " + matches[11:] + ".000")
                        elif matches[19] == '+' or matches[19] =="-":
                            line = line.replace(matches, matches[:10] + " " + matches[11:19] + "."+matches[20:23])
                        elif matches[19]==",":
                            line = line.replace(matches, matches[:19] + "."+matches[20:23])
                        elif matches[19]==".":
                            line = line.replace(matches, matches[:10] + " " + matches[11:19] + "." +matches[20:23])

                        # İf log file  commissioning or configure update time because of ntp server
                        if isCommissioning or isConfigure:
                            if (lineCount<int(lineNumber)) or ((lineCount>=int(lineNumber) and (plus ==True or plus==False))):
                                if (plus ==True or plus==False) and (lineCount==int(lineNumber) and not "configure" in filename):
                                    delta=timeDelta
                                newMatch = re.search(patternNFormat, line).group()
                                if minus or plus: # If minus true, line's time is less than ntp server
                                    newMatchNFormat=datetime.strptime((newMatch), '%Y-%m-%d %H:%M:%S.%f') - timedelta(
                                        hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]), milliseconds=int(delta[3]))  
                                elif not minus or not plus: #If minus false, line's time is bigger than ntp server
                                    newMatchNFormat = datetime.strptime((newMatch), '%Y-%m-%d %H:%M:%S.%f')+ timedelta(
                                        hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]), milliseconds=int(delta[3]))
                                timeUpdate=str(newMatchNFormat).rstrip("000")
                                if timeUpdate.endswith(":"):
                                    timeUpdate = timeUpdate + "00"
                                if not timeUpdate.__contains__("."):
                                    timeUpdate = timeUpdate + ".000"
                                line=line.replace(newMatch,timeUpdate) # Update line with updated time
                                if lineCount==int(lineNumber):
                                    print(line, end='')
                                    break
                    #If encod true log file has [12/20/2022 2:01:53 PM] date time like this. So this if statement block removes this line.
                    if encod:
                        try:
                            matchAMPM = re.search(patternAMPMFormat,line).group() # find [12/20/2022 2:01:53 PM] date format
                            line = line.replace(matchAMPM,"") #replace with null space
                            line = line.lstrip() # remove left space of line
                        except:
                            nullcontext   
                    print(line, end='') # This print line, writes the lines to log file
            except:
                nullcontext 
            if "configure" not in filename: # If configure comes from path lineCount should not increase. Because all time should update.
                lineCount+=1 
           

# path = input("Enter File path: ")
def fileMethod(path):
    for filename in os.listdir(path):
            # Skip files that are not commissioning.log files
            if not filename.endswith("commissioning.log"):
                continue
            getLineNumber(path, filename)

    fileReader(path)


