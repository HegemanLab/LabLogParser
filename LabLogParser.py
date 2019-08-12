#*** LabLogParser *************************************************************************
# Created by: Luke Gentle, Mark Elser, Arthur Eschenlauer, Adrian Hegeman, and Jerry Cohen
#
# Made on: 8/6/2019
# 
# Last Updated on: 8/8/2019
#
# A Program to parse logs and uploads the results to a influxdb database.
#
# Uses the re, os.path, sys, datetime, and influxdb libraries
#
#******************************************************************************************

#The regular expression library used for the parser
import re
#The library used for determining if a file exists
import os.path
#Library for passing arguments with python script
import sys
#Library for sending parsed logs to influxdb
from influxdb import InfluxDBClient
#Used for converting string to timestamp
from datetime import datetime

from os import listdir

from os.path import isfile, join

#Global variables parsed from configuration file
LAST_LINE_FILE = ""
FILE_NAME = ""
PARSING_PATTERN = ""
TIMESTAMP_PATTERN = "%m/%d/%y %H:%M:%S"
FN = ""
FIELDS = []
HOST = ""
PORT = ""
DATABASE = ""
MEASUREMENT = ""


#*** main *********************************************************************************
# The program parses logs 
# 
# The function calls the function to parse the configuration file and then calls the function
# to output the result to influxdb with the results of the formatOutput function which is called
# pattern to parse the file to parse and the last line parsed from the line file.
#
# Prints the parased logs to stdout.  The end goal is sending it to a influxdb database.
#
# Uses the sys library
#
#******************************************************************************************
def main():
	if(len(sys.argv) > 1):												#If the user provided an argument, use that for the config file
		parseConfigFile(sys.argv[1])
	else:																#Otherwise, use a configFile in the same directory
		parseConfigFile(os.path.join(os.path.dirname(__file__), "configFile"))
	if(FILE_NAME[len(FILE_NAME)-1] == '/'):
		filesToParse = [f for f in listdir(FILE_NAME) if isfile(join(FILE_NAME, f))]
		for files in filesToParse:
			print(FILE_NAME,files,"starting...")
			influxDBOutput(formatOutput(parseFile(PARSING_PATTERN, str(FILE_NAME+files), findFilePos(str(FILE_NAME+files))),str(FILE_NAME+files)))
			print(FILE_NAME,files,"parsed.")
	else:
		influxDBOutput(formatOutput(parseFile(PARSING_PATTERN, FILE_NAME, findFilePos(FILE_NAME))))


#*** parseFile ***************************************************************************
# A function that parses a given file with a given pattern, staring at a given line
# 
# Recieves a pattern to parse the file with, the name of the file to parse,
# and the line to start parsing the file at.
#
# Returns a list of lists containing the parsed logs and their individual fields
#
# Uses the library re
#
#******************************************************************************************
def parseFile(pattern, fileName, line):
	dataFile = open(fileName, encoding="utf8", errors='ignore')
	parsedLogs = []														#Create a empty list to hold the parsed logs
	for i in range(line):												#Ignore the first (line) lines of the file
		next(dataFile, None)
	parsedLogs = re.findall(pattern,dataFile.read(),re.UNICODE | re.MULTILINE)		#Parse the rest of the file
	filePosUpdate(fileName, file_len(fileName))							#call a function that will adjust the line on the current file.
	dataFile.close()
	return parsedLogs


#*** file_len ****************************************************************************
# A function that calculates the length of a file
# 
# Recieves a file name
#
# Returns a file length
#
# Source: https://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
#******************************************************************************************
def file_len(fname):
	i = 0
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1


#*** filePosUpdate ***********************************************************************
# A function that updates the last parsed line of the various files in a file
# 
# Recieves the file name the entry that needs to be updated and the last line parsed.
# It also uses the global variable, lineFile, which is the file where last line parsed is recorded.
#
# Uses the library os.path
#
#******************************************************************************************
def filePosUpdate(fileName, newLine):
	fileLines = []														#Will contain the current contents of the last line parsed file
	fileFound = False													#Used to keep track if the file name already existed in the last line parsed file 
	if(os.path.isfile(LAST_LINE_FILE)):									#If the file exists, grab the contents
		readIn = open(LAST_LINE_FILE)									#Open the last line parsed file to grab the contents
	
		for line in readIn:
			currentLine = line.split(",")								#Split each line at the comma
			fileLines.append(currentLine)								#Add the split line to the list

		for i in fileLines:												#Search through the list for the passed fileName
			if(i[0] == fileName):										#if it was found
				i[1] = newLine											#Update the last line parsed
				fileFound = True										#set the flag to state the file was found
				break													#Break out of the for loop, the file was found
		readIn.close()													#Close the file for reading

	if(fileFound == False):												#If the file wasn't file, just append it to the end of the list
		fileLines.append([fileName,newLine])

	out = open(LAST_LINE_FILE, 'w')										#Open the file in overwrite mode
	for j in fileLines:
		output = str(j[0])+','+str(int(j[1]))+'\n'						#Output the contents of the last line parsed list
		out.write(output)


