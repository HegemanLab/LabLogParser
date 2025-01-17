#Used for converting string to timestamp
from datetime import datetime
#Used for determining if DLS is on or off
import pytz
#Library used to include the host name
import socket
#The regular expression library used for the parser
import re

from datetime import timedelta

def formatOutput(parsedLogs, path, configs):
	"""
	A function that formats parsed logs into a list of dictionaries 
	
	The function makes a dictionary that InfluxDB can accept as a point.
	It goes through the list of keys for each parsedLog and adds to the dictionary
	for its datatype.  When all keys are assigned to the correct dictionaries all dictionaries
	are added to one dictionary which is appended a list.

	Parameters:
	parsedLogs (list): A list of dictionaries containing the parsedLogs
	path (String): The file the logs were parsed from
	configs (dictionary): The dictionary of configs

	Returns:
	List: A list of dictionaries, each containing the measurement and a dictionary of fields

	Libraries:
	Uses the library socket, pytz, and datetime
	"""
	formattedLogs = []
	filenameparsed = []
	if("FilenamePattern" in configs.keys()):							#If a pattern is defined to parse the file name
		try:
			filenameparsed = [m.groupdict() for m in re.finditer(configs["FilenamePattern"],path[path.rindex('/')+1:])]
			configs["Fields"] += configs["FileNameFields"]					#Add the datatype of the fields from the filename to the list

		except:
			filenameparsed = [m.groupdict() for m in re.finditer(configs["FilenamePattern"],path[path.rindex('\\')+1:])]
			configs["Fields"] += configs["FileNameFields"]					#Add the datatype of the fields from the filename to the list
	
	for logs in parsedLogs:												#For each log in the list
		log = {}														#Create a dictionary for the log
		log.update({"measurement":configs["Measurement"]})				#Add the measurement to the dictionary
		if(filenameparsed != []):										#Check if there's filename fields
			logs = Merge(filenameparsed[0],logs)						#If there is, add the filename fields to every log

		timestampExists = False											#Keep track if a timestamp was added
		fields = {}														#Create a dictionary for the fields
		tags = {}
		for key in logs.keys():
			dataType = dataTyper(key,configs["Fields"])					#Get the data type of the key
			if(dataType.lower() == "tag"):
				tags.update({key:logs[key]})							#Add the tag name and the value to the tag dictionary
				if(configs["TagAsField"] == "1"):
					fields.update({key:logs[key]})						#Add the field name and the value to the dictionary
			elif(dataType.lower() == "int" or dataType.lower() == "integer"):
				fields.update({key:int(logs[key])})						#Add the field name and the value to the field dictionary, append an i at the end to make it an int
			elif(dataType.lower() == "float"):
				fields.update({key:float(logs[key])})					#Add the field name and the value to the field dictionary, append an i at the end to make it an int
			elif(dataType.lower() == "date"):
				if(timestampExists == False):							#Check if a timestamp has already been added.
					for keyT in logs.keys():
						dT = dataTyper(keyT,configs["Fields"])			#Search through the field names for a time field
						if(dT == "time"):	
							timestampExists = True						#Once time is found construct a timestamp from time and date
							timestamp = logs[key] + logs[keyT]
							timestamp = datetime.strptime(timestamp, configs["TimestampPattern"])#Convert the string to a timestamp based on the timestamp pattern given
							timestamp = timestamp + timedelta(hours=int(datetime.now(pytz.timezone(configs["Timezone"])).strftime('%z'))/100)
							log.update({"time":timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})#Add the timestamp to the log dictionary
							timestampExists = True						#Keep track if a timestamp was added
				if(timestampExists == False):
					fields.update({key:logs[key]})						#If it's just a date with no time, just add date as a field
			elif(dataType.lower() == "time"):
				if(timestampExists == False):							#Check if a timestamp has already been added.
					for keyD in logs.keys():
						dT = dataTyper(keyD,configs["Fields"])			#Search for the date field		
						if(dT == "date"):
							timestampExists = True						#If the date is found construct a timestamp with time and date
							timestamp = logs[keyD] + logs[key]
							timestamp = datetime.strptime(timestamp, configs["TimestampPattern"])#Convert the string to a timestamp based on the timestamp pattern given
							timestamp = timestamp + timedelta(hours=int(datetime.now(pytz.timezone(configs["Timezone"])).strftime('%z'))/100)
							log.update({"time":timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})#Add the timestamp to the log dictionary
							timestampExists = True						#Keep track if a timestamp was added
				if(timestampExists == False):
					fields.update({key:logs[key]})						#Add the field name and the value to the dictionary
			elif(dataType.lower() == "timestamp"):
				timestamp = datetime.strptime(logs[key], configs["TimestampPattern"])#Convert the string to a timestamp based on the timestamp pattern given
				timestamp = timestamp + timedelta(hours=int(datetime.now(pytz.timezone(configs["Timezone"])).strftime('%z'))/100)
				log.update({"time":timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})#Add the timestamp to the log dictionary
				timestampExists = True									#Keep track if a timestamp was added
			elif(dataType.lower() != "drop"):
				if(logs[key]!=''):
					fields.update({key:logs[key]})							#Add the field name and the value to the dictionary
				else:
					fields.update({key:"null"})
		if(timestampExists == False):									#InfluxDB's write_point function doesn't work properly when writing points that don't have timestamps in batches
			currentDT = datetime.utcnow()								#To work around this, I'm adding the current time as the timestamp, which is what influx would do anyway
			
			log.update({"time":currentDT.strftime("%Y-%m-%dT%H:%M:%S.%fZ")})#Has to be microseconds since this is done so quickly otherwise all logs would have the exact same time
		tags.update({"path":path})										#Add the path to the tag dictionary
		tags.update({"host":socket.gethostname()})						#Add the host to the tag dictionary
		log.update({"fields":fields})									#Add the field dictionary to the log dictiona
		log.update({"tags":tags})										#Add the tags dictionary to the log dictionary
		formattedLogs.append(log)										#Add the log dictionary to the list
	return formattedLogs


def Merge(dict1, dict2): 
	"""
	A function that recieves two dictionaries and merges the two
	
	The function combines two dictionaries
	
	Parameters:
	dict1 (dictionary): Dictionary 1
	fields (dictionary): Dictionary 1
	
	Returns:
	res: A dictionary containing the contents of dict1 and dict2
	
	Source: https://www.geeksforgeeks.org/python-merging-two-dictionaries/
	"""
	res = {**dict1, **dict2} 
	return res 


def dataTyper(key,fields):
	"""
	A function that receives a key and determines what data type it is 
	
	The function iterates through a list of fields and searches for the entry
	for the passed key.  When found it returns the datatype for that field. 
	If it doesn't exist it returns "null"
	
	Parameters:
	key (String): A key 
	fields (list): A list of lists which includes a key and its data type
	
	Returns:
	string: A string containing the data type
	
	"""
	for field in fields:
		if(field[0].strip() == key.strip()):
			return field[1]
	return "null"
