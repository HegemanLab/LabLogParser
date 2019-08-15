#Library for sending parsed logs to influxdb
from influxdb import InfluxDBClient


def influxDBOutput(formattedLogs,configs):
	"""
	A function that output the parsed logs to an influxDB database
	
	The function connects to the influxdb database specified by the configs dictionary and
	writes the list of dictionaries to that database.
	
	Parameters:
	formattedLogs (list): A list of dictionaries with the formatted parsed logs
	configs (dictionary): A dictionary of configs
	
	Libraries:
	Uses the influxdb library
	"""
	client = InfluxDBClient(host=configs["Host"], port=configs["Port"])	#Connect to the influxdb database located at the location provided by the config file
	client.create_database(configs["Database"])							#Create the database, if it already exists nothing happens
	client.switch_database(configs["Database"])							#Switch to the database
	client.write_points(formattedLogs,batch_size=5000, time_precision="u")#Write the dictionaries one at a time to the database


