import os
import csv
from contextlib import nullcontext


"""
This python file reads trial file and gets stages if there are in logs file. Then it creates config.csf file for all stages.
"""

# path =""
trialFile="myTrial.txt"
stageNameList=[]
stageList=[]
stageDict={}
stageTimeDict={}

# This function reads dictionary and check stages with if statement. Then it sends to interested function.
def logCompare(path,stageDict):
    main1= "main-migration-primary.log"
    main2 = "main-migration-secondary.log"
    path=path+'/'+'UpdatedLogs'
    isExist1 = os.path.join(path, main1)
    isExist2 = os.path.join(path, main2)
    for filename in os.listdir(path):
       # Skip files that are not log files
        if not filename.endswith(".log"):
           continue
        
        for i in stageNameList:
            stageName=i
            stageFile=stageDict[i][0]
            stageStart=stageDict[i][1]
            stageEnd=(stageDict[i][2]).replace("\n","")

            # If main-migration logs in path pass upgrade stages
            if  os.path.exists(isExist1) or  os.path.exists(isExist2):
                if stageName =="Upgrade Side" or stageName =="Upgrade Duration Total":
                    continue
            # Checks if stage log file name stackApiServer
            if stageFile in filename and stageFile=="stackApiServer.log":
                if stageName=="Image upload VCD" or stageName=="Image upload VmWare":
                    getMCPVersion(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="VM Creation VCD":
                    getVCDCreation(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="Remove VCD VM":
                    getVCDRemoving(stageFile,stageName,stageStart,stageEnd,path)
                elif (stageName=="Config Drive") or (stageName=="Create cloud-init ISO") or (stageName=="Remove VMWARE VM") or (stageName=="Create cloud-init ISO VCD") :
                    threeStages(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="VM Creation":
                    vmCreationVmware(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="VM Disk Replacement":
                    vmDiskReplacement(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="VM Create":
                    VMCreate(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="Installation Duration Total":
                    ObjectsCreate(stageFile,stageName,stageStart,stageEnd,path)
                else:
                    otherStages(stageFile,stageName,stageStart,stageEnd,path)   
            # Checks if stage log file name vnfr
            elif stageFile in filename and stageFile=="vnfr":
                vnfrStages(filename,stageName,stageStart,stageEnd,path)
            # Checks if stage log file name main mifration
            elif stageFile in filename and "main-migration" in stageFile:
                if stageName=="Get DB Backup and Transfer":
                    getDbBackup(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="Shutdown VMs" or stageName=="Shutdown VMs VCD":
                    getShutdownVMs(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="VM Remove VMware" or stageName=="VM Remove VCD":
                    vmRemoveMainMigration(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="Migration Duration Total":
                    newConfigFileWriter(stageName, stageFile, stageStart, stageEnd,filename,path)
                else:
                    otherStages(stageFile,stageName,stageStart,stageEnd,path)
            # Checks if stage log file name commissioning or configure
            elif stageName == "Commisioning and Configure logs" and ("commissioning" in filename or "configure" in filename): 
                newConfigFileWriter(filename, filename, stageStart, stageEnd,filename,path)
                
            #Checks if stage log file name main mifration
            elif (stageName=="Wait for SM to be Migrated" or stageName=="Migrate DB") and "commissioning" in filename:
                    otherStages(filename,stageName,stageStart,stageEnd,path)


#Reads log file and if stage name in log file 
def getMCPVersion(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "vsphere_file.upload" in line and "MCP" in line and "Creating..." in line and stageName=="Image upload VmWare":
                    MCPName=(line.split('upload')[1]).split(":")[0]
                    serverNEList.append(MCPName) 
                if "AS_vm_template_upload" in line and "Creating..." in line and not "Still" in line and stageName=="Image upload VCD":  
                    MCPName=(line.split('upload')[1]).split(":")[0]
                    serverNEList.append(MCPName) 
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
#Reads log file and if stage name in log file        
def getVCDCreation(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if ("Creating..." in line and "AS_vm"in line) and (not "Still" in line and not "insert_media" in line and
                 not "cloud_iso_upload" in line and not "secondary_disk" in line and not "template_upload" in line) :
                    CreationVMName=(line.split('AS_vm')[1]).split(":")[0]
                    serverNEList.append(CreationVMName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
#Reads log file and if stage name in log file 
def getVCDRemoving(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if ("Destroying..." in line and "AS_vm"in line) and (not "Still" in line and not "insert_media" in line and
                 not "cloud_iso_upload" in line and not "secondary_disk" in line and not "template_upload" in line):
                    removeVMName=(line.split('AS_vm')[1]).split(":")[0]
                    serverNEList.append(removeVMName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
#Reads log file and if stage name in log file 
def threeStages(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList = []
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if stageStart.strip("<ServerName>") in line :
                    ServerNEName = (line.split(".yml ")[1]).split("\n")[0]
                    serverNEList.append(ServerNEName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
#Reads log file and if stage name in log file 
def vmCreationVmware(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList = []
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "VM Creation" in stageName and stageStart.strip("<ServerName>") in line :
                    ServerNEName = (line.split("disk")[1]).split(".")[0]
                    serverNEList.append(ServerNEName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
#Reads log file and if stage name in log file 
def vmDiskReplacement(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if stageStart.strip("<ServerName>") in line:
                        line = line.split('] ')[1]
                        ServerNEName = line.split(":")[1]
                        ServerNEName=(ServerNEName.split(" ")[1]).split(" ")[0]
                        serverNEList.append(ServerNEName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
#Reads log file and if stage name in log file 
def VMCreate(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if stageStart.strip("<ServerName>") in line:
                        line = line.split('] ')[1]
                        ServerNEName = (line.split("Create ISO from /objects/as_generic_vnf/resources/KvmAsRg/")[1]).split("]")[0]
                        serverNEList.append(ServerNEName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
#Reads log file and if stage name in log file 
def ObjectsCreate(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if ("Schedule object" in line) and ("as_generic" in line or "vnf" in line):   
                    line = (line.split("Schedule object ")[1]).split(" create")[0]
                    ServerNEName = line
                    serverNEList.append(ServerNEName)
                    
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 
# Reads log file and if stage name in log file 
def otherStages(stageFile,stageName,stageStart,stageEnd,path):
    with open(os.path.join(path, stageFile), 'r') as f:
        lines = f.readlines()
        for line in lines:
            
            if stageStart in line:
                if "commissioning" in stageFile:
                    stageName= stageName+" "+stageFile.split("-")[0] 
                newConfigFileWriter(stageName, stageFile, stageStart, stageEnd,None,path)
                break
#Reads log file and if stage name in log file 
def vnfrStages(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if stageStart.strip("<ServerName>") in line:
                    ServerNEName = "-e"+(line.split("-e")[1]).split("],")[0]+ "]"
                    serverNEList.append(ServerNEName)
    if not serverNEList== []:
        updateStages(serverNEList,stageName,stageStart,stageEnd,"vnfr",stageFile,path) 
#Reads log file and if stage name in log file 
def getDbBackup(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "TASK [Transfer DB backup from" in line:
                        line = (line.split("from ")[1]).split(" VM")[0]
                        ServerNEName = line
                        serverNEList.append(ServerNEName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 

#Reads log file and if stage name in log file 
def getShutdownVMs(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "to shutdown_vms list" in line:
                        line = (line.split("Add ")[1]).split(" to")[0]
                        ServerNEName = line
                        serverNEList.append(ServerNEName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path) 

#Reads log file and if stage name in log file 
def vmRemoveMainMigration(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList=[]
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "Get logical volume names of VM" in line:
                        line = (line.split("VM ")[1]).split("]")[0]
                        ServerNEName = line
                        serverNEList.append(ServerNEName)
    updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,None,path)                    
#This functions updates stages for servername.
def updateStages(serverNEList,stageName,stageStart,stageEnd,stageFile,filename,path):
    for i in serverNEList:
        if "Calling" in stageStart:
            stageUpdate = (i.split("[")[1]).split("]")[0]
            prevServerName="<ServerName>"
            VMStageName = stageName.replace(prevServerName,stageUpdate)
            VMStartTask = stageStart.replace(prevServerName, i)
            VMEndTask = stageEnd
        elif stageName=="VM Create":
            prevServerName="<ServerName>"
            VMStageName = stageName + " " + i
            VMStartTask = stageStart.replace(prevServerName, i)
            VMEndTask = stageEnd.replace(prevServerName, i.split("config-")[1])
        else:
            prevServerName="<ServerName>"
            VMStageName = stageName + " " + i
            VMStartTask = stageStart.replace(prevServerName, i)
            VMEndTask = stageEnd.replace(prevServerName, i)
        newConfigFileWriter(VMStageName, stageFile, VMStartTask, VMEndTask,filename,path)    

#Creates config.csv for stages and it creates a dictionary.
def newConfigFileWriter(stageName, stageFile, startTask, endTask,filename,path):
    isThere=False
    for i in stageList: # Check if stageName is a dublicated data or not 
        if stageName ==i:
            print("{} ---->>>> is already there so skipping".format(i))
            isThere=True
            break
    if not isThere:  #Put into the lists if it is not dublicated  
        stageList.append(stageName)
        with open(path+'/Config.csv', 'a', newline='') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)
            # Write the column headers if the file is empty
            if csvfile.tell() == 0:
                writer.writerow(['StageName', 'LogFileName', 'StageTaskStart', 'StageTaskEnd'])
            # Write the data to the file, one column at a time
            writer.writerow([stageName, stageFile, startTask,endTask])
            if not filename ==None:
                stageTimeDict[stageName]=[filename,startTask,endTask]
            else: 
                stageTimeDict[stageName]=[stageFile,startTask,endTask]
        
# Reads trial file and assign stages in a dictionary
def stageMethod(path):
    with open(trialFile, 'r') as f:

        for line in f:
            if line.startswith("#") or line.startswith("\n"):
                pass
            else:
                stageItems = (line.replace('; ',';')).split(";")
                stageNameList.append(stageItems[0])
                stageDict[stageItems[0]]=[stageItems[1],stageItems[2],stageItems[3]]
        
        try:
            os.remove(path + "/Config.csv")
        except:
            nullcontext
    logCompare(path,stageDict)






