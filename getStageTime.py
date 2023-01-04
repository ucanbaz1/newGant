from contextlib import nullcontext
import re
from datetime import datetime
import os

"""
This python file gets start time, end time and durations of stages. And gives a color for all stages.
"""


stageNameGroup=[]
stageStartGroup=[]
stageEndGroup=[]
durationGroup=[]
colorListGroup=[]
colorCount=0
Images=[]

migStartTime=""
migEndTime=""

def getKeys(path, stageTimeDict,patternNFormat, colorList):
       
    for key in stageTimeDict.keys():
        stageName = key
        stageFile = stageTimeDict[key][0]
        startTask = stageTimeDict[key][1]
        endTask = stageTimeDict[key][2]

        getStagesTime(stageName, stageFile, startTask,endTask,path,patternNFormat,colorList)
    sortGraph()

    getImageValue(path)

"""If stage in log file, gets start time and end time of stages. And assign a list.
Sometimes end time can be before line from starting time, So we cheks if starttime is not null then get endtime.
And if there are similar stages they gets same color. Also we gets stage duration for all stages. 
"""
def getStagesTime(stageName, stageFile, startTask,endTask,path,patternNFormat,colorList):
    with open(os.path.join(path, stageFile), 'r') as f:
        lines = f.readlines()
        startTime=""
        endTime=""
        global colorCount
        k=0
        debug=False
        for line in lines:
            if (startTask in line or stageFile in path) and not stageName=="Upgrade Duration Total":
                matches = re.search(patternNFormat, line).group()
                if matches:   
                    startTime=matches
                if stageName=="Primary Migration":
                   global migStartTime 
                   migStartTime= startTime
            elif endTask in line and not startTime=="" and not stageName=="Upgrade Duration Total" and not endTask=="PLAY RECAP" and not endTask=="entTime" and not stageName=="Migrate DB":
                matches = re.search(patternNFormat, line).group()
                if matches: 
                    endTime=matches
                if stageName=="Secondary Migration":
                   global migEndTime
                   migEndTime = endTime
                                   
            elif stageName=="Upgrade Duration Total" and startTask in line:
                matches = re.search(patternNFormat, line).group()
                if matches and not len(startTime)>25:   
                    startTime=matches
            elif (endTask=="PLAY RECAP") and not startTime=="" and line.startswith(endTask):
                line = (line.split("To:")[1]).split(")")[0]
                endTime=line
                
            elif (endTask=="entTime") and not startTime=="" and endTask in line:
                line = ((((line.split(": ")[1]).split(",")[0]).split('"')[1]).split('"')[0]) 
                endTime=line
                
            elif startTask=="FILE_START" and startTime=="":
                startTime= getFirstTimeOfLog(stageFile,path)
            elif (stageName=="Upgrade Duration Total" and endTask in line and endTime=="") or (endTask=="FILE_END" and endTime==""):
                endTime=getLastTimeOfLog(stageFile,endTask,path)
          
            elif stageName=="Full Migration" and startTime=="" and endTime=="":
                if not any(stageNameGroups.startswith('Full Migration') for stageNameGroups in stageNameGroup):
                    startTime = migStartTime
                    endTime = migEndTime
               

            elif stageName=="Migrate DB" and not startTime=="" and endTask in line:
                debug=True
            if debug:
                if "TASK [debug]" in line:
                    matches = re.search(patternNFormat, line).group()
                    if matches: 
                        endTime=matches
            

            if not startTime=="" and not endTime=="" and not stageName+" "+str(k) in stageNameGroup:
                startTime=startTime.split('.')[0]
                endTime=endTime.split('.')[0]
                try:
                    duration=("Duration: "+str(datetime.strptime(endTime,'%Y-%m-%d %H:%M:%S')- datetime.strptime(startTime,'%Y-%m-%d %H:%M:%S')))
                except:
                    nullcontext
                stageNameGroup.append(stageName+" "+str(k))
                stageStartGroup.append(startTime)
                stageEndGroup.append(endTime)
                durationGroup.append(duration)
                colorListGroup.append(colorList[colorCount])
                
                if stageName+" "+str(k) == "Upgrade Duration Total 0" or "commissioning" in stageName or "configure" in stageName:
                    break
                startTime=""
                endTime=""
                k+=1
        colorCount+=1  
# Gets first time of the log file        
def getFirstTimeOfLog(stageFile,path):
    with open(os.path.join(path, stageFile), 'r') as f:
        lines = f.readlines()
        for line in lines:
            try:
                line = line.split(" ")[0]+" "+line.split(" ")[1]
                datetime.strptime((line), '%Y-%m-%d %H:%M:%S.%f')  
                return line
            except:
                nullcontext
# Gets last time of the log file                   
def getLastTimeOfLog(stageFile,endTask,path):
    for line in reversed(list(open(path+"/"+stageFile))): 
            try:
                if stageFile=="stackApiServer.log":
                    if endTask in line:
                        line = line.split(" ")[0]+" "+line.split(" ")[1]
                        return line
                else:
                    line = line.split(" ")[0]+" "+line.split(" ")[1]
                    datetime.strptime((line), '%Y-%m-%d %H:%M:%S.%f')  
                    return line
            except:
                nullcontext
def getImageValue(path):
    with open(os.path.join(path, "stackApiServer.log"), 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "new_value" in line and "prev_value" in line:
                lineNew = (line.split("'new_value': ")[1]).split(",")[0]
                linePrev = (line.split("'prev_value': ")[1]).split(",")[0]
                Images.append(lineNew)
                Images.append(linePrev)
                break

# This function sorts all stages by starting time.
def sortGraph():
        j=0
        for i in range(len(stageStartGroup)):
            while j < len(stageStartGroup):
                if datetime.strptime(stageStartGroup[i],'%Y-%m-%d %H:%M:%S')>=datetime.strptime(stageStartGroup[j],'%Y-%m-%d %H:%M:%S'):
                    stageNameGroup.insert(i, stageNameGroup.pop(j))
                    stageStartGroup.insert(i, stageStartGroup.pop(j))
                    stageEndGroup.insert(i, stageEndGroup.pop(j))
                    durationGroup.insert(i, durationGroup.pop(j)) 
                    colorListGroup.insert(i, colorListGroup.pop(j))
                j = j+1
            j = i+1