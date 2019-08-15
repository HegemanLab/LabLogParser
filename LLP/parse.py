#The regular expression library used for the parser
import re
#The functions to update and retrieve last line parsed from a file
import LLP.filepos


def parseFile(pattern, fileName, line, LastLineFile):
	"""
	A function that parses a given file with a given pattern, staring at a given line
	
	The functions uses regular expressions to pick up where the function left of last time it parsed
	the file and returns the results.  It keeps track of where it left off for next time.

	Parameters:
	pattern (String): Receives a pattern to parse the file with
	fileName (String): The name of the file to parse,
	line (int): The line to start parsing the file at
	LastLineFile (String): The file containing the last line parsed of each file.
	
	Returns:
	parsedLogs (List): A list of dictionaries containing the parsed logs and their individual fields
	
	Libraries:
	Uses the library re and LLP.filepos
	"""
	dataFile = open(fileName, encoding="utf8", errors='ignore')
	parsedLogs = []														#Create a empty list to hold the parsed logs
	for i in range(line):												#Ignore the first (line) lines of the file
		next(dataFile, None)
	parsedLogs = [m.groupdict() for m in re.finditer(pattern,dataFile.read(),re.UNICODE | re.MULTILINE)]
	LLP.filepos.filePosUpdate(fileName, file_len(fileName), LastLineFile)#call a function that will adjust the line on the current file.
	dataFile.close()
	return parsedLogs


def file_len(fname):
	"""
	A function that calculates the length of a file
	 
	Parameters:
	fname (String): A file name
	
	Returns:
	int: The passed file's length
	
	Source: https://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
	"""
	i = 0
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1


