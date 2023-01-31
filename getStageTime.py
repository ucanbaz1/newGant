from contextlib import nullcontext
import re
from datetime import datetime
import os

stageNameGroup=[]
stageStartGroup=[]
stageEndGroup=[]
durationGroup=[]
colorListGroup=[]
colorCount=0
Images=[]

migStartTime=""
migEndTime=""

"""
This function retrieves the stages parameters from the dictionary "stageTimeDict". 
It loops through the keys of the dictionary and retrieves the stage name, stage file, start task, and end task for each key. 
Then it calls the "getStagesTime" function to process the data and passes the parameters: stage name, stage file, start task, end task, path, 
patternNFormat, and colorList. Finally, it calls the "getImageValue" and "sortGraph" functions.
"""
def getKeys(path, stageTimeDict,patternNFormat, colorList):
    path=path+'/'+'UpdatedLogs'   
    for key in stageTimeDict.keys():
        stageName = key
        stageFile = stageTimeDict[key][0]
        startTask = stageTimeDict[key][1]
        endTask = stageTimeDict[key][2]

        getStagesTime(stageName, stageFile, startTask,endTask,path,patternNFormat,colorList)
    getImageValue(path)
    sortGraph()


"""
This function reads the contents of a file, 'stageFile', located at the 'path' directory and parses the time of various stages
based on the provided arguments such as 'stageName', 'startTask', 'endTask', etc. The time is extracted by searching for a pattern that matches
the 'patternNFormat' regular expression in each line of the file. The extracted time is stored in the variables 'startTime' and 'endTime'.
Some special cases are handled based on the value of 'stageName' and 'endTask', such as if the stage is a failed case or
if the stage is part of the migration duration total, etc. The function uses the global variables 'colorCount', 'migStartTime', 'migEndTime'
to store data across function calls. 
"""
def getStagesTime(stageName, stageFile, startTask,endTask,path,patternNFormat,colorList):
    with open(os.path.join(path, stageFile), 'r') as f:
        lines = f.readlines()
        startTime=""
        endTime=""
        global colorCount
        stageCount=0
        stageCountRollback=1
        endTaskCounts=0
        debug=False
        checkRepair=False
        checkRollback=False
        failed=False
        #loop through all the lines in the file
        for line in lines:
            # Skip reading migration logs when Installation Duration is present
            if ("Migration Duration Total 0" in stageNameGroup or "Primary Migration 0" in stageNameGroup) and "Installation Duration" in stageName: 
                continue
            # Check if logs contain repair stages
            if "Upgrade Side"==stageName and not startTime==""  and "evaluate_repair_trigger()" in line:
                checkRepair=True 
            # Check if logs contain rollback case
            if "Upgrade Side"==stageName and not startTime==""  and "Playbook '/var/mcp/raf/rollback/pre-checks.yml' complete successfully" in line and not checkRollback==True:
                checkRollback=True
            
            # Check if logs contain failed case
            elif not startTime=="" and "failed=1" in line and "Upgrade Side"==stageName or "Installation Duration Total"==stageName:
                matches = re.search(patternNFormat, line).group()
                if matches: 
                    endTime=matches
                    failed=True

           # Gets start time of stages 
            if (startTask in line or stageFile in path) and not stageName=="Upgrade Duration Total":
                matches = re.search(patternNFormat, line).group()
                if matches:   
                    startTime=matches
                    endTaskCounts=0
                if stageName=="Primary Migration": # For Migration Duration Total start time
                   global migStartTime 
                   migStartTime= startTime
           
            # Gets end time of stages
            elif endTask in line and not startTime=="" and not stageName=="Upgrade Duration Total" and not endTask.startswith("PLAY RECAP") and not endTask=="entTime" and not stageName=="Migrate DB" and endTaskCounts<1:
                matches = re.search(patternNFormat, line).group()
                if matches: 
                    endTime=matches
                if stageName=="Secondary Migration":# For Migration Duration Total end time
                   global migEndTime
                   migEndTime = endTime
                endTaskCounts+=1
            # Gets total duration of upgrade     
            elif stageName=="Upgrade Duration Total" and startTask in line and startTime =="":
                matches = re.search(patternNFormat, line).group()
                # if matches and not len(startTime)>25:   
                if matches:
                    startTime=matches
            # Get end time if end task starts with "PLAY RECAP" string
            elif (endTask.startswith("PLAY RECAP")) and not startTime=="" and line.startswith(endTask):
                line = (line.split("To:")[1]).split(")")[0]
                endTime=line
            # Gets end time if end task starts with "endTime" string  
            elif (endTask=="entTime") and not startTime=="" and endTask in line:
                line = ((((line.split(": ")[1]).split(",")[0]).split('"')[1]).split('"')[0]) 
                endTime=line
             # If start task is FILE_START, gets first time of the logs   
            elif startTask=="FILE_START" and startTime=="":
                startTime= getFirstTimeOfLog(stageFile,path)
            # If start task is FILE_END, gets last time of the logs
            elif (stageName=="Upgrade Duration Total" and endTask in line and endTime=="") or (endTask=="FILE_END" and endTime==""):
                endTime=getLastTimeOfLog(stageFile,endTask,path)
            # Get migration duration total          
            elif stageName=="Migration Duration Total" and startTime=="" and endTime=="":
                if not any(stageNameGroups.startswith('Migration Duration Total') for stageNameGroups in stageNameGroup):
                    startTime = migStartTime
                    endTime = migEndTime
            # Checks if commissioning contains stages
            elif stageName=="Migrate DB" and not startTime=="" and endTask in line:
                debug=True
            if debug:
                if "TASK [debug]" in line:
                    matches = re.search(patternNFormat, line).group()
                    if matches: 
                        endTime=matches
           
            elif checkRollback:
                stageName=stageName+" Rollback"
                stageCount-=stageCountRollback
                checkRollback=False 
                stageCountRollback+=1
            # Assigns the Stage parameters to the lists
            if (not startTime=="" and not endTime=="" and not stageName+" "+str(stageCount) in stageNameGroup) or (not startTime=="" and not endTime=="" and "vnfr" in stageFile):
                # remove the microseconds part from the start and end time
                startTime=startTime.split('.')[0]
                endTime=endTime.split('.')[0]
                # calculate the duration
                try:
                    duration=("Duration: "+str(datetime.strptime(endTime,'%Y-%m-%d %H:%M:%S')- datetime.strptime(startTime,'%Y-%m-%d %H:%M:%S')))
                except:
                    nullcontext
                # only add to the stage groups if the duration is greater than 0:00:03
                if str(datetime.strptime(endTime,'%Y-%m-%d %H:%M:%S')- datetime.strptime(startTime,'%Y-%m-%d %H:%M:%S'))>"0:00:03":
                    # check if the stage is a repair stage
                    if checkRepair:
                        # find the next available repair stage count
                        while not stageName+" Repair "+str(stageCount) in stageNameGroup and stageCount>=0:
                            stageCount-=1
                        stageCount+=1
                        stageNameGroup.append(stageName+" Repair "+str(stageCount))
                        
                        checkRepair=False 
                    # check if the stage is a failed stage
                    elif failed:
                        # find the next available failed stage count
                        while not stageName+" Failed "+str(stageCount) in stageNameGroup and stageCount>=0:
                           stageCount-=1
                        stageCount+=1
                        stageNameGroup.append(stageName+" Failed "+str(stageCount))
                        
                        failed=False
                    # regular stage
                    else:
                        while not stageName+" "+str(stageCount) in stageNameGroup and stageCount>=0:
                            stageCount-=1
                        stageCount+=1
                        stageNameGroup.append(stageName+" "+str(stageCount))
                    # add the start, end and duration to the corresponding groups
                    stageStartGroup.append(startTime)
                    stageEndGroup.append(endTime)
                    durationGroup.append(duration)
                    colorListGroup.append(colorList[colorCount])
                    # break out of the loop if the stage name is "Upgrade Duration Total 0" or contains "commissioning" or "configure"
                    if stageName+" "+str(stageCount) == "Upgrade Duration Total 0" or "commissioning" in stageName or "configure" in stageName:
                        break
                    # reset start and end time, increase stage count
                    startTime=""
                    endTime=""
                    stageCount+=1
                    # if the stage name is "Upgrade Side", set it to just "Upgrade Side"
                    if "Upgrade Side" in stageName:
                        stageName="Upgrade Side"
        # increase the color count
        colorCount+=1  

