#The functions for opening files and reading configs files
import MSLP.read
#The library used for determining if a file exists
import os.path
#Library for passing arguments with python script
import sys
import time
def main():
	"""
	The function calls functions to parse files
	
	The function calls the function to parse the configuration file for each config file passed
	as an argument.  It then calls fileSelector.

	Parameters:
	Zero or more file paths can be passed when calling the python function that define configuration
	files to be run

	Libraries:
	Uses the os.path and sys libraries
	
	"""
	print((time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) / 60 / 60 * -1)
	if(len(sys.argv) == 1):												#If the doesn't provide an argument use a configFile in the same directory
		configs = MSLP.read.parseConfigFile(os.path.join(os.path.dirname(__file__), "configFile"))
		MSLP.read.fileSelector(configs)
	else:																#Parse the file provided.
		n = 1
		while(n < len(sys.argv)):										#For each config file passed
			configs = MSLP.read.parseConfigFile(sys.argv[n])				#Parse the config file
			MSLP.read.fileSelector(configs)								#Run the parser based on the config file's settings
			n += 1


if __name__ == "__main__":
	main()
