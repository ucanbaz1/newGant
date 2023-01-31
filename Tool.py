from fileReader import fileMethod
from fileReader import patternNFormat
from stageReader import stageMethod
from stageReader import stageTimeDict
from getStageTime import getKeys
from getStageTime import stageNameGroup,stageStartGroup,stageEndGroup,durationGroup,colorListGroup,Images
from htmlCreate import getStagesInfo
import argparse

# This color list is used to color each stage differently in the Gantt chart.
colorList=['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanchedalmond', 'blue',
 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson',
  'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 
  'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey',
   'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite',
    'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'grey', 'green', 'greenyellow', 'honeydew', 
    'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue',
     'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgrey', 'lightgreen', 'lightpink', 'lightsalmon',
      'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
       'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen',
        'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose',
         'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod',
          'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple',
           'red', 'rosybrown', 'royalblue', 'rebeccapurple', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna',
            'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle',
             'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen',
              'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue',
     'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgrey', 'lightgreen', 'lightpink', 'lightsalmon',
      'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
       'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen',
        'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose',
         'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod',
          'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple',
           'red', 'rosybrown', 'royalblue', 'rebeccapurple', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna',
            'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle',
             'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen'

]
"""
This code defines a Python class Main that uses the argparse library to parse command-line arguments. 
The two expected arguments are '--dir' for the directory path and '--labName' for the name of the lab. The parsed arguments are stored
in the 'args' variable and can be accessed using 'args.dir' and 'args.labName'.

The code then calls four functions: 'fileMethod', 'stageMethod', 'getKeys', and 'getStagesInfo' and passes 'path' and 'labName' as arguments. 
The exact implementation of these functions is not shown in the code snippet provided.
"""
class Main():

    path = input("Enter Directory: ")
    labName = input("Enter Lab Name: ")

    # Gets inputs with argparse librariy
    # parser = argparse.ArgumentParser(description='Process some Strings.')
    # parser.add_argument('--dir', type=str, 
    #                    )
    # parser.add_argument('--labName', type=str, 
    #                    )
    # args = parser.parse_args()
    
    # path = args.dir
    # labName=args.labName
    # print(args.dir)
    # print(args.labName)

    
    # calls method from other python files
    fileMethod(path)
    stageMethod(path)
    getKeys(path,stageTimeDict,patternNFormat,colorList)
    getStagesInfo(path,stageNameGroup,stageStartGroup,stageEndGroup,durationGroup,colorListGroup,Images,labName)

    