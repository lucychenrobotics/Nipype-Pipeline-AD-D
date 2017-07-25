#Created by Qianyi Chen

import os
import xlrd

"""
NOTES:
1.It expects the timing files to be in the studyDir/Data/Timing/model
2.It expects the data files to be in studyDir/Data/Func
3.It expects the timing file to be named as study_model_date_master.xlsx"
^You can change all these in def __init__

4. If you don't specify a column holding weight, it will automatically assign a weight of one to everything
5. Go to the very bottom for further instructions
"""



#Here you put the directory to where the files are
#Make sure if the directory is the research directory, to put /volumes/ in front of it
studyDir = "/Volumes/Research2/Lighthall_Lab/Experiments/CJfMRI/data/fmri"


class part0(object):
    #Creates timing file for the model inputted
    def __init__(self, study, model, date, variableColumns, infoColumns, runColumn, weight = False):  
        #####Creation of variables to hold directory paths####

        ##Change this if file structure is changed
        #Datadir should hold a file for each subject
        self.dataDir = studyDir + "/Data/Func"

        #Timingdir should hold the timing files for that model, specifically in this file there should be an excel spreadsheet for that model
        self.timingDir = studyDir + "/Data/Timing/" + model
        
        #This is what the timing excel file should look like
        self.timingMasterFilePath = "%s/%s_%s_%s_master.xlsx" % (self.timingDir, study, model, date)
        self.study = study
        self.model = model
        self.date = date
        self.variableColumns = variableColumns
        self.infoColumns = infoColumns
        self.runColumn = runColumn
        self.weight = weight
        self.createNewDir()
    



    def createNewFiles(self, subject):
        print("run")
        listVariables = []
        listVariablesData = []
        
        #Change this a bit according to largest variable
        colSpace = 10
        
        
        
        #Right now have the gui give an option to click the file
        book = xlrd.open_workbook(self.timingMasterFilePath)
        
        #Grabs the first sheet (should be the only sheet) of the excel file
        firstSheet = book.sheet_by_index(0)
        
        
        currentRun = 1
        
                        
        def saveTimingFile(currentRun):
            for indVariable in range(len(listVariablesData)):
                #Edited
                variableFileName = str(subject) + "R" + str(int(currentRun)) + "_"
                print(variableFileName)
                for eachVariable in range(len(self.variableColumns)):
                    variableFileName += str(listVariables[indVariable][eachVariable])
                print("saved", currentRun, subject, variableFileName)
                f = open('%s/%s/%s.txt' % (self.timingDir, str(subject), variableFileName), "w+")
                for row in range(len(listVariablesData[indVariable])):
                    for data in range(len(listVariablesData[indVariable][row])):
                        marginSpace = colSpace - len(str(listVariablesData[indVariable][row][data]))
                        f.write(str(listVariablesData[indVariable][row][data]) + " "*marginSpace)
                    f.write("\n")
                f.close()
                
                
        
            
        #Goes through each row and puts it in the data in the appropriate part of
        #listVariableData
        #Checks for all the independent variables
        for row in range(1, firstSheet.nrows):
            #checks and makes sure that the row is related to the subject first
            if(str(int(firstSheet.cell(row, 0).value)) == subject):
           
                rowVariable = [firstSheet.cell(row, col).value for col in self.variableColumns]
                rowData = [firstSheet.cell(row, col).value for col in self.infoColumns]
                runData = firstSheet.cell(row, self.runColumn).value
                if(self.weight == False):
                    rowData.append(1)
                else:
                    rowData.append(firstSheet.cell(row, self.weight))
                
    
                
                #Checks if new run started        
                if(currentRun < runData):
       
                    saveTimingFile(currentRun)
                    print(row)
                    listVariables = []
                    listVariablesData = []
                    currentRun = runData
                    
                #Checks to see if it's a new independent variable
                if(rowVariable not in listVariables):
                    listVariables.append(rowVariable)
                    listVariablesData.append([])
                
                #Adds it to the appropriate part of the arrays
                variablePos = listVariables.index(rowVariable)
                listVariablesData[variablePos].append(rowData)
        
        
            ##You've reached the end, you should save the data for the last run        
            if(row == firstSheet.nrows - 1):
                saveTimingFile(currentRun)
                    




    def createNewDir(self):
        # Loop through every subject in the Data Directory
        # Under the assumption that each subject has a file and it isn't just a run
        for subject in os.listdir(self.dataDir):
            #.ds_store files are not subjects
            
            if(subject == ".DS_Store"):
                    pass
            else:
                #Creates a directory to hold the new timing information if it doesn't exist
                if os.path.exists(self.timingDir + "/%s" % subject):
                    #Subject has a file in timing
                    print("path EXISTS!")
                else:
                    ####HERE IS WHERE ITLL GO AND MAKE TIMING FILES AFTER CHECKING EVERYTHING!!!!#########
                    ###This is what the file will look like
                    os.mkdir(self.timingDir + "/%s" %subject)
                    self.createNewFiles(subject)



#####HERE YOU WILL GIVE IT ALL THE INFORMATION########
#For each timing file you want to  make, copy and paste this line and add in the information
#The study, model, and date should be in quotes ("")
#the variableColumns and infoColumns should be in brackets ([]) even if there is only one

#part0(study, model, date, variableColumns, infoColumns, runColumn, weight)

"""What each of them is:
If timing file name is: CJfMRI_JAcc_05.12.17.xlsx

Study - study name as is in the timing file (EX: "CJFMRI")
model - model name as is in the timing file (EX: "JAcc", "EncEmot")
date - date of the timing file if it's in the name of the timing file (EX: "05.12.17")
variableColumns - Columns of the variables that determine which category it belongs into, the independent variables. 
(EX: Column 2 holds "Sing" or "Double", Column 4 holds "Low" or "High", therefore it will create 4 text files, sing_low, sing_high, double_low, double_high)
infoColumns - Column that holds the information corresponding to that data point
(EX: Column 6 holds the onset(s) and column 7 holds the duration(s))
runColumn - Column that specifies what run it is
weight - Column that specifies the weight, if no column specifies the weight just take this out.
"""
##This is an example##
#part0("CJfMRI", "JAcc", "05.12.17", [2,4], [6, 7], 1, 5)

##If no weight
#part0("CJfMRI", "JAcc", "05.12.17", [2,4], [6, 7], 1)

#Don't actually copy the #, this makes the line a comment, which means that it doesn't actually run