#*** findFilePos *************************************************************************
# A function that takes a file name and determines where the parser left off last time
# 
# Recieves the file name to look for
#
# Returns the line that it left off on, or 0 if the fileName didn't exist
#
# Uses the library os.path
#
#******************************************************************************************
def findFilePos(fileName):
	if(os.path.isfile(LAST_LINE_FILE)):									#If the file exists, grab the contents
		fileLines = []													#Will contain the current contents of the last line parsed file
		readIn = open(LAST_LINE_FILE)									#Open the last line parsed file to grab the contents
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


#*** parseConfigFile **********************************************************************
# A function parses the contents of a config file for last line parsed file, the file to parse,
# and the patten to parse the file with.
#
# Recieves the config file name
#
# Uses the global variables LAST_LINE_FILE, FILE_NAME, and pat
#
# Uses the library os.path and re
#
#******************************************************************************************
def parseConfigFile(configFileLoc):
	global LAST_LINE_FILE												#The glocal variables for the config file
	global FILE_NAME
	global PARSING_PATTERN
	global FN
	global FIELDS
	global MODE
	global HOST
	global PORT
	global DATABASE
	global MEASUREMENT
	configPattern = 'Last line parsed file: (.*)\nFile to parse: (.*)\nPattern: (.*)\nFieldNames: (.*)\nHost: (.*)\nPort: (.*)\nDatabase: (.*)\nMeasurement: (.*)(\ntimestamp pattern: (.*))?'
	#Pattern for parsing the config file
	if(os.path.isfile(configFileLoc)):									#If the file exists, parse the config file
		configFile = open(configFileLoc)								#Open the config file
		configs = re.findall(configPattern,configFile.read(),re.MULTILINE)#Parse the config file for the configs
		LAST_LINE_FILE = configs[0][0]									#The parsed file is saved in the list of list called configs 
		FILE_NAME = configs[0][1]
		PARSING_PATTERN = configs[0][2]
		FN = configs[0][3]												#The list of field names separated by commas
		FIELDS = FN.split(',')											#Make it into a list of fields followed by their type
		n = 0
		while(n < len(FIELDS)):
			FIELDS[n] = FIELDS[n].split(':')							#Split each field name and type into a list containing the name and type
			n += 1
		HOST = configs[0][4]
		PORT = configs[0][5]
		DATABASE = configs[0][6]
		MEASUREMENT = configs[0][7]
		if(configs[0][8] != ""):										#If the user included the time stamp pattern thats saved as well
			global TIMESTAMP_PATTERN
			TIMESTAMP_PATTERN = configs[0][9]
	else:																#If the config file doesn't exist error out
		print("Error, can not find configuration file.")
		exit()

#*** formatOutput *************************************************************************
# A function that formats parsed logs into a list of dictionaries 
#
# The function receives a list of lists containing the parsedLogs
#
# The function returns a list of dictionaries, each containing the measurement and a dictionary of fields
#******************************************************************************************
def formatOutput(parsedLogs, path):
	formattedLogs = []
	for logs in parsedLogs:												#For each log in the list
		log = {}														#Create a dictionary for the log
		log.update({"measurement":MEASUREMENT})							#Add the measurement to the dictionary
		fields = {}														#Create a dictionary for the fields
		tags = {}
		n = 0															#Counter
		while(n < len(logs)):											#For each capture in the log
			if(FIELDS[n][1] == "tag"):
				tags.update({FIELDS[n][0]:logs[n]})						#Add the tag name and the value to the tag dictionary
			elif(FIELDS[n][1] == "int"):
				tags.update({FIELDS[n][0]:str(logs[n]+'i')})			#Add the field name and the value to the field dictionary, append an i at the end to make it an int
			elif(FIELDS[n][1] == "float"):
				tags.update({FIELDS[n][0]:float(logs[n])})				#Add the field name and the value to the dictionary, type cast it as a float to make it a float
			elif(FIELDS[n][1] == "timestamp"):
				timestamp = datetime.strptime(logs[n], TIMESTAMP_PATTERN)#Convert the string to a timestamp based on the timestamp pattern given
				log.update({"time":timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")})#Add the timestamp to the log dictionary
			elif(FIELDS[n][1] != "drop"):
				fields.update({FIELDS[n][0]:logs[n]})					#Add the field name and the value to the dictionary
			n += 1
		tags.update({"path":path})										#Add the tag name and the value to the tag dictionary
		log.update({"fields":fields})									#Add the field dictionary to the log dictionary
		log.update({"tags":tags})										#Add the field dictionary to the log dictionary
		formattedLogs.append(log)										#Add the log dictionary to the list
	return formattedLogs


#*** influxDBOutput ***********************************************************************
# A function that output the parsed logs to an influxDB database
#
# The function receives a list of dictionaries with the formatted parsed logs
#
# Uses the influxdb library
#******************************************************************************************
def influxDBOutput(formattedLogs):
	client = InfluxDBClient(host=HOST, port=PORT)						#Connect to the influxdb database located at the location provided by the config file
	client.create_database(DATABASE)									#Create the database, if it already exists nothing happens
	client.switch_database(DATABASE)									#Switch to the database
	client.write_points(formattedLogs,batch_size=1)						#Write the dictionaries one at a time to the database


print("starting...")
currentDT = datetime.now()
print(str(currentDT))
main()
print("Done.")
currentDT = datetime.now()
print(str(currentDT))