"""
This function reads the content of the stage file located at the path and returns the first line in the file that contains a valid date time string,
formatted as "YYYY-MM-DD HH:MM:SS.fff". If no valid date time string is found in the file, the function returns nothing (null).
"""    
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
"""
The getLastTimeOfLog function retrieves the last time from a log file. It first reads the log file by lines in reverse order
(so it starts from the last line to the first line). For each line, it checks if the line contains a certain string, endTask,
for the "stackApiServer.log" file. If it does, it extracts the first two items of the line and returns it as a string. For other log files, 
it simply extracts the first two items of the line and returns it as a string.
"""           
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
"""
The function getImageValue reads the contents of a file "stackApiServer.log" located in the path provided as an argument.
It then searches for specific strings in the file and appends image related information such as operator type (upgrade, migration, or installation),
the new or migrated image name, and the previous image version to a list "Images". The function breaks out of the loop once it finds the information 
it is looking for.
"""
def getImageValue(path):
    # Open the log file located in the specified path
    with open(os.path.join(path, "stackApiServer.log"), 'r') as f:
        lines = f.readlines()
        # Loop through each line in the log file
        for line in lines:
            # Check if the line contains "new_value", "prev_value", and "MCP"
            if "new_value" in line and "prev_value" in line and "MCP" in line:
                # Extract the new and previous image version from the line
                lineNew = (line.split("'new_value': ")[1]).split(",")[0]
                linePrev = (line.split("'prev_value': ")[1]).split(",")[0]
                # Set the operation type as "upgrade"
                operator="upgrade"
                # Append the operation type, new image version, and previous image version to the Images list
                Images.append(operator)
                Images.append(lineNew)
                Images.append(linePrev)
                # Stop looping through the lines
                break
            # Check if the line contains "vsphere_file.upload" or "Upload /resources/images/" and "Migration Duration Total 0"
            elif (("vsphere_file.upload" in line and "MCP" in line) or "Upload /resources/images/" in line) and "Migration Duration Total 0" in stageNameGroup:
                # Extract the image name from the line
                if "Upload /resources/images/" in line:
                    migrateImage=(line.split('images/')[1]).split(" to")[0]
                else:
                    migrateImage=(line.split('upload')[1]).split(":")[0]
                # Set the operation type as "migration"
                operator="migration"
                # Append the operation type, image name, and previous image version to the Images list
                Images.append(operator)
                Images.append(migrateImage)
                Images.append("MCP_21.0")
                break
            # Check if the line does not contain "Migration Duration Total 0", "Primary Migration 0", and "Secondary Migration 0"
            elif not "Migration Duration Total 0" in stageNameGroup and not "Primary Migration 0" in stageNameGroup and not "Secondary Migration 0" in stageNameGroup:
                # Check if the line does not contain "Upgrade Duration Total 0", "Upgrade Side 0", and "Upgrade Side 1"
                if not "Upgrade Duration Total 0" in stageNameGroup and not "Upgrade Side 0" in stageNameGroup and not "Upgrade Side 1" in stageNameGroup:
                    # Check if the line contains "vsphere_file.upload" or "vcd_catalog_item.AS_vm_template_upload" and "MCP"
                    if ("vsphere_file.upload" in line and "MCP" in line) or ("vcd_catalog_item.AS_vm_template_upload" in line and "MCP" in line):
                        # Extract the image name from the line
                        migrateImage=(line.split('upload')[1]).split(":")[0]
                        # Set the operation type as "installation"
                        operator="installation"
                        Images.append(operator)
                        Images.append(migrateImage)
                        break
                    elif "TASK [Upload /resources/images/" in line : 
                        migrateImage=(line.split('images/')[1]).split(" to")[0]
                        operator="installation"
                        Images.append(operator)
                        Images.append(migrateImage)
                        break
