#*** LabLogParser *************************************************************************
# Created by: Luke Gentle, Mark Elser, Arthur Eschenlauer, Adrian Hegeman, and Jerry Cohen
#
# Made on: 8/6/2019
# 
# Last Updated on: 8/13/2019
#
# A Program to parse logs and uploads the results to a influxdb database.
#
# Uses the re, os, sys, configparser, datetime, socket, and influxdb libraries
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
#Used to get all the files in a directory
from os import listdir
#Used to check if a file exists
from os.path import isfile, join
#Library used to include the host name
import socket
#Used to parse configuration files
from configparser import ConfigParser


#*** main *********************************************************************************
# The function calls functions to parse files
# 
# The function calls the function to parse the configuration file for each config file passed
# as an argument.  It then calls fileSelector.
#
# Uses the os.path and sys libraries
#
#******************************************************************************************
def main():
	if(len(sys.argv) == 1):												#If the doesn't provide an argument use a configFile in the same directory
		configs = parseConfigFile(os.path.join(os.path.dirname(__file__), "configFile"))
		fileSelector(configs)
	else:																#Parse the file provided.
		n = 1
		while(n < len(sys.argv)):										#For each config file passed
			configs = parseConfigFile(sys.argv[n])								#Parse the config file
			fileSelector(configs)												#Run the parser based on the config file's settings
			n += 1


#*** fileSelector *************************************************************************
# The program selects a file to parse and then calls functions to parse them, format them, and output them
# 
# The function calls the function to parse the configuration file and then calls the function
# to output the result to influxdb with the results of the formatOutput function which is called
# pattern to parse the file to parse and the last line parsed from the line file.
#
# Receives a list of the configs
#
# Uses the os.path, and listdir libraries
#
#******************************************************************************************
def fileSelector(configs):
	if(configs["Path"][len(configs["Path"])-1] == '/'):								#If the path is a folder instead of a file
		filesToParse = [f for f in listdir(configs["Path"]) if isfile(join(configs["Path"], f))]#Get all the files in the folder
		for files in filesToParse:										#For every file parse it
			if(files.endswith(configs["FileExtension"]) or configs["FileExtension"] == '*'):#Only parse if it's the specified file extension or the *, which is all extensions
				print(FILE_NAME,files," starting...", sep="")
				influxDBOutput(formatOutput(parseFile(configs["Pattern"], str(configs["Path"]+files), findFilePos(str(configs["Path"]+files),configs["LastLineFile"]),configs["LastLineFile"]),str(configs["Path"]+files), configs),configs)
				print(FILE_NAME,files," parsed.", sep="")
	else:
		influxDBOutput(formatOutput(parseFile(configs["Pattern"], configs["Path"], findFilePos(configs["Path"],configs["LastLineFile"]),configs["LastLineFile"]),configs["Path"], configs),configs)


#*** parseFile ***************************************************************************
# A function that parses a given file with a given pattern, staring at a given line
# 
# Receives a pattern to parse the file with, the name of the file to parse,
# the line to start parsing the file at, and the file containing the last line parsed of each file.
#
# Returns a list of lists containing the parsed logs and their individual fields
#
# Uses the library re
#
#******************************************************************************************
def parseFile(pattern, fileName, line, LastLineFile):
	dataFile = open(fileName, encoding="utf8", errors='ignore')
	parsedLogs = []														#Create a empty list to hold the parsed logs
	for i in range(line):												#Ignore the first (line) lines of the file
		next(dataFile, None)
	parsedLogs = [m.groupdict() for m in re.finditer(pattern,dataFile.read(),re.UNICODE | re.MULTILINE)]
	filePosUpdate(fileName, file_len(fileName), LastLineFile)							#call a function that will adjust the line on the current file.
	dataFile.close()
	return parsedLogs

#*** file_len ****************************************************************************
# A function that calculates the length of a file
# 
# Receives a file name
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
# Receives the file name the entry that needs to be updated, the last line parsed,
# and LastlineFile which is the file where last line parsed is recorded.
#
# Uses the library os.path
#
#******************************************************************************************
def filePosUpdate(fileName, newLine, LastLineFile):
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

	if(fileFound == False):												#If the file wasn't file, just append it to the end of the list
		fileLines.append([fileName,newLine])

	out = open(LastLineFile, 'w')										#Open the file in overwrite mode
	for j in fileLines:
		output = str(j[0])+','+str(int(j[1]))+'\n'						#Output the contents of the last line parsed list
		out.write(output)


