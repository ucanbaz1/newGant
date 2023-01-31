# Time Measurement Tool

Raf has too many logs for an upgrade, migration, installation, etc. So we created a tool to check raf logs with the Gantt chart and in excel format. 

It allows us to see more clearly which stage started and ended when. And we can also see which stage takes how long to complete it.

## Overview
---
*   StageFile.txt
*   Tool.py
*   fileReader.py
*   stageReader.py
*   getStageTime.py
*   htmlCreate.py

### StageFile.txt
---
    A text file in which we specify which stages the operator logs such as 
    Installation, Upgrade, and Migration consists of, and the start task, 
    end task, and which log file these stages are in. 
    If we want to add a new stage, it should be in this format.

    stageName; logFileName; startTask; endTask

Example;

Shutdown VMs VCD; main-migration-primary.log; Shutdown VMs on VCD; shutdown_vms list
<style>
    p{
        color:green
    }

    </style>


### Tool.py
---
    We can call it the main python file of the tool. In this file, it 
    takes the necessary inputs as arguments, calls other python files, and 
    starts the logging tool.


### fileReader.py
--- 
    It reads log files line by line and converts time formats to desired 
    formats. If there are timestamps according to NTP time in the 
    commissioning logs, it corrects the timestamps in the commissioning 
    and configures logs. Apart from that, if there is a timestamp between 
    the VM logs and the stackApiServer, that is, the container log, it 
    also fixes it and rewrites the log files in the new directory.

### stageReader.py
--- 
    The code reads log files in a directory and classifies the logs into 
    different stages based on the stage names and their corresponding log 
    files. It then calls different functions to process each stage log 
    file. The stages include Upgrade Side, Image upload, VM creation, VM 
    disk replacement, main migration, commissioning and configure logs, 
    and several others. The code reads the stages and the log files from 
    the "stageFile.txt" and creates a dictionary "stageDict" to store the 
    stage name, log file name, start time, and end time of each stage. The 
    code then uses "os.listdir()" to get the list of log files in the 
    directory and checks the name of each log file to determine which 
    function to call for processing.

### getStageTime.py
--- 
    This code reads log files and gets the start and end time of various
    stages of the log file, such as upgrade duration, migration duration, 
    etc. The input parameters, "stageName", "stageFile", "startTask", 
    "endTask", "path", "patternNFormat", and "colorList", are used to 
    identify the stage and relevant information. The code uses the 
    "open()" function to open the log file and reads its contents line by 
    line using the "readlines()" method. The "re" library is used to 
    extract the relevant time information from the log file using regular 
    expressions. The code uses several variables to keep track of the 
    start and end times, as well as various flags to control the flow of 
    execution. The code also has functions to get the first time of the 
    log, the last time of the log, and the total duration of the 
    migration.

### htmlCreate.py
--- 
    This function generates a Gantt chart for a set of stages, each having 
    a start and end time. It is created using the Plotly Express library 
    and saved as an HTML file. The input parameters to the function 
    include:

    path: the directory where the HTML file and any auxiliary files will 
    be saved
    stageNameGroup: a list of names for each stage
    stageStartGroup: a list of start times for each stage
    stageEndGroup: a list of end times for each stage
    durationGroup: a list of durations for each stage
    colorListGroup: a list of colors to be used for each stage in the 
    Gantt chart
    Images: a list of names or descriptions of the type of operation being 
    performed. This can be "upgrade", "upgrade-rollback", "migration", 
    "installation", or "Null".
    labName: a string representing the name of the lab where the operation 
    is being performed
    The function creates three figures using the createFigure and 
    createSimpleTable functions and combines them into a single HTML file 
    using the figures_to_html function. The name and title of the HTML 
    file will depend on the type of operation specified in the Images 
    parameter. If the Images parameter is empty, it will default to 
    "Null".


    Finally, the function checks if the specified directory exists, and if 
    it does not, creates it. If the directory already exists, the function 
    removes all existing files in it before generating the HTML file.


    The figure_to_html method in Plotly is used to convert a Plotly figure 
    into an HTML format suitable for embedding in a web page. The method 
    returns a string of HTML code that can be saved as a standalone HTML 
    file, or embedded within another HTML file using an iframe or other 
    embedding method. The resulting HTML code is interactive, allowing 
    users to pan, zoom, and hover over data points in the figure. 
    Additionally, the HTML output is responsive, adjusting to the size of 
    the container it is embedded in. The figure_to_html method takes a 
    Plotly figure as input and returns the HTML representation of that 
    figure.
    
---


## Log Files Used:

### Upgrade
*   commissioning logs
*   configure logs
*   vnfr logs -->> from asVnf directory
*   stackApiServer log
### Migration
*   commissioning logs
*   configure logs
*   main migration primary and main migration secondary logs
*   stackApiServer log 
### Installation
*   commissioning logs
*   configure logs
*   stackApiServer log 
### Rollback
*   commissioning logs
*   configure logs
*   vnfr logs -->> from asVnf directory
*   stackApiServer log

## To Run Tool in Your Local
---
*   git clone project
*   Collect the logs you will use under a path
*   Run with this command
    *   python Tool.py --dir path --labname labname

**path is your logs directory**

**labname is which lab's logs are you using**