"""
The code sorts the contents of 5 lists: stageNameGroup, stageStartGroup, stageEndGroup, durationGroup, and colorListGroup. 
It uses the dates in the stageStartGroup list as a sort key. The code sorts the contents of all 5 lists based on the order of elements
in the sorted stageStartGroup list.
The code checks the value of Images list, which could contain one of the values "upgrade" or "migration".
If "upgrade" is present, it modifies the elements in the stageNameGroup list by prefixing "Primary " or "Secondary " 
to the elements depending on certain conditions. If "migration" is present, it modifies the elements in the stageNameGroup 
list by prefixing "Primary " or "Secondary " to the elements depending on certain conditions.
Finally, the code calls the halfPause function and passes the three lists stageNameGroup, stageStartGroup, and stageEndGroup as arguments.
"""
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
    flag = True

    if not Images==[]:
        if Images[0]=="upgrade":
            for i in range(len(stageNameGroup)):
                if stageNameGroup[i]=="Upgrade Duration Total 0":
                    if "Upgrade Side Rollback 0" in stageNameGroup:
                        Images[0]="upgrade-rollback"
                        stageNameGroup[i]= "Upgrade-Rollback Duration Total 0"
                    continue
                if stageNameGroup[i] == "Upgrade Side 1" or stageNameGroup[i] =="Upgrade Side Repair 1" or stageNameGroup[i] =="Upgrade Side Failed 1":
                # if stageNameGroup[i] == "Upgrade Side 1":
                    flag = False
                if stageNameGroup[i]=="Upgrade Side Rollback 0":
                    flag=True
                if flag:
                    if not  stageNameGroup[i].startswith("Primary "):
                        stageNameGroup[i] = "Primary " + stageNameGroup[i]
                else:
                    if not  stageNameGroup[i].startswith("Secondary "):
                        stageNameGroup[i] = "Secondary " + stageNameGroup[i]
        elif Images[0]=="migration":
            for i in range(len(stageNameGroup)):
                if stageNameGroup[i]=="Migration Duration Total 0":
                    continue
                if stageNameGroup[i] == "Secondary Migration 0":
                    flag = False
                if flag:
                    if not  stageNameGroup[i].startswith("Primary "):
                        stageNameGroup[i] = "Primary " + stageNameGroup[i]
                else:
                    if not  stageNameGroup[i].startswith("Secondary "):
                        stageNameGroup[i] = "Secondary " + stageNameGroup[i]

    halfPause(stageNameGroup,stageStartGroup,stageEndGroup)

