import plotly.express as px
import pandas as pd
import os
import glob


"""
This is a Python function that generates a Gantt chart and converts it into an HTML file. It creates the Gantt chart using three figures,
fig1, fig2, and fig3. The function first checks if a directory named "GanttFiles" exists at the specified path and creates it if it does not. 
If it exists, the function removes all files in the directory. Then, it creates three figures using the "createFigure" and "createSimpleTable" 
functions, and generates the HTML file using the "figures_to_html" function, with different file names and titles based on the type of operation 
being performed, as specified in the "Images" list parameter. The possible types of operation are "upgrade", "upgrade-rollback", "migration", 
"installation", or "Null".
"""

# Create new directory and it calls the html method according to the operator type.
def getStagesInfo(path,stageNameGroup,stageStartGroup,stageEndGroup,durationGroup,colorListGroup,Images,labName):
   
    path = path+"\\"+"GanttFiles"
    if not os.path.exists(path):
        os.mkdir(path)
    files = glob.glob(path+"/*")
    for file in files:
        os.remove(file)

    fig1 = createFigure(stageStartGroup,stageEndGroup,stageNameGroup,stageNameGroup,colorListGroup)
    fig2=createSimpleTable(stageStartGroup,stageEndGroup,path,stageNameGroup,durationGroup)
    fig3=createTableFig(stageStartGroup,stageEndGroup,path,stageNameGroup,durationGroup)
    if Images==[]:
        Images.append("Null")
        Images.append("Null")
        Images.append("Null")
    else: 
        if "[" in Images[0] or "]" in Images[0]:
            Images[0]=((str(Images[0]).strip("[")).strip("]")).strip('"')
        elif "[" in Images[1] or "]" in Images[1]:
            Images[1]=((str(Images[1]).strip("[")).strip("]")).strip('"')
    if Images[0]=="upgrade":
        newImage = Images[1]
        prevImage = Images[2]
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages on "+labName+", upgrading from "+ prevImage +" to "+ newImage,path+r"//"+"Upgrade_"+labName+"_from_"+prevImage+"_to_"+newImage+".html")
    elif Images[0]=="upgrade-rollback":
        newImage = Images[1]
        prevImage = Images[2]
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages on "+labName+", upgrade-rollback from "+ prevImage +" to "+ newImage,path+r"//"+"Upgrade_Rollback_"+labName+"_from_"+prevImage+"_to_"+newImage+".html")
    elif Images[0]=="migration": 
        newImage = Images[1]
        prevImage = Images[2]
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages about "+labName+", migrating from "+ prevImage +" to "+ newImage,path+r"//"+"Migration_"+labName+"_from_"+prevImage+"_to_"+newImage+".html")
    elif Images[0]=="installation": 
        newImage = Images[1]
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages about "+labName+ ", installation with "+ newImage,path+r"//"+"Installation_"+labName+"_"+newImage+".html") 
    elif Images[0]=="Null":
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages about "+labName+", installation with MCP core",path+r"//"+"Installation_"+labName+".html") 


"""
This is a Python function that creates a simple table from a set of input arrays and saves it as a CSV file. The input arrays are:
stageStartGroup: an array of start times for each stage
stageEndGroup: an array of end times for each stage
newdir: a string representing the directory where the CSV file will be saved
stageNameGroup: an array of stage names
durationGroup: an array of durations for each stage
The function first creates four empty lists for stage names, start times, end times, and durations. It then iterates through each stage name in 
stageNameGroup, checks if it matches certain conditions (e.g. "Upgrade Duration Total 0", "Primary Upgrade Side 0", etc.), and if it does, it appends
the corresponding stage name, start time, end time, and duration to the respective lists.
Finally, the function creates a pandas dataframe from these lists, sorts the dataframe by duration, and saves it as a CSV file at the 
specified file path. It then returns the sorted dataframe.
"""
def createSimpleTable(stageStartGroup,stageEndGroup,newdir,stageNameGroup,durationGroup):
    tableStage=[]
    tableDuration=[]
    tableStart=[]
    tableEnd=[]
    for i in range(len(stageNameGroup)):
        if stageNameGroup[i]=="Upgrade Duration Total 0" or stageNameGroup[i]=="Upgrade-Rollback Duration Total 0" or stageNameGroup[i]=="Migration Duration Total 0" or "Installation Duration Total" in stageNameGroup[i]:
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Primary Upgrade Side 0" or stageNameGroup[i]=="Secondary Upgrade Side 1" or stageNameGroup[i]=="Secondary Upgrade Side 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Primary Migration 0" or stageNameGroup[i]=="Secondary Migration 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Secondary Upgrade Side Rollback 1" or stageNameGroup[i]=="Primary Upgrade Side Rollback 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif "Half Pause" in stageNameGroup[i] or "Net" in stageNameGroup[i]:
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
            
    pathName='SimpleStage.csv'
    data = {'Task': tableStage, 'Start': tableStart, 'Finish': tableEnd, 'Duration':tableDuration}
    df = pd.DataFrame(data)
    df.to_csv(pathName)
    # Creating a table in dash with CSV file
    df = pd.read_csv(pathName, index_col=0)
    df.sort_values(df.columns[3], 
                    axis=0,
                    inplace=False)
    return df
# Create another csv file with all stages 
def createTableFig(start,endTime,newDir,taskData,durationList):
    pathName='Stage.csv'
    data = {'Task': taskData, 'Start': start, 'Finish': endTime, 'Duration':durationList}
    df = pd.DataFrame(data)
    df.to_csv(pathName)
    # Creating a table in dash with CSV file
    df = pd.read_csv(pathName, index_col=0)
    df.sort_values(df.columns[3], 
                    axis=0,
                    inplace=False)
    return df
