import os
import csv
from contextlib import nullcontext




stageFile="stageFile.txt"
stageNameList=[]
stageDict={}
stageTimeDict={}
vnfrCount=0
"""
This code is a log comparator that takes a path and a dictionary of stages as input. 
It then searches the logs in the directory specified by the path and compares the contents 
of the log files with the stages in the dictionary. The code checks the name of each log file
and performs a specific operation depending on the stage name and log file name. If the log 
file name is "stackApiServer.log", the code performs one of several operations, such as
"getMCPVersion", "getVCDCreation", "getVCDRemoving", "threeStages", "manuelRaf", "vmCreationVmware", 
"vmDiskReplacement", "VMCreate", or "ObjectsCreate". If the log file name is "vnfr", the code performs 
the "vnfrStages" operation. If the log file name is "main-migration", the code performs one of several 
operations, such as "getDbBackup", "getShutdownVMs", "vmRemoveMainMigration", or "newConfigFileWriter". 
If the log file name is "commissioning" or "configure", the code performs the "newConfigFileWriter" operation.

"""
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
            # Checks if stage log file name stackApiServer and searh stagenames
            if stageFile in filename and stageFile=="stackApiServer.log":
                if stageName=="Image upload VCD" or stageName=="Image upload VmWare":
                    getMCPVersion(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="VM Creation VCD":
                    getVCDCreation(stageFile,stageName,stageStart,stageEnd,path)
                elif stageName=="Remove VCD VM":
                    getVCDRemoving(stageFile,stageName,stageStart,stageEnd,path)
                elif (stageName=="Config Drive") or (stageName=="Create cloud-init ISO") or (stageName=="Create cloud-init ISO AS") or (stageName=="Check Vnfr Reachable") or (stageName=="Remove VMWARE VM") or (stageName=="Create As Tarbal") or (stageName=="commission-vm-from-raf"):
                    threeStages(stageFile,stageName,stageStart,stageEnd,path)
                elif (stageName=="Manuel Half RAF VMs"):
                     manuelRaf(stageFile,stageName,stageStart,stageEnd,path)
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
                
            #Checks if stage log file name main migration
            elif (stageName=="Wait for SM" or stageName=="Migrate DB") and "commissioning" in filename:
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
def manuelRaf(stageFile,stageName,stageStart,stageEnd,path):
    serverNEList = []
    with open(os.path.join(path, stageFile), 'r') as f:
            lines = f.readlines()
            for line in lines:
                if stageStart.strip("<ServerName>") in line :
                    ServerNEName = (line.split("on")[1]).split("in")[0]
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
                if ("Schedule object" in line) and ("as_generic" in line.lower() or "vnf" in line.lower()):   
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


"""
This code is updating the stages in a configuration file by replacing placeholder values with actual values.
The code takes in the following parameters:

serverNEList: a list of server names
stageName: the name of the stage
stageStart: the start task of the stage
stageEnd: the end task of the stage
stageFile: the file containing the stage configuration
filename: the name of the output file
path: the path to the output file
For each server name in serverNEList, the code performs the following steps:

If "Calling" is in stageStart, it updates the stage name by replacing a placeholder value with 
the server name, updates the start task by replacing the server name placeholder with the actual 
server name, and sets the end task to be the same as stageEnd.
If the stage name is "VM Create", it updates the stage name by appending the server name,
updates the start task by replacing the server name placeholder with the actual server name, 
and updates the end task by replacing a placeholder value with the server name without the "config-" prefix.
For all other stage names, it updates the stage name by appending the server name, 
updates the start task by replacing the server name placeholder with the actual server name, 
and updates the end task by replacing a placeholder value with the actual server name.

Finally, the function calls another function named "newConfigFileWriter" and passes in the updated stage name, stage file, start task, end task, output file name, and output path.
"""
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

"""
newConfigFileWriter function updates a dictionary called stageTimeDict which is storing information
about a certain stage. The function checks if the stage name is already in the dictionary, 
and if it is, it will add a unique identifier to it 
(by adding the value of the variable vnfrCount to the stage name). 
If the stage name is not already in the dictionary, the function will store the stage name, 
the stage file, the start task, and the end task in the dictionary.
"""
def newConfigFileWriter(stageName, stageFile, startTask, endTask,filename,path):
    isThere=False

    if stageName in stageTimeDict:
        if not stageTimeDict[stageName][0]==filename and not filename==None:
            global vnfrCount
            stageName=stageName+str(vnfrCount)
            vnfrCount+=1 
        else:
            print("{} ---->>>> is already there so skipping".format(stageName))
            isThere=True
    if not isThere:  #Put into the dictioanry if it is not dublicated  
            if not filename ==None:
                stageTimeDict[stageName]=[filename,startTask,endTask]
            else: 
                stageTimeDict[stageName]=[stageFile,startTask,endTask]
        
# Reads stage file txt
def stageMethod(path):
    with open(stageFile, 'r') as f:

        for line in f:
            if line.startswith("#") or line.startswith("\n"):
                pass
            else:
                stageItems = (line.replace('; ',';')).split(";")
                stageNameList.append(stageItems[0])
                stageDict[stageItems[0]]=[stageItems[1],stageItems[2],stageItems[3]]
    logCompare(path,stageDict)