"""
The code defines the halfPause function which adds a "half pause" item to the stageNameGroup, stageStartGroup, stageEndGroup, durationGroup,
and colorListGroup lists. The half pause is the time interval between two specific stages, namely "Primary Upgrade Side 0",
"Primary Migration 0", or "Secondary Upgrade Side Rollback 1" and "Secondary Upgrade Side 1", "Secondary Migration 0", or 
"Primary Upgrade Side Rollback 0". The function calculates the duration of this time interval and appends a new item to the lists with 
the calculated duration, a generated label "Half Pause", and the color "red".
"""
def halfPause(stageNameGroup,stageStartGroup,stageEndGroup):
    i=0
    k=0
    halfStart=""
    while i < len(stageNameGroup):
        if stageNameGroup[i]=="Primary Upgrade Side 0" or stageNameGroup[i]=="Primary Migration 0" or stageNameGroup[i]=="Secondary Upgrade Side Rollback 1":
            halfStart=stageEndGroup[i]
        if (stageNameGroup[i]=="Secondary Upgrade Side 1" or stageNameGroup[i]=="Secondary Migration 0" or stageNameGroup[i]=="Primary Upgrade Side Rollback 0") and not halfStart=="":
            halfEnd=stageStartGroup[i]
        
            try:
                duration=("Duration: "+str(datetime.strptime(halfEnd,'%Y-%m-%d %H:%M:%S')- datetime.strptime(halfStart,'%Y-%m-%d %H:%M:%S')))
            except:
                nullcontext
            stageNameGroup.append("Half Pause "+str(k))
            stageStartGroup.append(halfStart)
            stageEndGroup.append(halfEnd)
            durationGroup.append(duration)
            colorListGroup.append("red")
            k+=1
        i+=1


           

    
            
        