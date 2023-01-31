from contextlib import nullcontext
import os
import re
import fileinput
from datetime import datetime,timedelta
import io
import shutil


"""
Start of the python file to run filereader.py Gets path and then assign time format.    
Datetime formats to read log files. Which time formats matches, that one used. And It can change for every log files.
"""

patternTFormat = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\,\d{3}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
patternNFormat= r"(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2}).(\d+)"
patternCommissioningTimeFormat = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\,\d{3}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}|(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2}).(\d+)|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}"
patternAMPMFormat=r"\[(\d{2})/(\d{2})/(\d{4}) (\d{1,2}):(\d{2}):(\d{2}) ([AP]M)\]"

#gets container and vms time difference format
patternForTimeDifference=r"([A-Za-z]+) ([0-9]+) ([A-Za-z]+) ([0-9]+)  ([0-9]+):([0-9]+):([0-9]+) ([+-][0-9]+)"

timeDict={}
containertimeDict={}

"""
This code defines a function 'getcontainerTimeDifference' that takes two arguments: 'path' and 'filename'. 
The function opens the file specified by the file path 'os.path.join(path, filename)' in read mode.

The function then searches each line in the file for a time format using a regular expression
pattern 'patternForTimeDifference'. If the time format is found, the code uses another regular expression 
to extract the time difference, which is the time zone offset in the format '+HHMM'.

The code then converts the time zone offset into a string in the format
'timedelta(hours=hour, minutes=minute, seconds=second)', where 'hour', 'minute', and 'second' are extracted 
from the time difference string. If the time difference string is not equal to '+0000', '-0000', or '0000', 
the code adds the time difference information to a dictionary 'containertimeDict' with the filename as the key. 
The value of the dictionary is a list with two elements: the time difference in the 'timedelta' format, 
and a Boolean value indicating whether the time difference is a plus or minus offset.
Finally, the function returns the 'containertimeDict'.
"""
def getcontainerTimeDifference(path, filename):
    with open(os.path.join(path, filename), 'r') as f:
        
        timeDifference=""
        for line in f: # Search each line to get time format 
                try:
                    DifferenceMatch = re.search(patternForTimeDifference, line).group() # Finds Monday 12 September 2022  10:18:46 +0300 time format
                    timeDifference = (re.search("( [+-][0-9]+)",line).group()).strip(" ") # Finds +0300 time format
                    hour = int(timeDifference[2])
                    minute = int(timeDifference[3])
                    second = int(timeDifference[4])
                    timeDifferenceSTR=str(timedelta(hours=hour, minutes=minute, seconds=second,))+".000"
                    if DifferenceMatch:
                        break # If time format is found and parsed break loop
                except:
                    nullcontext
                
            
        if not timeDifference=="": 
            if not timeDifference=="+0000" or not timeDifference=="-0000" or not timeDifference=="0000": # If timeDifference is zero dont any action. 
                if timeDifference.__contains__("+"): 
                    minus=True
                else:
                    minus=False
                containertimeDict[filename]=[timeDifferenceSTR,minus] # Assign each parameter to the dictionary for all log file.
                return containertimeDict