"""
This function generates a timeline figure using the Plotly library's px.timeline function. 
The timeline data is specified by the x_start and x_end parameters (for the start and end times of the tasks), 
the y parameter (for the task names), and the color parameter (for the task categories). The layout of the figure is updated
with the fig.update_* functions to adjust the axis titles, grid visibility, and menu. The menu is a dropdown that allows
the user to select either "All" or "None" of the tasks to display. The function returns the final figure.
"""
def createFigure(start,endTime,taskAndDuration,taskFilterNamesList,color):   
    
    fig=px.timeline(x_start=start,x_end=endTime,y=taskAndDuration,color=taskFilterNamesList,color_discrete_sequence=color)  
   
    fig.update_yaxes(autorange='reversed', title='Tasks')
    fig.update_xaxes(title='Time')
   
    fig.update_layout(
        height=1200,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        
        updatemenus=[

            dict(
                type="dropdown",
                direction="down",
                active=0,
                x=1,
                y=1,
            buttons=list([
                    dict(label="All",
                        method="update",
                        args=[{"visible":[True]},                        
                        ]),
                    dict(label="None",
                        method="update",
                        args=[{"visible":['legendonly']},
                        ],
                        ), 
                        
                ]),
                
            )
        ],
        
        title_font_size=14,
        font_size=8,
        title_font_family='Arial'
    )

    return fig


"""
The function figures_to_html takes four parameters:

figs: a list of figures/tables
header: a string that is used as the header of the HTML file
note: a string that is used to show a note in the HTML file
filename: a string representing the name of the HTML file to be created
The function creates an HTML file with the given filename and writes to it the header, note, and tables provided in the list figs.
The table data is written in HTML table format, with each column separated by a border and each row separated by a border. 
The table headers have a green background. The function also adds JavaScript code for highlighting a row on click and for exporting
the table as an Excel file.
"""
def figures_to_html(figs, header, note, filename):
    dashboard = open(filename, 'w', encoding="utf-8")
    dashboard.write("<html><head><meta http-equiv=\"content-type\" content=\"application/vnd.ms-excel; charset=UTF-8\"><style>table{border-collapse:collapse; width:100%;} th, td { border: 1px solid black; padding: 8px;} th { background-color: #90EE90;} tr:active { background-color: lightblue;} </style>")
    dashboard.write("""<script type="text/javascript">
  function highlightRow() { 
    var rows = document.getElementsByTagName("tr"); 
    for (var i = 0; i < rows.length; i++) { 
      rows[i].onclick = function() { 
        if (this.style.backgroundColor === "lightblue") { 
          this.style.backgroundColor = this.originalColor; 
        } else { 
          this.originalColor = this.style.backgroundColor; 
          this.style.backgroundColor = "lightblue"; 
        } 
      } 
    } 
  } 
  window.onload = highlightRow;
  
  var exportTable = (function(tableId) {
        var uri = 'data:application/vnd.ms-excel;base64,'
          , template = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><meta http-equiv="content-type" content="application/vnd.ms-excel; charset=UTF-8"><head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>{worksheet}</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head><body><table>{table}</table></body></html>'
          , base64 = function(s) { return window.btoa(unescape(encodeURIComponent(s))) }
          , format = function(s, c) { return s.replace(/{(\w+)}/g, function(m, p) { return c[p]; }) }
        return function(table, name) {
          if (!table.nodeType) table = document.getElementById(table)
          var ctx = {worksheet: name || 'Worksheet', table: table.innerHTML}
          var link = document.createElement("a");
          link.download = "stageTable.xls";
          link.href = uri + base64(format(template, ctx));
          link.click();
        }
      })()
</script></head><body>" + "\n""")
    dashboard.write("<h1 style=\"text-align:center;font-size:40;\">"+header+"</h1>"+"\n")
    dashboard.write("<p style=\"color:red\"><strong>" + note + "</strong></p>" + "\n")
    count=0
    for fig in figs:
        if count>0:
            dashboard.write("<table id='table"+str(count)+"'>")
            dashboard.write("<button onclick='exportTable(\"table"+str(count)+"\")'>Export</button>")
            dashboard.write("<tr>")
            dashboard.write("<th>Index</th>")
            colorFailed = False
            colorRepair=False
            for col in fig.columns:
                dashboard.write("<th>" + col + "</th>")
            dashboard.write("</tr>")
            for index, row in fig.iterrows():
                if 'failed' in row.to_string().lower() and not count==1:
                    colorFailed = True
                    colorRepair = False
                if 'repair' in row.to_string().lower() and not count==1:
                    colorFailed = False
                    colorRepair = True
                if 'upgrade side 0' in row.to_string().lower() and ('repair' not in row.to_string().lower() or 'failed' not in row.to_string().lower()) and not count==1:
                    colorFailed = False
                    colorRepair = False
                if 'upgrade side 1' in row.to_string().lower() and ('repair' not in row.to_string().lower() or 'failed' not in row.to_string().lower()) and not count==1: 
                    colorRepair = False
                    colorFailed = False
                if colorFailed:
                    dashboard.write("<tr style='color:#DC143C'>")
                elif colorRepair:
                    dashboard.write("<tr style='color:#7B68EE'>")
                else:
                    dashboard.write("<tr>")
                dashboard.write("<td>" + str(index) + "</td>")
                for val in row:
                    dashboard.write("<td>" + str(val) + "</td>")
                dashboard.write("</tr>")
            dashboard.write("</table>")
            dashboard.write("<br>")
            
        else:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
            
        count+=1
    dashboard.write("</body></html>" + "\n")
