#The library used for determining if a file exists
import os.path


def filePosUpdate(fileName, newLine, LastLineFile):
	"""
	A function that updates the last parsed line of the various files in a file
	
	The function looks for an already exists last line file, if it exists it looks
	for fileName's entry.  If found, it updates the last line and rewrites the file
	with the new line.  If not found it appends the new file to the end of the file.
	If the file doesn't exist it creates it and adds fileName and the line to it 

	Parameters:
	fileName (String):The file name the entry that needs to be updated
	newLine (int): the last line parsed,
	LastlineFile (String): The file where last line parsed is recorded.
	
	Libraries:
	Uses the library os.path
	"""
	fileLines = []														#Will contain the current contents of the last line parsed file
	fileFound = False													#Used to keep track if the file name already existed in the last line parsed file 
	if(os.path.isfile(LastLineFile)):									#If the file exists, grab the contents
		readIn = open(LastLineFile)										#Open the last line parsed file to grab the contents
	
		for line in readIn:
			currentLine = line.split(",")								#Split each line at the comma
			fileLines.append(currentLine)								#Add the split line to the list

		for i in fileLines:												#Search through the list for the passed fileName
			if(i[0] == fileName):										#if it was found
				i[1] = newLine											#Update the last line parsed
				fileFound = True										#set the flag to state the file was found
				break													#Break out of the for loop, the file was found
		readIn.close()													#Close the file for reading

	if(fileFound == False):												#If the file wasn't found, just append it to the end of the list
		fileLines.append([fileName,newLine])

	out = open(LastLineFile, 'w')										#Open the file in overwrite mode
	for j in fileLines:
		output = str(j[0])+','+str(int(j[1]))+'\n'						#Output the contents of the last line parsed list
		out.write(output)


def findFilePos(fileName, LastLineFile):
	"""
	A function that takes a file name and determines where the parser left off last time
	
	The function reads line by line and splits each line by the commas.  It looks through the 
	create list for the fileName and if found returns the number following it.  Otherwise, if
	not found, a 0 is returned.

	Parameters:
	fileName (String): file name to look for 
	LastLineFile (String): the file that keeps track of last line parsed
	
	findFilePos:
	int: The line that it left off on, or 0 if the fileName didn't exist

	Libraries:
	Uses the library os.path
	"""
	if(os.path.isfile(LastLineFile)):									#If the file exists, grab the contents
		fileLines = []													#Will contain the current contents of the last line parsed file
		readIn = open(LastLineFile)										#Open the last line parsed file to grab the contents
		for line in readIn:
			currentLine = line.split(",")								#Split each line at the comma
			fileLines.append(currentLine)								#Add the split line to the list

		for i in fileLines:												#Search through the list for the passed fileName
			if(i[0] == fileName):										#if it was found
				readIn.close()											#Close the file
				return int(i[1])										#return the last file found

		readIn.close()													#Close the file
		return 0														#The file name wasn't in the list so just return 0
	else:
		return 0														#File doesn't exist, return 0



