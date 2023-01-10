# from cgi import print_form
# from fileinput import filename
# from pydoc import visiblename
# from turtle import color, fillcolor
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import glob
import plotly.subplots as sp



def getStagesInfo(path,stageNameGroup,stageStartGroup,stageEndGroup,durationGroup,colorListGroup,Images,labName):
   

    path = path+"\\"+"GanttFiles"
    if not os.path.exists(path):
        os.mkdir(path)
    files = glob.glob(path+"/*")
    for file in files:
        os.remove(file)

    fig1 = createFigure(stageStartGroup,stageEndGroup,stageNameGroup,stageNameGroup,colorListGroup)
    fig2 = createSimpleTable(stageStartGroup,stageEndGroup,path,stageNameGroup,durationGroup)
    fig3=createTableFig(stageStartGroup,stageEndGroup,path,stageNameGroup,durationGroup)
    if Images[0]=="upgrade":
        newImage = Images[1]
        prevImage = Images[2]
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages on upgrading from "+ prevImage +" to "+ newImage,path+r"//"+labName+"_from_"+prevImage+"_to_"+newImage+".html")
    elif Images[0]=="migration": 
        newImage = Images[1]
        prevImage = Images[2]
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages on migrating from "+ prevImage +" to "+ newImage,path+r"//"+labName+"_from_"+prevImage+"_to_"+newImage+".html")
    elif Images[0]=="installation": 
        newImage = Images[1]
        figures_to_html([fig1,fig2,fig3],"Task Overview","NOTE: This gantt chart shows stages on installation with "+ newImage,labName,path+r"//"+labName+"_"+newImage+".html") 


def createSimpleTable(stageStartGroup,stageEndGroup,newdir,stageNameGroup,durationGroup):
    tableStage=[]
    tableDuration=[]
    tableStart=[]
    tableEnd=[]
    for i in range(len(stageNameGroup)):
        if stageNameGroup[i]=="Upgrade Duration Total 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Primary Upgrade Side 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Secondary Upgrade Side 1":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Migration Duration Total 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Primary Migration 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Secondary Migration 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i]) 
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])  
        elif "Installation Duration Total" in stageNameGroup[i]:
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Primary installation 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i])
        elif stageNameGroup[i]=="Secondary installation 0":
            tableStage.append(stageNameGroup[i])
            tableDuration.append(durationGroup[i])
            tableStart.append(stageStartGroup[i])
            tableEnd.append(stageEndGroup[i]) 
    
    pathName='\SimpleStage.csv'
    filePath=newdir+pathName
    data = {'Task': tableStage, 'Start': tableStart, 'Finish': tableEnd, 'Duration':tableDuration}
    # if (os.path.exists(filePath) and os.path.isfile(filePath)):
    #     os.remove(filePath)
    df = pd.DataFrame(data)
    df.to_csv(filePath)
    # Creating a table in dash with CSV file
    df = pd.read_csv(newdir+pathName, index_col=0)
    df.sort_values(df.columns[3], 
                    axis=0,
                    inplace=False)
    
    fig3 = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                     fill_color='seagreen',
                    align='left'
                    ),
        cells=dict(values=[df.Task, df.Start, df.Finish, df.Duration],
                    fill_color='lavender',
                    align='left'
                    
                  )
                   )
    ])
    fig3.update_layout(
    width=1000,
    height=140,
    margin=dict(
    l=75,
    r=0,
    t=0,
    b=0
    
    )
)

  
    return fig3
    
def createTableFig(start,endTime,newDir,taskData,durationList):
    pathName='\Stage.csv'
    filePath=newDir+pathName
    data = {'Index':"",'Task': taskData, 'Start': start, 'Finish': endTime, 'Duration':durationList}
    # if (os.path.exists(filePath) and os.path.isfile(filePath)):
    #     os.remove(filePath)
    df = pd.DataFrame(data)
    df.to_csv(filePath)
    # Creating a table in dash with CSV file
    df = pd.read_csv(newDir+pathName, index_col=0)
    df.sort_values(df.columns[3], 
                    axis=0,
                    inplace=False)
    
    fig2 = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='seagreen',
                    align='left'),
        cells=dict(values=[df.index,df.Task, df.Start, df.Finish, df.Duration],
                    fill_color='lavender',
                    align='left'),
                    columnwidth=[10, 80, 80, 80],                         
                   )             
    ])
    fig2.update_layout(
        margin=dict(
        l=75,
        r=100,
        t=0,
        b=0
    ))  

    return fig2

def createFigure(start,endTime,taskAndDuration,taskFilterNamesList,color):   
    fig=px.timeline(x_start=start,x_end=endTime,y=taskAndDuration,color=taskFilterNamesList,color_discrete_sequence=color)

    
    fig.update_layout(height=1200)    

    fig.update_yaxes(autorange='reversed', title='Tasks')
    fig.update_xaxes(title='Time')
   
    fig.update_layout(
        
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
                        # {'shapes[{}].visible'.format(i):True for i in range(colorCount)}
                        
                        ]),
                    dict(label="None",
                        method="update",
                        args=[{"visible":['legendonly']},
                        # {'shapes[{}].visible'.format(i): False for i in range(colorCount)}

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
def figures_to_html(figs, header, note,guiLabName, filename):
    
    dashboard = open(filename, 'w')

    dashboard.write("<html><head></head><body>" + "\n")
    dashboard.write("<h1 style=\"text-align:center;font-size:40;\">"+header+"</h1>"+"\n")
    dashboard.write("<p style=\"color:red\"><strong>" + note + "</strong></p>" + "\n")
    dashboard.write("<p style=\"color:red\"><strong>"+guiLabName+"</strong></p>" + "\n")
    
    # dashboard.write("<p style=\"color:red\"><small>Option2: Removes all vertical lines</small></p>" + "\n")
    # dashboard.write("<p style=\"color:red\"><small>Option3: Removes vertical lines which far from other vertical lines</small></p>" + "\n")
        #dashboard.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>.vl {border-left: 4px solid green;height: 75px;position: absolute;left: 13%;margin-left: -3px;top: 100;}</style></head><body><h2>"+mgStart+"</h2><div class=\"vl\"></div>")
        #dashboard.write("<br><p><strong>" + mgTime + "</strong></p>")
    count=0
    for fig in figs:
        if count==2:
            inner_html = fig.to_html(div_id="my-table").split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        
        else:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        count+=1
    dashboard.write("""
        <script>
            const table = document.getElementById("my-table");
            table.addEventListener("mouseover", (event) => {
                const row = event.target.parentNode;
                row.style.backgroundColor = "yellow";
            });
        </script>
    """)
    dashboard.write("</body></html>" + "\n")