"""
This code is a part of a larger script that updates timestamps in log files present in a directory. 
The code first gets the path to the directory and the lab name from command line arguments using the argparse library.

The code then defines a function updateContainerTime(newPath) which updates the timestamps in log files. 
The function takes in a parameter newPath, which is the path to the directory containing the log files.

The function iterates through all the files in the directory newPath. 
If the file is a log file (ending with ".log" and doesn't contain the word "configure"), 
it retrieves the time difference between the time on the log file and the NTP server's time. 
This time difference was previously stored in a dictionary containertimeDict.

For each line in the log file, the function uses regular expressions to search for a time stamp in the format
 %Y-%m-%d %H:%M:%S.%f. If a time stamp is found, the function uses the stored time difference to either add or 
 subtract the time from the log file's time stamp to correct it to match the NTP server's time. 
 The corrected time stamp is then used to replace the original time stamp in the line.

The corrected line is then printed, and the process repeats for each line in the log file.
""" 
def updateContainerTime(newPath):
     for filename in os.listdir(newPath):
        # Skip files that are not log files
        if not filename.endswith(".log"):
            continue

        if "configure" not in filename:
            timeDifference =False

        # Gets the previously assigned parameters from the dictionary.
        if filename in containertimeDict: 
            timeDifference=True
            getTime=containertimeDict[filename][0]
            minus=containertimeDict[filename][1]
            getTime = getTime.replace(".", ":")
            delta = getTime.split(":")
        
        if timeDifference:
            for line in fileinput.input(os.path.join(newPath, filename), inplace=True):
                try: 
                    if ("PLAY RECAP" in line or "endTime" in line) and not "failed=1" in line:
                        print(line, end='')
                        continue 
                    newMatch = re.search(patternNFormat, line).group()
                    if minus: # If minus true, line's time is less than ntp server
                        newMatchNFormat=datetime.strptime(newMatch, '%Y-%m-%d %H:%M:%S.%f') - timedelta(
                            hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]), milliseconds=int(delta[3]))  
                    elif not minus: #If minus false, line's time is bigger than ntp server
                        newMatchNFormat = datetime.strptime(newMatch, '%Y-%m-%d %H:%M:%S.%f')+ timedelta(
                            hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]), milliseconds=int(delta[3]))
                    timeUpdate=str(newMatchNFormat).rstrip("000")
                    if timeUpdate.endswith(":"):
                        timeUpdate = timeUpdate + "00"
                    if not timeUpdate.__contains__("."):
                        timeUpdate = timeUpdate + ".000"
                    line=line.replace(newMatch,timeUpdate) # Update line with updated time
                    print(line, end='')
                except:
                    nullcontext

"""
The function getLineNumber is used to find the line number that contains the string "Run chronyd with tmp NTP conf 
file to set system clock" in a specified file located in a specified path. The line number and time difference 
between the line containing the special string and the line with "changed:" are calculated. 
The time difference is stored in the dictionary timeDict with the filename as the key and line number, 
time difference and a flag indicating if the time difference is negative as the value. If the time difference 
is greater than 1 second, the function returns timeDict.
"""
def getLineNumber(path, filename):
    # Open the log file
    with open(os.path.join(path, filename), 'r') as f:
        # Initialize the line number to 0
        countLine = 0
        timeRun =""
        timeChange =""
        # Iterate over the lines in the file
        for line in f:
            timeUpdate=""
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
                
                # Assign time format
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
                elif datetime.strptime((timeChange), timeFormat) < datetime.strptime((timeRun), timeFormat):
                    timeUpdate=datetime.strptime((timeRun), timeFormat)-datetime.strptime((timeChange), timeFormat)
                    if str(timeUpdate).__contains__("."):
                        timeUpdate = "-"+str(timeUpdate).rstrip("000")
                    else:
                        timeUpdate = "-"+str(timeUpdate)+".000"
            
                   
                #Checks if commissioning file if line has "-" signature it is less then ntp time 
                if not timeUpdate=="":
                    if timeUpdate>"0:00:01.000":
                        if timeUpdate.__contains__("-"):
                            minus = True
                            timeUpdate = str(timeUpdate).rstrip("000")
                        else:
                            minus = False
                            timeUpdate = str(timeUpdate).rstrip("000")
                        timeUpdate=timeUpdate.lstrip("-")
                        #Adds key and value to the dictionary all datas
                        timeDict[filename]=[countLine,timeUpdate,minus]
                        #Return Dictionary
                        return timeDict  

