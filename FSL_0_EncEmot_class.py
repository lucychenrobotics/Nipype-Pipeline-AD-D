#Created by Qianyi Chen
import os
import xlrd
#Have options here to just click a folder (Tkinter can do this)
studyDir = "/Volumes/Research2/Lighthall_Lab/Experiments/CJfMRI/data/fmri"



#Self explanatory...
class part0(object):
    #Creates timing file for the model inputted
    def __init__(self, study, model, date, variableColumns, infoColumns, runColumn, weight = False):
        #Ex. of model = EncEmot based on checkboxes on GUI
        #study will be inputted at the beginning
        #date will be inputted individually for each model
        
        #####Creation of variables to hold directory paths####
        self.dataDir = studyDir + "/Data/Func"
        self.timingDir = studyDir + "/Data/Timing/" + model
        
        
        
        
        
        
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
                #checks whether the subject has timing data first
                #edut this later to use the excel module instead
                if(subject in "bruh"):
                    #Subject is not in timing masterfile ERROR
                    #Create a thing in gui that will pop up and say "continue? stop?"" if stop then "delete all files created during this run?"
                    print(subject + " not in timing masterfile!")
                else:
                    #Subject is in timing masterfile
                    
                    #Creates a directory to hold the new timing information if it doesn't exist
                    if os.path.exists(self.timingDir + "/%s" % subject):
                        #Subject has a file in timing
                        print("path EXISTS!")
                    else:
                        ####HERE IS WHERE ITLL GO AND MAKE TIMING FILES AFTER CHECKING EVERYTHING!!!!#########
                        os.mkdir(self.timingDir + "/%s" %subject)
                        self.createNewFiles(subject)


part0("CJfMRI", "JAcc", "05.12.17", [2,4], [6, 7], 1, 5)