#The library used for determining if a file exists
import os.path
#Used to check if a file exists
from os.path import isfile, join
#Used to parse configuration files
from configparser import ConfigParser
#Used to get all the files in a directory
from os import listdir
#The functions for writing to the influxDB database
import LLP.write
#The functions for formatting output for writing
import LLP.format
#The functions for parsing files
import LLP.parse
#The functions to update and retrieve last line parsed from a file
import LLP.filepos


def fileSelector(configs):
	"""
	The program selects a file to parse and then calls functions to parse them, format them, and output them
	
	The function calls the function to parse the configuration file and then calls the function
	to output the result to influxdb with the results of the formatOutput function which is called
	pattern to parse the file to parse and the last line parsed from the line file.
	
	Parameters:
	configs (dictionary): A dictionary of configurations
	
	Libraries:
	Uses the os.path, listdir libraries, LLP.write, LLP.format, LLP.parse, LLP.filepos
	
	"""
	if(configs["Path"][len(configs["Path"])-1] == '/'):					#If the path is a folder instead of a file
		filesToParse = [f for f in listdir(configs["Path"]) if isfile(join(configs["Path"], f))]#Get all the files in the folder
		for files in filesToParse:										#For every file parse it
			if(files.endswith(configs["FileExtension"]) or configs["FileExtension"] == '*'):#Only parse if it's the specified file extension or the *, which is all extensions
				print(str(configs["Path"]+files),files," starting...", sep="")
				LLP.write.influxDBOutput(LLP.format.formatOutput(LLP.parse.parseFile(configs["Pattern"], str(configs["Path"]+files), LLP.filepos.findFilePos(str(configs["Path"]+files),configs["LastLineFile"]),configs["LastLineFile"]),str(configs["Path"]+files), configs),configs)
				print(str(configs["Path"]+files),files," parsed.", sep="")
	else:
		print(str(configs["Path"]),"starting...")
		LLP.write.influxDBOutput(LLP.format.formatOutput(LLP.parse.parseFile(configs["Pattern"], configs["Path"], LLP.filepos.findFilePos(configs["Path"],configs["LastLineFile"]),configs["LastLineFile"]),configs["Path"], configs),configs)
		print(str(configs["Path"]),"parsed.")


def parseConfigFile(configFileLoc):
	"""
	A function parses the contents of a config file for last line parsed file, the file to parse,
	and the pattern to parse the file with.
	
	Parameters:
	configFileLoc (String): Receives the config file name
	
	Returns:
	configurations (dictionary): the dictionary of the configs

	Libraries:
	Uses the library os.path and ConfigParser
	
	"""
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