"""
The function fileReader reads log files from a given directory path, makes some modifications to them, 
and saves the modified files to a new directory path. The following are the modifications performed by the function:

Skips files that are not log files (files not ending in '.log').
Renames log files that contain "stackApi" in their name but not "stackApiServer.log" to "stackApiServer.log".
Reads the first line of the file and checks if it starts with "ÿþ[\x00B" or "|\x00". 
If it does, it sets a flag encod to True, indicating the file is in utf-16le format.
Determines if the file name contains "configure" and sets a flag isConfigure accordingly.
If the file name exists in the timeDict dictionary, it sets flags isCommissioning and isConfigure to True, 
gets the line number, time, and a flag indicating whether the time is smaller or larger than the NTP server from 
the dictionary, and formats the time.
If the file is in utf-16le format, the function reads the file as binary, decodes it using 'utf-16le' encoding, 
converts it to ASCII encoding, and saves it as an ASCII-encoded file.
Reads each line of the log file, and if a line matches the expected time format, modifies the line's time 
according to whether the file is a commissioning or configure log and whether the line's time is smaller or larger than 
the NTP server. The modified log is saved to a new file in the new directory path.
"""              
def fileReader(path, newPath):   
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



        with open(path+'/'+filename, 'r') as file: # Read log files
            with open(newPath+'/'+filename, 'a') as newFile: # Write updated log files under new path
                lineCount=1
                for line in file:
                    # Read the lines of the log file
                    try:   
                        # Read lines and if lines is expected time format modify line.              
                        matchNFormat = re.search(patternNFormat, line).group()
                        matchTFormat = re.findall(patternTFormat, line)
                        if matchNFormat and not matchTFormat:
                            for matches in matchNFormat:
                                # İf log file  commissioning or configure update time because of ntp server
                                if isCommissioning or isConfigure:
                                    if lineCount<int(lineNumber):
                                        newMatch = re.search(patternNFormat, line).group()
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
                            try:
                                matchAMPM = re.search(patternAMPMFormat,line).group() # find [12/20/2022 2:01:53 PM] date format
                                line = line.replace(matchAMPM,"") #replace with null space
                                line = line.lstrip() # remove left space of line
                            except:
                                nullcontext   
                            newFile.write(line) # This print line writes the lines to log file
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
                                    if lineCount<int(lineNumber):
                                        newMatch = re.search(patternNFormat, line).group()
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
                                                     
                            try:
                                matchAMPM = re.search(patternAMPMFormat,line).group() # find [12/20/2022 2:01:53 PM] date format
                                line = line.replace(matchAMPM,"") #replace with null space
                                line = line.lstrip() # remove left space of line
                            except:
                                nullcontext   
                            
                                # Write the formatted lines to the file
                            newFile.write(line)
                            
                    except:
                        nullcontext 
                    if "configure" not in filename: # If configure comes from path lineCount should not increase. Because all time should update.
                        lineCount+=1 

"""
This function performs the following operations:

-   Loops through each file in the directory specified by the path argument.
-   For each file, if the file ends with "commissioning.log", it calls the getLineNumber function with path and filename
as arguments.
-   For each file, if the file ends with "commissioning.log", "migration-primary.log", "migration-secondary.log", 
or "stackApiServer.log", it calls the getcontainerTimeDifference function with path and filename as arguments.
-   Creates a new directory named "UpdatedLogs" at newPath (which is path + "/UpdatedLogs"). If the directory already exists, 
it deletes it first.
-   Calls the fileReader function with path and newPath as arguments.
-   Calls the updateContainerTime function with newPath as argument.
"""
def fileMethod(path):
    for filename in os.listdir(path):
            # Skip files that are not commissioning.log files
            if filename.endswith("commissioning.log"):
                getLineNumber(path, filename)

            if filename.endswith("commissioning.log") or filename.endswith("migration-primary.log") or filename.endswith("migration-secondary.log") or filename.endswith("stackApiServer.log"):
            # if filename.endswith("commissioning.log") or filename.endswith("migration-primary.log") or filename.endswith("migration-secondary.log") or "vnfr" in filename or filename.endswith("stackApiServer.log"):
            # if filename.endswith("commissioning.log") or filename.endswith("migration-primary.log") or filename.endswith("migration-secondary.log"):                
                getcontainerTimeDifference(path, filename)
    newPath=path+"/UpdatedLogs"
    if os.path.exists(newPath):
        shutil.rmtree(newPath)
    os.makedirs(newPath)
        
    fileReader(path,newPath)
    updateContainerTime(newPath)