#*** findFilePos *************************************************************************
# A function that takes a file name and determines where the parser left off last time
# 
# Receives the file name to look for and the LastLineFile
#
# Returns the line that it left off on, or 0 if the fileName didn't exist
#
# Uses the library os.path
#
#******************************************************************************************
def findFilePos(fileName, LastLineFile):
	if(os.path.isfile(LastLineFile)):									#If the file exists, grab the contents
		fileLines = []													#Will contain the current contents of the last line parsed file
		readIn = open(LastLineFile)									#Open the last line parsed file to grab the contents
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
# and the pattern to parse the file with.
#
# Receives the config file name
#
# Returns the list of the configs
#
# Uses the library os.path and ConfigParser
#
#******************************************************************************************
def parseConfigFile(configFileLoc):
	if(os.path.isfile(configFileLoc)):									#If the file exists, parse the config file
		config = ConfigParser()											#The variable to hold the results of parsing the config file
		config.read(configFileLoc)										#Parse the config file
		configurations = {}												#All configurations are going to a list to be returned

		configurations["LastLineFile"] = config.get('FILES','LastLineFile')#Get the last line file location
		configurations["Path"] = config.get('FILES','Path')				#Get the file path to parse
		if(config.has_option('FILES', 'FileExtension')):				#If the user specified a file extension
			configurations["FileExtension"] = config.get('FILES','FileExtension')#Set the file extension
		configurations["Pattern"] = config.get('PARSER','Pattern')		#Get the parsing pattern
		fn = config.get('PARSER','FieldNames')							#In the configuration file datatype is stored in a comma separated list
		field = fn.split(',')											#Make it into a list of fields followed by their type
		
		n = 0
		while(n < len(field)):
			field[n] = field[n].split(':')								#Split each field name and type into a list containing the name and type
			n += 1
		configurations["Fields"] = field								#Add the results to the configurations list
		configurations["Host"] = config.get('INFLUXDB','Host')
		configurations["Port"] = config.get('INFLUXDB','Port')
		configurations["Database"] = config.get('INFLUXDB','Database')
		configurations["Measurement"] = config.get('INFLUXDB','Measurement')
		if(config.has_option('PARSER', 'TimestampPattern')):			#If a timestamp pattern is given
			configurations["TimestampPattern"] = config.get('PARSER', 'TimestampPattern')#Set the timestamp pattern
		return configurations
	else:																#If the config file doesn't exist error out
		print("Error, can not find configuration file.")
		exit()

#*** formatOutput *************************************************************************
# A function that formats parsed logs into a list of dictionaries 
#
# The function receives a list of lists containing the parsedLogs, the file the logs were parsed from
# and the list of configs
#
# The function returns a list of dictionaries, each containing the measurement and a dictionary of fields
#
# Uses the library socket and datetime
#******************************************************************************************
def formatOutput(parsedLogs, path, configs):
	formattedLogs = []
	for logs in parsedLogs:												#For each log in the list
		log = {}														#Create a dictionary for the log
		log.update({"measurement":configs["Measurement"]})				#Add the measurement to the dictionary
		timestampExists = False											#Keep track if a timestamp was added
		fields = {}														#Create a dictionary for the fields
		tags = {}
		for key in logs.keys():
			dataType = dataTyper(key,configs["Fields"])
			if(dataType == "tag"):
				tags.update({key:logs[key]})							#Add the tag name and the value to the tag dictionary
			elif(dataType == "int"):
				tags.update({key:str(logs[key]+'i')})					#Add the field name and the value to the field dictionary, append an i at the end to make it an int
			elif(dataType == "float"):
				tags.update({key:float(logs[key])})						#Add the field name and the value to the dictionary, type cast it as a float to make it a float
			elif(dataType == "timestamp"):
				timestamp = datetime.strptime(logs[key], configs["TimestampPattern"])#Convert the string to a timestamp based on the timestamp pattern given
				log.update({"time":timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})#Add the timestamp to the log dictionary
				timestampExists = True									#Keep track if a timestamp was added
			elif(dataType != "drop"):
				fields.update({key:logs[key]})							#Add the field name and the value to the dictionary
		if(timestampExists == False):									#InfluxDB's write_point function doesn't work properly when writing points that don't have timestamps in batches
			currentDT = datetime.now()									#To work around this, I'm adding the current time as the timestamp, which is what influx would do anyway
			log.update({"time":currentDT.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})#Has to be microseconds since this is done so quickly otherwise all logs would have the exact same time
		tags.update({"path":path})										#Add the path to the tag dictionary
		tags.update({"host":socket.gethostname()})						#Add the host to the tag dictionary
		log.update({"fields":fields})									#Add the field dictionary to the log dictionary
		log.update({"tags":tags})										#Add the tags dictionary to the log dictionary
		formattedLogs.append(log)										#Add the log dictionary to the list
	return formattedLogs


#*** dataTyper ****************************************************************************
# A function that receives a key and determines what data type it is 
#
# The function that receives a key and the list of fields which includes their data types
#
# The function returns a string containing the data type
#
#******************************************************************************************
def dataTyper(key,fields):
	for field in fields:
		if(field[0] == key):
			return field[1]
	return "null"


#*** influxDBOutput ***********************************************************************
# A function that output the parsed logs to an influxDB database
#
# The function receives a list of dictionaries with the formatted parsed logs and the list of configs
#
# Uses the influxdb library
#******************************************************************************************
def influxDBOutput(formattedLogs,configs):
	client = InfluxDBClient(host=configs["Host"], port=configs["Port"])			#Connect to the influxdb database located at the location provided by the config file
	client.create_database(configs["Database"])									#Create the database, if it already exists nothing happens
	client.switch_database(configs["Database"])									#Switch to the database
	client.write_points(formattedLogs,batch_size=5000, time_precision="u")		#Write the dictionaries one at a time to the database


print("starting...")
currentDT = datetime.now()
print(str(currentDT))
main()
print("Done.")
currentDT = datetime.now()
print(str(currentDT))
