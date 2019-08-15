#Used for converting string to timestamp
from datetime import datetime
#Library used to include the host name
import socket



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
	Uses the library socket and datetime
	"""
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
		if(field[0] == key):
			return field[1]
	return "null"
